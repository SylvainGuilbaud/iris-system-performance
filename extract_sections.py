import dateutil.parser
from dateutil.relativedelta import *

import pandas as pd
from yaspe_utilities import get_number_type, make_mdy_date, check_date, get_aix_wacky_numbers


def extract_sections(
    operating_system, profile_run, input_file, include_iostat, include_nfsiostat, html_filename, disk_list
):

    once = True

    vmstat_processing = False
    vmstat_header = ""
    vmstat_rows_list = []
    vmstat_date = ""
    vmstat_date_convert = False
    aix_vmstat_line_date = ""
    previous_time = "00:00:00"

    iostat_processing = False
    iostat_header = ""
    iostat_rows_list = []
    iostat_device_block_processing = False
    iostat_am_pm = False
    iostat_date_included = False
    iostat_date = ""
    iostat_date_convert = False

    mgstat_processing = False
    mgstat_header = ""
    mgstat_rows_list = []
    mgstat_date = ""
    mgstat_date_convert = False

    perfmon_processing = False
    perfmon_header = ""
    perfmon_rows_list = []

    nfsiostat_processing = False
    nfsiostat_header = ""
    nfsiostat_rows_list = []
    nfsiostat_read = False
    nfsiostat_write = False

    aix_sar_d_processing = False
    aix_sar_d_header = ""
    aix_sar_d_rows_list = []
    aix_sar_d_date = ""
    aix_sar_d_date_convert = False
    aix_sar_d_line_date = ""
    aix_sar_d_previous_time = "00:00:00"

    run_start = profile_run.split("on ")[1]
    run_start = run_start[:-1]
    run_start_date = dateutil.parser.parse(run_start)

    with open(input_file, "r", encoding="ISO-8859-1") as file:

        for line in file:
            if "<!-- beg_mgstat -->" in line:
                mgstat_processing = True
            if "<!-- end_mgstat -->" in line:
                mgstat_processing = False
            if mgstat_processing and mgstat_header != "":
                if line.strip() != "":
                    mgstat_row_dict = {}
                    values = line.split(",")
                    values = [i.strip() for i in values]  # strip off carriage return etc
                    # Convert integers or real from strings if possible
                    values_converted = [get_number_type(v) for v in values]
                    # create a dictionary of this row and append to a list of row dictionaries for later add to table
                    mgstat_row_dict = dict(zip(mgstat_columns, values_converted))
                    # Add the file name
                    mgstat_row_dict["html name"] = html_filename

                    # Check date format
                    if not mgstat_date_convert and mgstat_row_dict["Date"] != mgstat_date:
                        mgstat_date = mgstat_row_dict["Date"]
                        mgstat_date_convert = check_date("mgstat", run_start_date, mgstat_row_dict["Date"])

                    if mgstat_date_convert:
                        new_date = make_mdy_date(mgstat_row_dict["Date"])
                        new_date_dict = {"Date": new_date}
                        mgstat_row_dict.update(new_date_dict)

                    if operating_system == "AIX":
                        if aix_vmstat_line_date == "":
                            aix_vmstat_line_date = mgstat_row_dict["Date"]
                            aix_sar_d_line_date = mgstat_row_dict["Date"]

                    # Added for pretty processing
                    mgstat_row_dict["datetime"] = f'{mgstat_row_dict["Date"]} {mgstat_row_dict["Time"]}'
                    mgstat_rows_list.append(mgstat_row_dict)
            if mgstat_processing and "Glorefs" in line:
                mgstat_header = line
                mgstat_columns = mgstat_header.split(",")
                mgstat_columns = [i.strip() for i in mgstat_columns]  # strip off carriage return etc

            if operating_system == "Linux" or operating_system == "Ubuntu":
                if "<!-- beg_vmstat -->" in line:
                    vmstat_processing = True
                if "<!-- end_vmstat -->" in line:
                    vmstat_processing = False
                if vmstat_processing and vmstat_header != "":
                    if line.strip() != "":
                        vmstat_row_dict = {}
                        values = line.split()
                        values = [i.strip() for i in values]  # strip off carriage return etc
                        values_converted = [get_number_type(v) for v in values]
                        vmstat_row_dict = dict(zip(vmstat_columns, values_converted))
                        vmstat_row_dict["html name"] = html_filename

                        # Check date format
                        if not vmstat_date_convert and vmstat_row_dict["Date"] != vmstat_date:
                            vmstat_date = vmstat_row_dict["Date"]
                            vmstat_date_convert = check_date("vmstat", run_start_date, vmstat_row_dict["Date"])

                        if vmstat_date_convert:
                            new_date = make_mdy_date(vmstat_row_dict["Date"])
                            new_date_dict = {"Date": new_date}
                            vmstat_row_dict.update(new_date_dict)

                        # Added for pretty processing
                        vmstat_row_dict["datetime"] = f'{vmstat_row_dict["Date"]} {vmstat_row_dict["Time"]}'
                        vmstat_rows_list.append(vmstat_row_dict)
                if vmstat_processing and "us sy id wa" in line:
                    # vmstat !sometimes! has column names on same line as html
                    if "<pre>" in line:
                        vmstat_header = line.split("<pre>")[1].strip()
                    else:
                        vmstat_header = line
                    vmstat_header = vmstat_header.split(" r ")[1]
                    vmstat_header = f"Date Time r {vmstat_header}"
                    vmstat_columns = vmstat_header.split()
                    vmstat_columns = [i.strip() for i in vmstat_columns]  # strip off carriage return etc

            if operating_system == "AIX":
                if "<!-- beg_vmstat -->" in line:
                    vmstat_processing = True
                if "<!-- end_vmstat -->" in line:
                    vmstat_processing = False
                if vmstat_processing and vmstat_header != "":
                    if line.strip() != "":
                        vmstat_row_dict = {}
                        values = line.split()
                        values = [i.strip() for i in values]  # strip off carriage return etc

                        # AIX insert date and time in first two columns, Time is the last column
                        this_time = values[-1]
                        values.insert(0, this_time)

                        # Have no date, only time. Make sure we haven't rolled over midnight
                        # Comparing time as strings is a bit hacky, but we only care about the hour
                        if this_time < previous_time:
                            next_day = dateutil.parser.parse(aix_vmstat_line_date) + relativedelta(days=+1)
                            aix_vmstat_line_date = next_day.strftime("%m/%d/%Y")
                        previous_time = this_time
                        values.insert(0, aix_vmstat_line_date)

                        values_converted = [get_number_type(v) for v in values]
                        vmstat_row_dict = dict(zip(vmstat_columns, values_converted))
                        vmstat_row_dict["html name"] = html_filename

                        # Check date format
                        if not vmstat_date_convert and vmstat_row_dict["Date"] != vmstat_date:
                            vmstat_date = vmstat_row_dict["Date"]
                            vmstat_date_convert = check_date("aix_vmstat", run_start_date, vmstat_row_dict["Date"])

                        if vmstat_date_convert:
                            new_date = make_mdy_date(vmstat_row_dict["Date"])
                            new_date_dict = {"Date": new_date}
                            vmstat_row_dict.update(new_date_dict)

                        # Added for pretty processing
                        vmstat_row_dict["datetime"] = f'{vmstat_row_dict["Date"]} {vmstat_row_dict["Time"]}'
                        vmstat_rows_list.append(vmstat_row_dict)

                if vmstat_processing and "us sy id wa" in line:
                    # vmstat !sometimes! has column names on same line as html
                    if "<pre>" in line:
                        vmstat_header = line.split("<pre>")[1].strip()
                    else:
                        vmstat_header = line

                    vmstat_header = vmstat_header.split("r ", 1)[1]
                    vmstat_header = f"Date Time r {vmstat_header}"
                    vmstat_columns = vmstat_header.split()
                    vmstat_columns = [i.strip() for i in vmstat_columns]  # strip off carriage return etc

                    # Duplicate column names in AIX
                    for i in range(len(vmstat_columns)):
                        if vmstat_columns[i] == "sy":
                            vmstat_columns[i] = "sy_calls"
                            break

                if "<div id=sar-d>" in line:
                    aix_sar_d_processing = True
                if "</pre><p align=" in line and "<div id=sar-d>" not in line:
                    aix_sar_d_processing = False
                if aix_sar_d_processing and aix_sar_d_header != "":
                    if line.strip() != "":
                        aix_sar_d_row_dict = {}
                        values = line.split()
                        values = [i.strip() for i in values]  # strip off carriage return etc

                        # AIX insert date and time in first two columns, Time is the first column
                        # except when it is missing.
                        if "disk" in values[0]:
                            values.insert(0, aix_sar_d_previous_time)
                        else:
                            this_time = values[0]

                        # Have no date, only time. Make sure we haven't rolled over midnight
                        # Comparing time as strings is a bit hacky, but we only care about the hour
                        if this_time < aix_sar_d_previous_time:
                            next_day = dateutil.parser.parse(aix_sar_d_line_date) + relativedelta(days=+1)
                            aix_sar_d_line_date = next_day.strftime("%m/%d/%Y")
                        aix_sar_d_previous_time = this_time
                        values.insert(0, aix_sar_d_line_date)

                        values_converted = [get_number_type(v) for v in values]
                        aix_sar_d_row_dict = dict(zip(aix_sar_d_columns, values_converted))
                        aix_sar_d_row_dict["html name"] = html_filename

                        # Check date format
                        if not aix_sar_d_date_convert and aix_sar_d_row_dict["Date"] != aix_sar_d_date:
                            aix_sar_d_date = aix_sar_d_row_dict["Date"]
                            aix_sar_d_date_convert = check_date("aix_sar_d", run_start_date, aix_sar_d_row_dict["Date"])

                        if aix_sar_d_date_convert:
                            new_date = make_mdy_date(aix_sar_d_row_dict["Date"])
                            new_date_dict = {"Date": new_date}
                            aix_sar_d_row_dict.update(new_date_dict)

                        # Added for pretty processing
                        aix_sar_d_row_dict["datetime"] = f'{aix_sar_d_row_dict["Date"]} {aix_sar_d_row_dict["Time"]}'
                        aix_sar_d_rows_list.append(aix_sar_d_row_dict)

                if aix_sar_d_processing and "device" in line:
                    # sar d time on the same row as column names
                    aix_sar_d_header = line

                    aix_sar_d_header = aix_sar_d_header.split("device ", 1)[1]
                    aix_sar_d_header = f"Date Time device {aix_sar_d_header}"
                    aix_sar_d_columns = aix_sar_d_header.split()
                    aix_sar_d_columns = [i.strip() for i in aix_sar_d_columns]  # strip off carriage return etc

            if operating_system == "Windows":
                if "id=perfmon" in line:
                    perfmon_processing = True
                if "<!-- end_win_perfmon -->" in line:
                    perfmon_processing = False
                if perfmon_processing and perfmon_header != "":
                    if line.strip() != "":
                        perfmon_row_dict = {}
                        values = line.split(",")
                        values = [i.strip() for i in values]  # strip off carriage return etc
                        values = list(map(lambda x: x[1:-1].replace('"', ""), values))
                        values = list(map(lambda x: 0.0 if x == " " else x, values))
                        values_converted = [get_number_type(v) for v in values]
                        perfmon_row_dict = dict(zip(perfmon_columns, values_converted))
                        perfmon_row_dict["html name"] = html_filename

                        # The first column is a date time with timezone
                        # todo: move datetime column creation to here, include dd/mm/yy check

                        perfmon_rows_list.append(perfmon_row_dict)
                if perfmon_processing and "Memory" in line:
                    perfmon_header = line
                    # get rid of characters that screw with queries or charting
                    perfmon_header = [s for s in perfmon_header if s.isalnum() or s.isspace() or (s == ",")]
                    perfmon_header = "".join(perfmon_header)
                    perfmon_header = perfmon_header.replace(" ", "_")

                    perfmon_columns = perfmon_header.split(",")
                    perfmon_columns = [i.strip() for i in perfmon_columns]  # strip off carriage return etc

            # iostat has a lot of variations, start as needed
            if (operating_system == "Linux" or operating_system == "Ubuntu") and include_iostat:

                if iostat_processing and "<div" in line:  # iostat does not flag end
                    iostat_processing = False
                else:
                    # Found iostat
                    if "id=iostat" in line:
                        iostat_processing = True
                    # Is there a date and time line (not in some cases)
                    if iostat_processing and len(line.split()) == 2:
                        # If a date is found then device block ended
                        iostat_device_block_processing = False
                        iostat_date_included = True
                        date_time = line.strip()
                    if iostat_processing and len(line.split()) == 3:  # date time AM
                        iostat_am_pm = True
                        # If a date is found then device block ended
                        iostat_device_block_processing = False
                        iostat_date_included = True
                        date_time = line.strip()
                    # If there is no date then this is the next likely header, device block ended
                    if "avg-cpu" in line:
                        iostat_device_block_processing = False
                    # Add devices to database
                    if iostat_processing and iostat_device_block_processing and iostat_header != "":
                        if line.strip() != "":
                            print_line = False
                            if disk_list:
                                for item in disk_list:
                                    if item in line:
                                        print_line = True
                            else:
                                print_line = True
                            if print_line:
                                iostat_row_dict = {}
                                # if European "," for ".", do that first
                                line = line.replace(",", ".")
                                # get rid of multiple whitespaces, then use comma separator so the AM/PM is preserved if its there
                                line = " ".join(line.split())
                                line = line.replace(" ", ",")
                                if iostat_date_included:
                                    if iostat_am_pm:
                                        line = (
                                            date_time.split()[0]
                                            + ","
                                            + date_time.split()[1]
                                            + " "
                                            + date_time.split()[2]
                                            + ","
                                            + line
                                        )
                                    else:
                                        line = date_time.split()[0] + "," + str(date_time.split()[1]) + "," + line
                                values = line.split(",")
                                values = [i.strip() for i in values]  # strip off carriage return etc
                                values_converted = [get_number_type(v) for v in values]
                                iostat_row_dict = dict(zip(iostat_columns, values_converted))
                                iostat_row_dict["html name"] = html_filename

                                # Check date format
                                if not iostat_date_convert and iostat_row_dict["Date"] != iostat_date:
                                    iostat_date = iostat_row_dict["Date"]
                                    iostat_date_convert = check_date("iostat", run_start_date, iostat_row_dict["Date"])

                                if iostat_date_convert:
                                    new_date = make_mdy_date(iostat_row_dict["Date"])
                                    new_date_dict = {"Date": new_date}
                                    iostat_row_dict.update(new_date_dict)

                                # Added for pretty processing
                                iostat_row_dict["datetime"] = f'{iostat_row_dict["Date"]} {iostat_row_dict["Time"]}'
                                iostat_rows_list.append(iostat_row_dict)
                    # Header line found, next line is start of device block
                    if "Device" in line:
                        iostat_device_block_processing = True
                    # First time in create column names
                    if iostat_processing and iostat_header == "" and "Device" in line:
                        if iostat_date_included:
                            iostat_header = f"Date Time {line}"
                        else:
                            iostat_header = f"{line}"
                        iostat_header = iostat_header.replace(":", "")  # "Device:" used later on logic
                        iostat_columns = iostat_header.split()
                        iostat_columns = [i.strip() for i in iostat_columns]  # strip off carriage return etc

            # nfsiostat
            if (operating_system == "Linux" or operating_system == "Ubuntu") and include_nfsiostat:

                if nfsiostat_processing and "pre>" in line:  # nfsiostat does not flag end
                    nfsiostat_processing = False
                else:
                    # Found nfsiostat
                    if "id=nfsiostat" in line:
                        nfsiostat_processing = True
                    # There is no date and time
                    if "mounted on" in line:
                        nfsiostat_host = line.split(":")[0]
                        nfsiostat_device = line.split()[0].split(":")[1]
                        nfsiostat_mount_point = line.split()[3].replace(":", "")
                        nfs_output_line = f"{nfsiostat_host},{nfsiostat_device},{nfsiostat_mount_point}"
                    if nfsiostat_read:
                        # Get rid of extra spaces
                        line = " ".join(line.split())
                        # make percentage (0.0%) a number
                        line = line.replace("(", "")
                        line = line.replace(")", "")
                        line = line.replace("%", "")
                        line = line.replace(" ", ",")
                        nfs_output_line += f",{line}"
                        nfsiostat_read = False
                    if nfsiostat_write:
                        # Get rid of extra spaces
                        line = " ".join(line.split())
                        # make percentage (0.0%) a number
                        line = line.replace("(", "")
                        line = line.replace(")", "")
                        line = line.replace("%", "")
                        line = line.replace(" ", ",")
                        nfs_output_line += f",{line}"
                        nfsiostat_write = False
                    if "read:" in line:
                        nfsiostat_read = True
                        nfsiostat_write = False
                        # First time in create column names
                        if nfsiostat_header == "":
                            # Hardcoded while debugging
                            nfsiostat_header = "Host,Device,Mounted on"
                            nfsiostat_header += (
                                f",read ops/s,read kB/s,read kB/op,read retrans,read retrans %,"
                                f"read avg RTT (ms),read avg exe (ms),read avg queue (ms),"
                                f"read errors,read errors %"
                            )
                            nfsiostat_header += (
                                f",write ops/s,write kB/s,write kB/op,write retrans,write retrans %,"
                                f"write avg RTT (ms),write avg exe (ms),write avg queue (ms),"
                                f"write errors,write errors %"
                            )
                            nfsiostat_header += f",html name"
                            nfsiostat_columns = nfsiostat_header.split(",")
                            mgstat_columns = [i.strip() for i in nfsiostat_columns]  # strip off carriage return etc
                    if "write:" in line:
                        nfsiostat_read = False
                        nfsiostat_write = True
                    if nfsiostat_processing and nfsiostat_header != "":
                        if nfs_output_line.strip() != "":
                            nfsiostat_row_dict = {}
                            values = nfs_output_line.split(",")
                            values = [i.strip() for i in values]  # strip off carriage return etc
                            values_converted = [get_number_type(v) for v in values]
                            nfsiostat_row_dict = dict(zip(nfsiostat_columns, values_converted))
                            nfsiostat_row_dict["html name"] = html_filename
                            nfsiostat_rows_list.append(nfsiostat_row_dict)

            # AIX iostat has variations, start as needed
            #
            #  ....<div id=iostat></div>iostat</font></b><br><pre>
            # System configuration: lcpu=80 drives=2 paths=4 vdisks=2
            # Disks:                      xfers                                read                                write                                  queue                    time
            #                   %tm    bps   tps  bread  bwrtn   rps    avg    min    max time fail   wps    avg    min    max time fail    avg    min    max   avg   avg  serv
            #                   act                                    serv   serv   serv outs              serv   serv   serv outs        time   time   time  wqsz  sqsz qfull
            # hdisk0            2.0  65.5K  13.0  57.3K   8.2K  11.0   0.6    1.5S   0.9     0    0   2.0   0.4    0.3    0.4     0    0   0.0    0.0    0.0    0.0   0.0   3.0  12:41:43
            # hdisk1            7.0   4.2M 135.0  57.3K   4.2M   7.0   6.9    0.5   20.2     0    0 128.0   0.4    0.3    0.6     0    0   0.0    0.0    0.1    0.0   0.0   4.0  12:41:43

            # Fake header columns
            aix_iostat_columns = [
                "Device",
                "xfer tm act",
                "xfer bps",
                "xfer tps",
                "xfer bread",
                "xfer bwrtn",
                "read rps",
                "read avg serv",
                "read min serv",
                "read max serv",
                "read time outs",
                "read fail",
                "write wps",
                "write avg serv",
                "write min serv",
                "write max serv",
                "write time outs",
                "write fail",
                "queue avg time",
                "queue min time",
                "queue max time",
                "queue avg wqsz",
                "queue avg sqsz",
                "queue serv qfull",
                "Time",
            ]
            aix_column_count = len(aix_iostat_columns)

            if operating_system == "AIX" and include_iostat:

                if iostat_processing and "<div" in line:  # iostat does not flag end
                    iostat_processing = False
                else:
                    # Found iostat
                    if "id=iostat" in line:
                        iostat_processing = True
                    # Is this a data line
                    if iostat_processing and len(line.split()) == aix_column_count:
                        iostat_row_dict = {}
                        # get rid of multiple whitespaces, then use comma separator
                        line = " ".join(line.split())
                        line = line.replace(" ", ",")

                        # Get the values add devices to database
                        values = line.split(",")
                        values = [i.strip() for i in values]  # strip off carriage return etc

                        values_converted = [get_aix_wacky_numbers(v) for v in values]

                        iostat_row_dict = dict(zip(aix_iostat_columns, values_converted))
                        iostat_row_dict["html name"] = html_filename
                        iostat_row_dict["Date"] = run_start_date.strftime("%m/%d/%y")

                        # Added for pretty processing
                        iostat_row_dict["datetime"] = f'{iostat_row_dict["Date"]} {iostat_row_dict["Time"]}'
                        iostat_rows_list.append(iostat_row_dict)

                    # First time in create column names
                    if iostat_processing and iostat_header == "":
                        aix_iostat_columns.extend(["Date"])
                        iostat_header = ",".join(aix_iostat_columns)

    if mgstat_header != "":
        # Create dataframe of rows. Shortcut here to creating table columns or later charts etc
        mgstat_df = pd.DataFrame(mgstat_rows_list)

        # "date" and "time" are reserved words in SQL. Rename the columns to avoid clashes later.
        mgstat_df.rename(columns={"Date": "RunDate", "Time": "RunTime"}, inplace=True)

        # Remove any rows with NaN
        mgstat_df.dropna(inplace=True)

    else:
        mgstat_df = pd.DataFrame({"empty": []})

    if vmstat_header != "":
        vmstat_df = pd.DataFrame(vmstat_rows_list)
        # "date" and "time" are reserved words in SQL. Rename the columns to avoid clashes later.
        vmstat_df.rename(columns={"Date": "RunDate", "Time": "RunTime"}, inplace=True)
        vmstat_df.dropna(inplace=True)
    else:
        vmstat_df = pd.DataFrame({"empty": []})

    if perfmon_header != "":

        perfmon_df = pd.DataFrame(perfmon_rows_list)
        perfmon_df.dropna(inplace=True)

        # add datetime column
        # The first column is a date time with timezone
        perfmon_df.columns = perfmon_df.columns[:0].tolist() + ["datetime"] + perfmon_df.columns[1:].tolist()

        # In some cases time is a separate column
        if perfmon_df.columns[1] == "Time":
            perfmon_df["datetime"] = perfmon_df["datetime"] + " " + perfmon_df["Time"]

        # preprocess time to remove decimal precision
        perfmon_df["datetime"] = perfmon_df["datetime"].apply(lambda x: x.split(".")[0])

    else:
        perfmon_df = pd.DataFrame({"empty": []})

    if iostat_header != "":
        iostat_df = pd.DataFrame(iostat_rows_list)
        # "date" and "time" are reserved words in SQL. Rename the columns to avoid clashes later.
        iostat_df.rename(columns={"Date": "RunDate", "Time": "RunTime"}, inplace=True)
        iostat_df.dropna(inplace=True)
    else:
        iostat_df = pd.DataFrame({"empty": []})

    if nfsiostat_header != "":
        nfsiostat_df = pd.DataFrame(nfsiostat_rows_list)
        nfsiostat_df.dropna(inplace=True)
    else:
        nfsiostat_df = pd.DataFrame({"empty": []})

    if aix_sar_d_header != "":
        aix_sar_d_df = pd.DataFrame(aix_sar_d_rows_list)
        aix_sar_d_df.rename(columns={"Date": "RunDate", "Time": "RunTime"}, inplace=True)
        aix_sar_d_df.dropna(inplace=True)
    else:
        aix_sar_d_df = pd.DataFrame({"empty": []})

    return mgstat_df, vmstat_df, iostat_df, nfsiostat_df, perfmon_df, aix_sar_d_df

# yaspe

Parse and chart pButtons and SystemPerformance files

# Yet Another System Performance Extractor

This will replace `yape`. I will add functionality as I need it. e.g. I expect to create charts with multiple interesting metrics. If you would like to see specific combinations let me know e.g. glorefs with CPU 

:: **NOTE:** Currently only supports ::

- IRIS/Caché (mgstat)
- Linux (vmstat, iostat)
- Windows (Perfmon)

## Create docker container image

- download the source files
- `cd` to folder with source files
- build yaspe container image: `docker build --no-cache -t yaspe .`

## Run the command over a pButtons or SystemPerformance file

Required argument `-i /data/filename.html` to point to the pButtons or SystemPerformance file.

See the help text:

```plaintext
$ docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -h
usage: yaspe [-h] [-i "/path/file.html"] [-x] [-a]
             [-e "/path/SystemPerformance.sqlite"]

Performance file review

optional arguments:
  -h, --help            show this help message and exit
  -i "/path/file.html", --input_file "/path/file.html"
                        Input html filename with full path
  -x, --iostat          Also plot iostat data (can take a long time)
  -a, --append          Do not overwrite database, append to existing database
  -e "/path/SystemPerformance.sqlite", --existing_database "/path/SystemPerformance.sqlite"
                        Chart existing database, database name with full path

Be safe, "quote the path"
```

For example, change to the folder with a SystemPerformance html file and run the command:

```plaintext
docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -i /data/mysystems_systemperformance_24hour_1sec.html
```

<hr>

Or put the path to the folder with the html file in the docker volume parameter and put the html file name after `-i /data/` 

```plaintext
docker run -v "/path/to/folder/with html file":/data --rm --name yaspe yaspe ./yaspe.py -i /data/mysystems_systemperformance_24hour_1sec.html
```

<hr>

To run _yaspe_ over multiple input files, for example a few days or a week, use the following steps:

- Copy all the SystemPerformance html files to one folder
- Use the `-a` (append) option to put all the metrics in the database (also `-x` if you want iostat)
- Use the `-e` (existing database option) to chart the appended database (also `-x` if you want iostat)

__Note:__ This works by appending data to database that contains extracted SystemPerformance data.
If the SystemPerformance files have a short sample period this can result in long run times and large output files with many data points. 
It may be a bit clunky to work with in the browser.
I suggest you run over a week without iostat (`-x`), then use the method above to deep dive on a day or couple of days.

Example of running over multiple days;
- change to the folder with the html files and run the commands, run:

```plaintext
for i in `ls *.html`;do docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -i /data/"${i}" -a; done
```

```plaintext
docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -e /data/SystemPerformance.sqlite
```

<hr>

## Output files

- An sqlite database file `SystemPerformance.sqlite` stores extracted metrics for (further processing (TBA))
- HTML charts for all columns in mgstat and vmstat or windows perfmon and output to folders under `./metrics`
- It is optional to create charts for iostat as this can take a long time if there is a big disk list

*Example output*

![alt text][logo]

<hr>

# Updates

Remove the old image and create a new one with updated source code

`docker rmi yaspe`

[logo]: https://github.com/murrayo/yaspe/blob/main/yaspe.gif "Example"


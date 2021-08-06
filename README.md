# yaspe
Parse and chart pButtons and SystemPerformance files

# Yet Another System Performance Extractor

## Create docker container image

- `cd` to folder with source files
- build container `docker build --no-cache -t yaspe .`

Required argument `-i /data/filename.html` to point to the pButtons or SystemPerformance file.

See the help text:

```plaintext
$ docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -h
usage: yaspe [-h] -i "/path/file.html" [--iostat]

Performance file review

optional arguments:
  -h, --help            show this help message and exit
  -i "/path/file.html", --input_file "/path/file.html"
                        Input html filename with full path
  --iostat              Also plot iostat data (can take a long time)

Be safe, "quote the path"
```

For example, change to the folder and run the command:

```plaintext
docker run -v "$(pwd)":/data --rm --name yaspe yaspe ./yaspe.py -i /data/mysystems_systemperformance_24hour_1sec.html
```

Or update  put the path in docker volume flag

```plaintext
docker run -v "/path/to/folder/with html file":/data --rm --name yaspe yaspe ./yaspe.py -i /data/mysystems_systemperformance_24hour_1sec.html
```

## Output files

- A sqlite file `SystemPerformance.sqlite` for further processing
- HTML charts for all columns in mgstat and vmstat or windows perfmon in folder `./metrics`
- Optional charts for iostat, this can take a long time if there is a big disk list

*Example output*

![alt text][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Example"


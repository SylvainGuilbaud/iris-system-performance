# docker run -v "$(pwd)":/data --rm --name yaspe murray1oldfield/yaspe:latest_M1 ./yaspe.py -h

# docker run -v "/Users/guilbaud/git/ancv/new_architecture/SystemPerformance":/data --rm --name yaspe murray1oldfield/yaspe:latest_M1 ./yaspe.py -i /data/perfo.html 


now=$(date +"%Y_%m_%d_%H_%M_%S")
docker run \
-v "./SystemPerformance":/data \
--rm --name yaspe yaspe \
./yaspe.py \
-i /data/formation-iris_IRIS_20230725_102233_30mins.html \
--system \
-o $now

docker run \
-v "./SystemPerformance":/data \
--rm --name yaspe yaspe \
./yaspe.py \
-i /data/formation-iris_IRIS_20230725_102233_30mins.html \
--png \
--system \
-o $now
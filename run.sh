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
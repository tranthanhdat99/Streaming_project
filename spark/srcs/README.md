## 1. Kiểm tra kết nối tới Kafka server

Kiểm tra kết nối tới 3 brokers

```shell
telnet localhost 9094
telnet localhost 9194
telnet localhost 9294
```
## 2. Copy file vào trong spark docker**

**Tạo thư mục:**

```shell
docker exec -ti spark-spark-1 mkdir -p /data/location
docker exec -ti spark-spark-worker-1 mkdir -p /data/location
docker exec -ti spark-spark-worker-2 mkdir -p /data/location
```

**Copy file từ host vào trong container:**

```shell
docker cp project/ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-1:/data/location
docker cp project/ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-worker-1:/data/location
docker cp project/ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-worker-2:/data/location
```

## 3. Chạy chương trình

```shell
(cd project && zip -r code.zip udf util tables) &&  
docker container stop kafka-streaming || true && 
docker container rm kafka-streaming || true && 
docker run -ti --name kafka-streaming \
--network=streaming-network \
-p 4040:4040 \
-v ./:/spark \
-v spark_lib:/opt/bitnami/spark/.ivy2 \
-v spark_data:/data \
-e KAFKA_SASL_JAAS_CONFIG='org.apache.kafka.common.security.plain.PlainLoginModule required username="kafka" password="UnigapKafka@2024";' \
-e PYSPARK_DRIVER_PYTHON='python' \
-e PYSPARK_PYTHON='./environment/bin/python' \
unigap/spark:3.5 bash -c "python -m venv pyspark_venv &&
source pyspark_venv/bin/activate &&
pip install -r /spark/requirements.txt &&
venv-pack -o pyspark_venv.tar.gz && 
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3 \
--archives pyspark_venv.tar.gz#environment \
--py-files /spark/project/code.zip /spark/project/kafka_streaming.py"
```
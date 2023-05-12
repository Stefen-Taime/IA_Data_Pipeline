# Variables
container_id_spark=6cf1fcf94888 #use your container_id with docker ps
local_path_spark=/home/your_path/Data_Storage/load_to_mongo.py
docker_path_spark=/tmp/load_to_mongo.py

container_id_hdfs=70d68dd98920
local_dir_hdfs=/home/your_path/Ingestion
docker_dir_hdfs=/tmp
hdfs_dir_hdfs=/input

api_script=/home/your_path/api.py

front_end_path=/home/your_path/front-end

# Targets
.PHONY: run_load_to_mongo
run_load_to_mongo:
	@docker cp $(local_path_spark) $(container_id_spark):$(docker_path_spark)
	@docker exec $(container_id_spark) /opt/bitnami/spark/bin/spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 $(docker_path_spark)

.PHONY: copy_files_to_hdfs
copy_files_to_hdfs:
	@for local_path in $(local_dir_hdfs)/*.json; do \
		filename=$$(basename -- "$$local_path"); \
		docker cp $$local_path $(container_id_hdfs):$(docker_dir_hdfs)/$$filename; \
		docker exec $(container_id_hdfs) hadoop fs -copyFromLocal $(docker_dir_hdfs)/$$filename $(hdfs_dir_hdfs)/$$filename; \
	done

.PHONY: run_api
run_api:
	@python $(api_script)

.PHONY: start_front_end
start_front_end:
	@cd $(front_end_path) && npm start

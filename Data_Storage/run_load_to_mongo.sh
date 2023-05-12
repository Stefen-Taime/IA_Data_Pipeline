#!/bin/bash

# Define container id for the Spark master
container_id=6cf1fcf94888

# Define the local path for your Python script
local_path=/home/your_path/Data_Storage/load_to_mongo.py

# Define the path where you want to store the Python script in docker container
docker_path=/tmp/load_to_mongo.py

# Copy Python script to the docker container
docker cp $local_path $container_id:$docker_path

# Execute Spark job submission command
docker exec $container_id /opt/bitnami/spark/bin/spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 $docker_path

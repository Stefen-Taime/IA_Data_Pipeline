#!/bin/bash

# Define container id for the namenode
container_id=70d68dd98920

# Define the local directory where your JSON files are stored
local_dir=/home/your_path/Ingestion

# Define the path where you want to store the file in docker container
docker_dir=/tmp

# Define the HDFS directory where you want to store the files
hdfs_dir=/input

# Loop over each JSON file in the local directory
for local_path in ${local_dir}/*.json
do
  # Get the filename
  filename=$(basename -- "$local_path")

  # Copy the file to the Docker container
  docker cp ${local_path} ${container_id}:${docker_dir}/${filename}

  # Execute Hadoop command to move file from Docker container to HDFS
  docker exec ${container_id} hadoop fs -put ${docker_dir}/${filename} ${hdfs_dir}/${filename}
done

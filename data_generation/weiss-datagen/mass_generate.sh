#!/usr/bin/env bash

env_name=MScProject
images_per_batch=20
start_batch_num=1
end_batch_num=1
save_folder=../data/generated_images

source activate ${env_name}
for (( i=${start_batch_num}; i<=${end_batch_num}; i++ ))
do
    location=${save_folder}/batch_${i}/
    mkdir -p ${location}
    python command.py -s ${location} -n ${images_per_batch} -c
done
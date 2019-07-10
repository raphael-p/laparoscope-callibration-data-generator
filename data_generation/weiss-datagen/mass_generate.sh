#!/usr/bin/env bash

env_name=MScProject
images_per_batch=20
start_batch_num=1
end_batch_num=3
save_folder=../data/generated_images

label_loc=${save_folder}/labels/
mkdir -p ${label_loc}
source activate ${env_name}
for (( i=${start_batch_num}; i<=${end_batch_num}; i++ ))
do
    save_loc=${save_folder}/batch_${i}/
    mkdir -p ${save_loc}
    python command.py -s ${save_loc} -l ${label_loc} -n ${images_per_batch} -c
done
#!/usr/bin/env bash

env_name=MScProject
images_per_batch=400
start_batch_num=2
end_batch_num=45
save_folder=../../../../../../../Downloads/data
img_folder=${save_folder}/generated_images/
label_loc=${save_folder}/labels/
mkdir -p ${label_loc}
source activate ${env_name}
for (( i=${start_batch_num}; i<=${end_batch_num}; i++ ))
do
    img_loc=${img_folder}/batch_${i}/
    mkdir -p ${img_loc}
    python command.py -s ${img_loc} -l ${label_loc} -n ${images_per_batch} -c
done
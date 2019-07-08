#!/usr/bin/env bash
source activate MScProject
images_per_batch=350
n_batches=20
start_batch_num=1
for (( i=${start_batch_num}; i<=${n_batches}; i++ ))
do
    location=../data/generated_images/batch_${i}/
    mkdir -p ${location}
    python command.py -s ${location} -n ${images_per_batch}
done
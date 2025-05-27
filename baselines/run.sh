#!/bin/bash

models=("gpt-4o") 

commands=(
  "python run_task.py --task blink_spatial"
  "python run_task.py --task blink_counting"
  "python run_task.py --task vd_illusion"
  "ADD_DOT=1 python run_task.py --task blink_viscorr"
  "ADD_DOT=1 python run_task.py --task blink_semcorr"
  "python run_task.py --task mme_commonsense_reasoning"
  "python run_task.py --task mme_count"
  "python run_task.py --task mme_existence"
  "python run_task.py --task mme_position"
  "python run_task.py --task mme_color"
  "python run_task.py --task ooo"
  "ADD_DOT=1 python run_task.py --task blink_functional_correspondence"
)

folders=("standard" "cot")

for folder in "${folders[@]}"; do
  cd "$folder" || exit
  echo "Running tasks in $folder"
  for model in "${models[@]}"; do
    echo "Using model: $model"
    for cmd in "${commands[@]}"; do
      full_cmd="MODEL=$model $cmd "
      echo "Running: $full_cmd"
      eval sleep 1
      eval "$full_cmd"
    done
  done
  cd .. 
done

echo "All tasks are running in the background."
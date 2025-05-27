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
  "python run_task.py --task angle"
  "python run_task.py --task diff"
  "python run_task.py --task rot-ang"
  "python run_task.py --task direction"
  "python run_task.py --task dif-ang"
)

folders=("cot" "standard" "scaffold")

for folder in "${folders[@]}"; do
  cd "$folder" || exit
  echo "Running tasks in $folder"
  for model in "${models[@]}"; do
    echo "Using model: $model"
    for cmd in "${commands[@]}"; do
      full_cmd="MODEL=$model $cmd &"
      echo "Running: $full_cmd"
      eval sleep 1
      eval "$full_cmd"
    done
  done
  cd .. 
done

echo "All tasks are running in the background."
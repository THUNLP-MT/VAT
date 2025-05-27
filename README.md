# Visual Abstract Thinking Empowers Multimodal Reasoning

This repository contains the official codebase for the paper "Visual Abstract Thinking Empowers Multimodal Reasoning".

---

## Installation

We recommend using a conda environment:

```bash
conda create -n vat python=3.9
conda activate vat

pip install Pillow opencv-python numpy gradio gradio_client networkx scipy datasets
```

---

## Image to Abstract Model Services

The `img2abs` directory contains two main modules for image abstraction:

### 1. informative-drawings

- `open_server.py`: Open-sketch style (port 8086)
- `contour_server.py`: Contour style (port 8085)
- `ani_server.py`: Anime style (port 8084)

To start a service (example for open_server.py):

```bash
cd img2abs/informative-drawings
python open_server.py
```

Replace with the corresponding `_server.py` file for other styles.

### 2. PhotoSketch

- `ps_server.py`: Photo-to-sketch style (port 8083)

To start:

```bash
cd img2abs/PhotoSketch
python ps_server.py
```

All services use Gradio and provide a web interface for image upload and abstraction.

---

## Tasks

## Running Main Tasks

The `run.sh` script in the project root can be used to batch run various tasks. It will automatically call scripts in subdirectories such as `vat`, supporting multiple models and tasks in parallel.

To run:

```bash
bash run.sh
```

The script will launch all configured tasks in the background. Logs and outputs will be saved in the corresponding subdirectories.

## Running a Single Task

You can run a single task with the following command:

```bash
python run_task.py --task your_task
```

Replace `your_task` with the name of the task you want to run.

### Environment Variables

- `MODEL`: Specify the model to use.
  - `gpt-4o`: gpt-4o-2024-11-20
  - `gemini`: gemini-2.0-pro-exp-02-05

- `sk_type`: Specify the type of visual abstract. Options are:
  - `ps`: PhotoSketch
  - `open`: OpenSketch
  - `contour`: Contour style
  - `anime`: Anime style

Example:

```bash
MODEL=gpt-4o sk_type=open python run_task.py --task ooo
```

> **Note:** For the tasks `blink_viscorr`, `blink_semcorr`, and `blink_functional_correspondence`, you need to set the environment variable `ADD_DOT=1` to mark reference points in the visual abstract. For example:
>
> ```bash
> ADD_DOT=1 MODEL=gpt-4o sk_type=open python run_task.py --task blink_viscorr
> ```

---

## Citation
If you find this project useful for your research, please cite the original paper.

---

## Acknowledgements
This project integrates and adapts code from the following open-source projects:
- [informative-drawings](https://github.com/carolineec/informative-drawings)
- [PhotoSketch](http://www.cs.cmu.edu/~mengtial/proj/sketch/)

For further details, please refer to the README files in each submodule.
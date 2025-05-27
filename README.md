# Visual Abstract Thinking Empowers Multimodal Reasoning

This repository contains the official codebase for the paper "Visual Abstract Thinking Empowers Multimodal Reasoning".

---

## Installation

We recommend using a conda environment:

```bash
conda create -n vat python=3.9
conda activate vat

pip install pyautogen==0.2.26
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

---


## Citation
If you find this project useful for your research, please cite the original paper.

---

## Acknowledgements
This project integrates and adapts code from the following open-source projects:
- [informative-drawings](https://github.com/carolineec/informative-drawings)
- [PhotoSketch](http://www.cs.cmu.edu/~mengtial/proj/sketch/)

For further details, please refer to the README files in each submodule.


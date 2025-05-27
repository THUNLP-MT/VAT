# Visual Abstract Thinking Empowers Multimodal Reasoning

This repository contains the official codebase for the paper "Visual Abstract Thinking Empowers Multimodal Reasoning".

<div align="center">

<!-- Project Banner -->
<img src="https://github.com/ironmt/picx-images-hosting/raw/master/fig1-ooo-44-manual-v6-1.4n7y6yzdg7.webp" alt="Visual Abstract Thinking Overview" width="90%"/>

<!-- Badges -->
<br><br>
<a href="https://github.com/THUNLP-MT/VAT"><img src="https://img.shields.io/badge/Project-Homepage-green" alt="Project Homepage"></a>
<a href="https://arxiv.org/abs/2505.20164"><img src="https://img.shields.io/badge/arXiv-2505.20164-red" alt="arXiv"></a>
<img src="https://visitor-badge.laobi.icu/badge?page_id=THUNLP-MT/VAT" alt="visitors">

</div>

## Introduction

Images usually convey richer detail than text, but often include redundant information which potentially downgrades multimodal reasoning performance. When faced with lengthy or complex messages, humans tend to employ abstract thinking to convert them into simple and concise abstracts. Inspired by this cognitive strategy, we introduce **V**isual **A**bstract **T**hinking (**VAT**), a novel thinking paradigm that prompts Multimodal Large Language Models (MLLMs) with visual abstract instead of explicit verbal thoughts or elaborate guidance, permitting a more concentrated visual reasoning mechanism. 

Explicit thinking, such as Chain-of-thought (CoT) or tool-augmented approaches, increases the complexity of reasoning process via inserting verbose intermediate steps, external knowledge or visual information. In contrast, VAT reduces redundant visual information and encourages models to focus their reasoning on more essential visual elements. 

Experimental results show that VAT consistently empowers different models, and achieves an average gain of 17\% over GPT-4o baseline by employing diverse types of visual abstracts, compared with 13\% of CoT, demonstrating that VAT better enhances visual reasoning abilities for MLLMs regarding conceptual, structural and relational reasoning tasks.
VAT is also compatible with CoT in knowledge-intensive multimodal reasoning tasks.
These findings highlight the effectiveness of visual reasoning via abstract thinking 
and encourage further exploration of more diverse reasoning paradigms from the perspective of human cognition.

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
If you find our work helpful, please cite us:
```bibtex
@misc{liu2025Visual,
  title = {Visual {{Abstract Thinking Empowers Multimodal Reasoning}}},
  author = {Liu, Dairu and Wang, Ziyue and Ruan, Minyuan and Luo, Fuwen and Chen, Chi and Li, Peng and Liu, Yang},
  year = {2025},
  month = may,
  number = {arXiv:2505.20164},
  eprint = {2505.20164},
  primaryclass = {cs},
  publisher = {arXiv},
  doi = {10.48550/arXiv.2505.20164},
  url = {http://arxiv.org/abs/2505.20164},
  archiveprefix = {arXiv},
  langid = {american},
}
```


---

## Acknowledgements
This project integrates and adapts code from the following open-source projects:
- [informative-drawings](https://github.com/carolineec/informative-drawings)
- [PhotoSketch](http://www.cs.cmu.edu/~mengtial/proj/sketch/)

For further details, please refer to the README files in each submodule.
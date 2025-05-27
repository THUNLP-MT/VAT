# Visual Abstract Thinking Empowers Multimodal Reasoning
<div align="center">
<!-- <<a href="https://github.com/THUNLP-MT/VAT"><img src="https://img.shields.io/badge/Project-Homepage-green" alt="Project Homepage"></a> -->
<a href="https://arxiv.org/abs/2505.20164"><img src="https://img.shields.io/badge/arXiv-2505.20164-red" alt="arXiv"></a>
<img src="https://visitor-badge.laobi.icu/badge?page_id=THUNLP-MT/VAT" alt="visitors">


Dairu Liu<sup>3\*</sup>, Ziyue Wang<sup>1\* :beginner:</sup>, Minyuan Ruan<sup>1\*</sup>, Fuwen Luo<sup>1</sup>,  
Chi Chen<sup>1</sup>, Peng Li<sup>2 :envelope:</sup>, Yang Liu<sup>1,2 :envelope:</sup>

<sup>1</sup>Dept. of Computer Science & Technology, Institute for AI, Tsinghua University, Beijing, China  
<sup>2</sup>Institute for AI Industry Research (AIR), Tsinghua University, Beijing, China  
<sup>3</sup>College of Software, Nankai University, Tianjin, China  

<sup>*</sup>Equal contribution  
<sup>:beginner:</sup>Project lead  
<sup>:envelope:</sup>Corresponding author



<img src="https://github.com/ironmt/picx-images-hosting/raw/master/fig1-ooo-44-manual-v6-1.4n7y6yzdg7.webp" alt="Visual Abstract Thinking Overview" width="90%"/>

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

## Data

You can download all task data from [Feishu Cloud](https://nankai.feishu.cn/drive/folder/APDKfGCbTlau9ydN0HscCPGSnge?from=from_copylink).
After downloading, put all task folders under the `./tasks` directory.

The structure should look like this:

```
./tasks/
├── blink_spatial/
├── blink_counting/
├── blink_viscorr/
├── blink_semcorr/
├── blink_functional_correspondence/
├── mme_commonsense_reasoning/
├── mme_count/
├── mme_existence/
├── mme_position/
├── mme_color/
├── ooo/
└── ...

```

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

- `ABS_TYPE`: Specify the type of visual abstract. Options are:
  - `ps`: PhotoSketch
  - `open`: OpenSketch
  - `contour`: Contour style
  - `anime`: Anime style

Example:

```bash
MODEL=gpt-4o ABS_TYPE=open python run_task.py --task ooo
```

### Supported Tasks and Benchmarks

Our VAT framework supports a variety of tasks for visual perception and multimodal reasoning, covering different benchmarks. Below is a list of all available tasks and their corresponding benchmarks:

| Task Name                        | Benchmark         |
|----------------------------------|-------------------|
| mme_existence                    | MME              |
| mme_count                        | MME              |
| mme_color                        | MME              |
| mme_position                     | MME              |
| mme_commonsense_reasoning        | MME              |
| blink_counting                   | BLINK            |
| blink_spatial                    | BLINK            |
| blink_viscorr                    | BLINK            |
| blink_semcorr                    | BLINK            |
| blink_functional_correspondence  | BLINK            |
| vd_illusion                      | HallusionBench   |
| ooo                              | Odd-One-Out      |
| direction                        | CoSpace          |
| angle                            | CoSpace          |
| dif-ang                          | CoSpace          |
| diff                             | CoSpace          |

These tasks cover object-centric perception, object relation reasoning, spatial reasoning, and commonsense reasoning.

> **Note:** For the tasks `blink_viscorr`, `blink_semcorr`, and `blink_functional_correspondence`, you need to set the environment variable `ADD_DOT=1` to mark reference points in the visual abstract. For example:
>
> ```bash
> ADD_DOT=1 MODEL=gpt-4o ABS_TYPE=open python run_task.py --task blink_viscorr
> ```

## Evaluation

You can use `calc.py` to evaluate the results of your tasks. The basic usage is:

```bash
python calc.py <outputs_folder_path> [--accp 0/1] [--abs_type <abstract_type>] [--model <model_name>]
```

- `<outputs_folder_path>`: Path to the folder containing the output results to be evaluated.
- `--accp 0/1`: Whether to calculate the acc+ metric for MME tasks (set to 1 for acc+, 0 for standard accuracy).
- `--abs_type <abstract_type>`: Specify the type of abstract to evaluate (e.g., `ps`, `open`, `contour`, `anime`).
- `--model <model_name>`: Specify the model name to be evaluated (e.g., `gpt-4o`, `gemini`).

**Example:**

```bash
python calc.py <outputs_folder_path> --accp 1 --abs_type open --model gpt-4o
```

This will evaluate all results in the `<outputs_folder_path>` folder, calculate acc+ for MME tasks, use the `open` abstract type, and specify the model as `gpt-4o`.

> **Note:** `calc.py` can only be used to evaluate tasks other than the CoSpace benchmark.

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

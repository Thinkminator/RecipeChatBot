# RecipeChatBot

A desktop GUI application for generating cooking recipes using various methods. It supports both text and speech interfaces.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [File Structure](#file-structure)

## Project Overview
RecipeChatBot is a desktop GUI application (Tkinter) that generates cooking recipes from 4 methods:
- List of recipes in datasets
- Hugging Face API (Not working)
- Hugging Face T5-based recipe generation model ([flax-community/t5-recipe-generation](https://huggingface.co/flax-community/t5-recipe-generation))
- [Task 2] TODO <br />

The app supports both text and speech interfaces. The architecture separates GUI, NLU/knowledge logic, and model inference so you can run the model locally (PyTorch) or fall back to Hugging Face remote inference.

## Features
### 1. Dictionary Searching
- Accepts a recipe request from the user (text or speech or image)
- Use [nlu.py](src\core\nlu.py) to extract dish name from request
- With [knowledge.py](src\core\knowledge.py) find and display respective recipe from [recipe dataset](data\recipes)
- Presents the recipe in a simple GUI and allows voice I/O

### 2. Hugging Face API Accessing
- Accepts a recipe request from the user (text or speech or image)
- Use [themealdb_api.py](src\core\themealdb_api.py) to pass the prompt to online Deepseek model via API
- Presents the recipe in a simple GUI and allows voice I/O

### 3. Pretrained Model Loading
- Accepts a recipe request from the user (text or speech or image) via [custom_llm.py](src\core\custom_llm.py)
- Uses a pretrained recipe-generation model to generate structured recipe text
- Presents the recipe in a simple GUI and allows voice I/O

### 4. Task 2
- Run multi-turn chat via [run_terminal_chat.py](src\scripts\run_terminal_chat.py)
- Implements a terminal-based chat loop where user inputs are confirmed with the ENTER key
- Supports context retention across multiple turns
- Demonstrates correct Terminal operation and interaction flow

### 5. Task 3
- Run evaluation via [evaluate.py](src\scripts\evaluate.py)
- Test different pretrained models on benchmark datasets (e.g., BoolQ, PIQA) for reading comprehension and commonsense reasoning
- Collect accuracy and performance metrics for systematic comparison across models

### Extra. VLM-Integrated Prompting
- Accept recipes searching with [pictures](src\core\vlm.py)

## File Structure
```
RecipeChatBot/
├─ README.md                      # Project overview, setup, usage instructions
├─ environment.yml                # Conda environment config for dependencies
├─ data/
│  ├─ recipes/                   # Recipe text files 
│  └─ images/                    # Pictures for VLM Testing
├─ src/
│  ├─ __init__.py                # Marks src as a package
│  ├─ stacked_gui/
│  │  ├── app.py                    # Router (single Tk root), entry point
│  │  ├── backend.py             # Shared logic (tries to import your real
│  │  └── pages/
│  │   ├─ __init__.py
│  │   ├─ base_page.py                # BasePage with Back button & header
│  │   ├─ mode_selection_page.py      # Page selection for Task1 models, Task 2 model
│  │   ├─ input_type_page.py          # Select text/Audio/Image input page to the model
│  │   ├─ llm_parameter_page.py       # Setting page for Task 2 model parameters
│  │   ├─ text_page.py                # Text input page to interact with different models
│  │   ├─ speech_page.py              # Audio input page to interact with different models
│  │   ├─ image_page.py               # Image input page to interact with different models
│  ├─ core/     
│  │  ├─ __init__.py
│  │  ├─ nlu.py                  # Natural Language Understanding (dish extraction)
│  │  ├─ custom_llm.py 
│  │  ├─ knowledge.py            # Recipe lookup, file reading
│  │  ├─ themealdb_api,py
│  │  ├─ llm_adapter.py          # Task 2 multi-turn chat
│  │  └─ utils.py                # Helper functions (logging, config loading) TODO
│  ├─ evaluation/
│  │  ├─ __init__.py
│  │  ├─ evaluator.py            # Task 3 Performance evaluation class
│  │  └─ benchmarks/             # Sample questions and gold answers
│  └─ scripts/
│     ├─ __init__.py
│     ├─ run_ui.py               # Script to launch the main UI (mode_selection_ui)
│     ├─ run_terminal_chat.py   # CLI chat interface
│     ├─ download_models.py     # Scripts to download large models if needed
│     └─ evaluate.py               # Task 3 Performance evaluation script
├─ tests/
│  ├─ test_nlu.py               # Unit tests for NLU functions
│  ├─ test_knowledge.py         # Unit tests for recipe lookup
│  └─ test_llm_adapter.py       # Unit tests for LLM interface
├─ reports/
     └─ project_report.pdf        # Combined project report for submission
```
## Quick Setup
### 1. Create & Activate Recommended Environment
```sh
conda env create -f environment.yml
conda activate RecipeChatBot
```

### 2. Running the App
Launch GUI
```sh
python src/stacked_gui/app.py
```

### 3. Run with CUDA

To run GPT4All with CUDA support, ensure your system has the following:

- A compatible NVIDIA GPU
- CUDA and Vulkan SDK installed and properly configured

#### Building from Source

GPT4All must be built from source to enable CUDA support. Follow the instructions in the [GPT4All PyPI page](https://pypi.org/project/gpt4all/) under the "Local Build" section.

> **Note:** Version `v3.4.2` is recommended, as it has been tested. Some newer versions may contain bugs.  

You can switch to this version using:

```git checkout v3.4.2```

## TODO

### 1. Add Performance Evaluation
Implement evaluation scripts in src/evaluation/.
Prepare benchmark questions and expected answers.
Automate accuracy or correctness measurement.

### 2. Document and Report
Keep your README updated.
Write your project report with methodology, results, and challenges.
Comment your code well.
# Local RAG Chatbot

This is the complete runnable project. All RAG application files are in:

`D:\AI\files\VibeDemo`

A local document question-answering app built with Python, Streamlit, LangChain, Ollama, and persistent ChromaDB.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- Enough local disk space for the models and ChromaDB index

## Installation

Open PowerShell and change to the project folder:

```powershell
cd D:\AI\files\VibeDemo
```

From the project folder, create and activate a virtual environment:

```powershell
& D:\Python\python.exe -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The virtual environment belongs to this project and is located at:

`D:\AI\files\VibeDemo\.venv`

There is no separate project environment in `D:\AI\files\.venv`.

If the project environment already exists, do not recreate it. Activate it
directly from the project folder:

```powershell
cd D:\AI\files\VibeDemo
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
```

If `D:\Python\python.exe` is not present on another machine, replace it with
the full path to that machine's Python executable. The `py` command is not
available in this installation.

Pull the required Ollama models:

```powershell
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

If Ollama is not already running, start it in a separate terminal:

```powershell
ollama serve
```

The app uses `http://localhost:11434/` by default.

## Run

```powershell
cd D:\AI\files\VibeDemo
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the displayed local URL in a browser. Upload one or more PDF, DOCX, TXT, or MD files in the sidebar and select **Process Documents**.

The main application file is `D:\AI\files\VibeDemo\app.py`.

## Features

- Persistent ChromaDB storage in `data/chroma/`
- Local uploaded files in `data/uploads/`
- Recursive character chunking with defaults of 1000 characters and 150 overlap
- Duplicate chunk prevention using deterministic content-based IDs
- Top four retrieved chunks shown for every answer
- Clear chat, delete documents, and clear ChromaDB actions
- Answers constrained to retrieved document context

The exact fallback response for questions not answered by the documents is:

> I don't have enough information in the provided documents.

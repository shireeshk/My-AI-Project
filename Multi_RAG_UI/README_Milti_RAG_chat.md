# Multi RAG Chatbot

A local Retrieval-Augmented Generation (RAG) chatbot built with Python, Streamlit, LangChain, Chroma, and Ollama.

The application allows users to upload multiple documents, create searchable document chunks, store their embeddings in Chroma, retrieve relevant content, and ask questions using a locally running LLM.

## High-Level Overview

The application follows this RAG workflow:

```text
Upload Documents
      ↓
Document Loading
      ↓
Text Chunking
      ↓
Generate Embeddings
      ↓
Store in Chroma Vector Database
      ↓
User Question
      ↓
Retrieve Relevant Chunks
      ↓
Build Prompt with Context + Chat History
      ↓
Ollama LLM
      ↓
Generated Answer
```

### Supported Documents

- PDF
- DOCX
- TXT
- Markdown (`.md`)

### Main Components

| Component | Technology |
|---|---|
| User Interface | Streamlit |
| Programming Language | Python |
| RAG Framework | LangChain |
| Vector Database | Chroma |
| Embedding Model | Ollama `nomic-embed-text` |
| LLM | Ollama `llama3.2:1b` |
| Application File | `UI_multie.py` |

## How It Works

1. **Document Upload** — Upload one or more supported documents through Streamlit.
2. **Document Loading** — The appropriate LangChain loader is selected based on the file type.
3. **Chunking** — Documents are split using `RecursiveCharacterTextSplitter` with `chunk_size=200` and `chunk_overlap=50`.
4. **Embeddings** — Each chunk is converted into an embedding using `nomic-embed-text`.
5. **Vector Database** — Embeddings are stored in Chroma under `./ui_rag_demo`.
6. **Retrieval** — The application retrieves the top 2 relevant chunks for a question.
7. **Generation** — Retrieved context, conversation history, and the question are sent to `llama3.2:1b` through Ollama.

## Prerequisites

- Python 3.10 or newer
- Ollama
- Git (if cloning the repository)

## 1. Create a Python Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 2. Configure Ollama

Make sure Ollama is installed and running.

Pull the embedding model:

```powershell
ollama pull nomic-embed-text
```

Pull the LLM:

```powershell
ollama pull llama3.2:1b
```

Verify:

```powershell
ollama list
```

The application expects Ollama at:

```text
http://localhost:11434
```

## 3. Run the Application

From the project directory:

```powershell
streamlit run UI_multie.py
```

Open the Streamlit URL, normally:

```text
http://localhost:8501
```

## 4. Using the Application

1. Start Ollama.
2. Start Streamlit.
3. Upload one or more PDF, DOCX, TXT, or MD files.
4. Wait for the documents, chunks, embeddings, and Chroma database to be created.
5. Enter a question.
6. Click **Ask**.
7. Expand **Retrieved Context** to inspect the chunks retrieved from Chroma.
8. Review the generated answer.

## Example

After uploading a document containing a support process, ask:

```text
What is the escalation process?
```

The application retrieves relevant chunks from the document and supplies them to the LLM as context.

## Project Structure

```text
Multi-RAG/
│
├── UI_multie.py
├── requirements.txt
├── README.md
└── .gitignore
```

The `ui_rag_demo` directory is created/used by Chroma for the local vector database.

## Public GitHub Repository

Do not commit sensitive information or private documents.

Avoid pushing:

- Passwords
- API keys
- Access tokens
- Credentials
- Private documents
- Personal information
- Sensitive company information
- Virtual environments
- Local Chroma database files

Recommended `.gitignore` entries:

```text
.venv/
__pycache__/
.env
ui_rag_demo/
uploads/
data/
*.log
```

## Current Limitations

This is a local RAG learning/demo application. Possible improvements include:

- Semantic chunking
- Configurable chunk size and overlap
- Similarity/relevance thresholds
- Reranking
- Source citations
- Better metadata handling
- Authentication and authorization
- Prompt-injection protection
- PII detection and masking
- Audit logging
- Dockerization
- GPU-based inference

## Future Architecture

The application can later evolve into a more enterprise-oriented GenAI/RAG architecture:

```text
                  FastAPI / Streamlit
                         │
             ┌───────────┼───────────┐
             │           │           │
          Security      RAG        Audit
             │           │           │
             │        Chroma         │
             │           │           │
             └──────── Ollama ───────┘
                         │
                         ↓
                        LLM
```

This project provides a foundation for progressing from a local RAG prototype to a more enterprise-oriented GenAI application.

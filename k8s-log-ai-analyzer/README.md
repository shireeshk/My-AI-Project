# Kubernetes AI Log Analyzer

A local Streamlit application for analyzing Linux, Kubernetes,
and application logs using:

- Python
- Streamlit
- Kubernetes troubleshooting rules
- LangChain
- Chroma
- Ollama
- RAG
- Local embeddings
- Local LLM inference

## Architecture

User
  |
  v
Streamlit
  |
  +--> ZIP/TAR extraction
  |
  +--> Log normalization
  |
  +--> Kubernetes rule engine
  |
  +--> Chroma vector database
  |
  +--> Ollama embeddings
  |
  +--> Retrieval
  |
  +--> Ollama LLM
  |
  v
Incident Analysis

## Requirements

Python 3.10+

Ollama

Recommended models:

    ollama pull llama3.2:1b
    ollama pull nomic-embed-text

## Installation

Create a virtual environment:

    python -m venv .venv

Linux/macOS:

    source .venv/bin/activate

Windows:

    .venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

## Start Ollama

Make sure Ollama is running:

    ollama serve

Verify:

    ollama list

Pull models:

    ollama pull llama3.1:1b
    ollama pull nomic-embed-text

## Start Application

    streamlit run app.py

Open:

    http://localhost:8501

## Supported Files

Individual files:

    .log
    .txt
    .out
    .err
    .json
    .yaml
    .yml

Archives:

    .zip
    .tar
    .tar.gz
    .tgz

Multiple files can be uploaded simultaneously.

## Kubernetes Data

Useful commands:

    kubectl logs <pod>

    kubectl logs <pod> --previous

    kubectl describe pod <pod>

    kubectl get events --sort-by=.lastTimestamp

    kubectl get pod <pod> -o yaml

For multiple containers:

    kubectl logs <pod> --all-containers=true

Save logs:

    kubectl logs <pod> --previous > pod-previous.log

Save describe output:

    kubectl describe pod <pod> > pod-describe.txt

## Example Investigation

Upload:

    pod-previous.log
    pod-describe.txt

The deterministic engine checks for:

    CrashLoopBackOff
    OOMKilled
    ImagePullBackOff
    ErrImagePull
    Probe failures
    DNS failures
    Connection failures
    Permission failures
    Application exceptions

The RAG layer then retrieves relevant log sections.

Ollama generates the final explanation.

## Privacy

Logs remain local.

The application does not require an external AI API.

Ollama performs local LLM inference.

Do not upload credentials, secrets, tokens,
private keys, or other sensitive information.

## Security

Archive extraction contains path traversal protection.

File and archive size limits are enforced.

Production deployments should additionally implement:

- authentication
- authorization
- audit logging
- malware scanning
- stronger archive limits
- secret redaction
- persistent vector-store isolation
- per-user sessions

## TEST IT
cd k8s-log-ai-analyzer

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

ollama pull llama3.1:8b
ollama pull nomic-embed-text

python samples/create_samples.py

streamlit run app.py

"""Local document RAG chatbot using Streamlit, Ollama, and ChromaDB."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "local_rag_documents"
OLLAMA_URL = "http://localhost:11434/"
LLM_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"
SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt", "md"}
FALLBACK_ANSWER = "I don't have enough information in the provided documents."

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You answer questions only using the retrieved context below.
Do not use outside knowledge and do not hallucinate. If the answer is not
contained in the context, reply exactly:
"I don't have enough information in the provided documents."

Retrieved context:
{context}""",
        ),
        ("human", "{question}"),
    ]
)


def ensure_directories() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource(show_spinner=False)
def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_URL)


@st.cache_resource(show_spinner=False)
def get_llm() -> ChatOllama:
    return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_URL, temperature=0)


@st.cache_resource(show_spinner=False)
def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def reset_vectorstore() -> None:
    get_vectorstore().delete_collection()
    get_vectorstore.clear()
    get_vectorstore()


def file_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_file(path: Path) -> list[Document]:
    extension = path.suffix.lower().lstrip(".")
    if extension == "pdf":
        return PyPDFLoader(str(path)).load()
    if extension == "docx":
        return Docx2txtLoader(str(path)).load()
    if extension in {"txt", "md"}:
        return TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
    raise ValueError(f"Unsupported file type: .{extension}")


def source_label(metadata: dict[str, Any]) -> str:
    source = Path(str(metadata.get("source", "Unknown"))).name
    page = metadata.get("page")
    return f"{source} (page {int(page) + 1})" if page is not None else source


def get_all_chunks() -> list[Document]:
    result = get_vectorstore().get(include=["documents", "metadatas"])
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []
    return [
        Document(page_content=text, metadata=metadata or {})
        for text, metadata in zip(documents, metadatas)
    ]


def process_documents(files: list[Any], chunk_size: int, chunk_overlap: int) -> tuple[int, int]:
    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    all_chunks: list[Document] = []
    for uploaded_file in files:
        raw = uploaded_file.getvalue()
        digest = file_digest(raw)
        destination = UPLOAD_DIR / f"{digest[:16]}_{Path(uploaded_file.name).name}"
        destination.write_bytes(raw)
        loaded_documents = load_file(destination)
        chunks = splitter.split_documents(loaded_documents)
        for index, chunk in enumerate(chunks):
            chunk.metadata = {
                **chunk.metadata,
                "source": uploaded_file.name,
                "file_hash": digest,
                "chunk_index": index,
                "page": chunk.metadata.get("page"),
            }
            chunk_id = hashlib.sha256(
                f"{digest}:{index}:{chunk.page_content}".encode("utf-8")
            ).hexdigest()
            chunk.metadata["chunk_id"] = chunk_id
            chunk.metadata["source_path"] = str(destination)
            all_chunks.append(chunk)

    if not all_chunks:
        return 0, 0

    ids = [str(chunk.metadata["chunk_id"]) for chunk in all_chunks]
    existing = get_vectorstore().get(ids=ids, include=["metadatas"])
    existing_ids = set(existing.get("ids") or [])
    new_chunks = [
        (chunk, chunk_id)
        for chunk, chunk_id in zip(all_chunks, ids)
        if chunk_id not in existing_ids
    ]
    if new_chunks:
        get_vectorstore().add_documents(
            documents=[item[0] for item in new_chunks],
            ids=[item[1] for item in new_chunks],
        )
    return len(files), len(new_chunks)


def answer_question(question: str) -> tuple[str, list[Document]]:
    retrieved = get_vectorstore().similarity_search(question, k=4)
    if not retrieved:
        return FALLBACK_ANSWER, []
    context = "\n\n".join(
        f"[{source_label(doc.metadata)}]\n{doc.page_content}" for doc in retrieved
    )
    response = get_llm().invoke(RAG_PROMPT.invoke({"context": context, "question": question}))
    answer = response.content if isinstance(response.content, str) else str(response.content)
    return answer.strip() or FALLBACK_ANSWER, retrieved


def clear_chat() -> None:
    st.session_state.messages = []


def delete_documents() -> None:
    reset_vectorstore()
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def render_chunk_inventory() -> None:
    chunks = get_all_chunks()
    st.subheader("Indexed chunks")
    st.caption(f"{len(chunks)} chunk(s) stored in persistent ChromaDB.")
    if not chunks:
        st.info("No chunks indexed yet. Upload documents and click Process Documents.")
        return
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.metadata
        st.markdown(f"**Chunk {index}** — {source_label(metadata)}")
        st.caption(
            f"Chunk ID: {metadata.get('chunk_id', 'unknown')} | "
            f"Chunk index: {metadata.get('chunk_index', 'unknown')}"
        )
        st.code(chunk.page_content, language="text")


def main() -> None:
    ensure_directories()
    st.set_page_config(page_title="Local RAG Chatbot", page_icon="📚", layout="wide")
    st.title("📚 Local RAG Chatbot")
    st.write("Ask questions about your local PDF, DOCX, TXT, and Markdown documents.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Document management")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=sorted(SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
            help="Files are stored locally in data/uploads.",
        )
        chunk_size = st.number_input("Chunk size", min_value=100, value=1000, step=100)
        chunk_overlap = st.number_input(
            "Chunk overlap", min_value=0, value=150, step=25
        )
        if st.button("Process Documents", type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("Upload at least one document first.")
            else:
                try:
                    with st.spinner("Loading, chunking, embedding, and indexing..."):
                        document_count, new_chunk_count = process_documents(
                            uploaded_files, int(chunk_size), int(chunk_overlap)
                        )
                    st.success(
                        f"Processed {document_count} document(s); "
                        f"added {new_chunk_count} new chunk(s)."
                    )
                except Exception as exc:
                    st.error(f"Could not process documents: {exc}")

        st.divider()
        if st.button("Clear chat", use_container_width=True):
            clear_chat()
            st.rerun()
        if st.button("Delete documents", use_container_width=True):
            try:
                delete_documents()
                clear_chat()
                st.success("Uploaded documents and indexed chunks deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete documents: {exc}")
        if st.button("Clear ChromaDB", use_container_width=True):
            try:
                reset_vectorstore()
                st.success("ChromaDB cleared. Local uploaded files were kept.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not clear ChromaDB: {exc}")

        stored_files = sorted(
            path.name for path in UPLOAD_DIR.iterdir() if path.is_file()
        )
        st.subheader("Uploaded documents")
        if stored_files:
            for name in stored_files:
                st.write(f"- {name}")
        else:
            st.caption("No documents uploaded.")
        st.metric("Number of documents", len(stored_files))
        try:
            st.metric("Number of chunks", get_vectorstore()._collection.count())
        except Exception:
            st.metric("Number of chunks", 0)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("retrieved"):
                with st.expander("Retrieved chunks"):
                    for doc in message["retrieved"]:
                        st.markdown(f"**{source_label(doc.metadata)}**")
                        st.code(doc.page_content, language="text")

    question = st.chat_input("Ask a question about your documents...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Searching documents and asking Ollama..."):
                    answer, retrieved = answer_question(question)
                st.markdown(answer)
                with st.expander(f"Retrieved chunks ({len(retrieved)})"):
                    if retrieved:
                        for doc in retrieved:
                            st.markdown(f"**{source_label(doc.metadata)}**")
                            st.code(doc.page_content, language="text")
                    else:
                        st.info("No indexed chunks matched this question.")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "retrieved": retrieved,
                    }
                )
            except Exception as exc:
                error_message = (
                    "I couldn't answer because the local RAG service failed. "
                    f"Check that Ollama is running and the required models are installed. Details: {exc}"
                )
                st.error(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message}
                )

    render_chunk_inventory()


if __name__ == "__main__":
    main()

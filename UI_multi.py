# Import Streamlit for UI
import streamlit as st
import tempfile
import os
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredFileLoader
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama


st.title("Multi RAG Chatbot")
st.write("Welcome everyone to building UI session")


# =========================================================
# Initialize Chat History
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# Upload Multiple Documents
# =========================================================

uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True
)


documents = []


# =========================================================
# Handle Multiple File Uploads
# =========================================================

if uploaded_files:

    temp_dir = tempfile.mkdtemp()

    for uploaded_file in uploaded_files:

        temp_path = os.path.join(
            temp_dir,
            uploaded_file.name
        )

        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"{uploaded_file.name} uploaded")

        # Get file extension
        suffix = Path(temp_path).suffix.lower()

        # Select appropriate loader
        if suffix == ".pdf":
            loader = PyPDFLoader(temp_path)

        elif suffix == ".docx":
            loader = UnstructuredWordDocumentLoader(temp_path)

        elif suffix == ".txt":
            loader = TextLoader(temp_path)

        elif suffix == ".md":
            loader = UnstructuredFileLoader(temp_path)

        # Load document
        file_documents = loader.load()

        # Add source filename to metadata
        for doc in file_documents:
            doc.metadata["source"] = uploaded_file.name

        # Add this file's documents to the main list
        documents.extend(file_documents)

    st.success(
        f"{len(uploaded_files)} files uploaded and "
        f"{len(documents)} document sections loaded"
    )


# =========================================================
# Create Chunks
# =========================================================

if documents:

    with st.spinner("Creating Chunks..."):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )

        chunks = text_splitter.split_documents(documents)

    st.success(f"{len(chunks)} chunks created")


    # =====================================================
    # Create Embeddings
    # =====================================================

    with st.spinner("Creating Embeddings..."):

        embeddings = OllamaEmbeddings(
            model="nomic-embed-text"
        )


    # =====================================================
    # Create Vector Database
    # =====================================================

    with st.spinner("Creating Vector Database..."):

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./ui_rag_demo"
        )

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 2}
        )

    st.success("Vector DB Created")


    # =====================================================
    # Create LLM
    # =====================================================

    llm = ChatOllama(
        model="llama3.2:1b",
        base_url="http://localhost:11434"
    )


    # =====================================================
    # Create Prompt
    # =====================================================

    prompt = ChatPromptTemplate.from_messages([

        (
            "system",
            """
            You are a document question-answering assistant.

            Answer the user's question using ONLY the information
            provided in the document context.

            Use the conversation history only to understand
            follow-up questions.

            If the answer cannot be found in the document context,
            say that you don't have enough information.
            """
        ),

        (
            "system",
            "Document Context:\n{context}"
        ),

        (
            "system",
            "Conversation History:\n{history}"
        ),

        (
            "human",
            "{input}"
        )
    ])


    # =====================================================
    # Display Previous Chat History
    # =====================================================

    for message in st.session_state.chat_history:

        if isinstance(message, HumanMessage):

            st.chat_message("user").write(
                message.content
            )

        elif isinstance(message, AIMessage):

            st.chat_message("assistant").write(
                message.content
            )


    # =====================================================
    # User Question
    # =====================================================

    question = st.text_input("Ask your question")


    # =====================================================
    # Ask Button
    # =====================================================

    if st.button("Ask"):

        if question:

            # -------------------------------------------------
            # Retrieval
            # -------------------------------------------------

            retrieved_docs = retriever.invoke(question)

            context = "\n\n".join(
                [
                    doc.page_content
                    for doc in retrieved_docs
                ]
            )


            # -------------------------------------------------
            # Show Retrieved Context
            # -------------------------------------------------

            with st.expander("Retrieved Context"):

                st.write(context)


            # -------------------------------------------------
            # Convert Chat History to Text
            # -------------------------------------------------

            history_text = "\n".join(

                [
                    f"User: {message.content}"
                    if isinstance(message, HumanMessage)
                    else f"Assistant: {message.content}"

                    for message in st.session_state.chat_history
                ]
            )


            # -------------------------------------------------
            # Create Final Prompt
            # -------------------------------------------------

            final_prompt = prompt.format(
                context=context,
                history=history_text,
                input=question
            )


            # -------------------------------------------------
            # Send Prompt to LLM
            # -------------------------------------------------

            with st.spinner("Generating Answer..."):

                response = llm.invoke(final_prompt)


            # -------------------------------------------------
            # Save Conversation to History
            # -------------------------------------------------

            st.session_state.chat_history.append(
                HumanMessage(content=question)
            )

            st.session_state.chat_history.append(
                AIMessage(content=response.content)
            )


            # -------------------------------------------------
            # Display Answer
            # -------------------------------------------------

            st.subheader("Assistant")

            st.write(response.content)

        else:

            st.warning("Please enter a question.")

else:

    st.info("Please upload one or more documents to start.")

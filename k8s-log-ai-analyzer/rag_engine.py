from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


class LogRAG:

    def __init__(
        self,
        collection_name="k8s_logs",
        ollama_url="http://localhost:11434",
        embedding_model="nomic-embed-text",
    ):

        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_url,
        )

        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def index_logs(self, files):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
        )

        documents = []

        for filename, content in files:

            chunks = splitter.split_text(content)

            for index, chunk in enumerate(chunks):

                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "filename": filename,
                            "chunk": index,
                        },
                    )
                )

        if documents:
            self.vectorstore.add_documents(documents)

        return len(documents)

    def search(self, query, k=5):

        docs = self.vectorstore.similarity_search(
            query,
            k=k,
        )

        return docs
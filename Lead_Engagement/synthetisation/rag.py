import os
import nltk
from dotenv import load_dotenv
from pathlib import Path

# Télécharger les ressources nécessaires de NLTK (une seule fois)
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI


# Classe de gestion de Gemini
class LLMManager:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def ask_with_context(self, question, context):
        prompt = f"""Réponds précisément à la question ci-dessous en te basant uniquement sur ce contexte :

=== CONTEXTE ===
{context}

=== QUESTION ===
{question}
"""
        return self.llm.invoke(prompt).content

def main():
    load_dotenv()

    # --- Dossiers ---
    data_root = Path("outputs")  # Contient les rapports .md
    db_path = Path(".chroma_db")

    if not data_root.exists():
        print("❌ Aucun rapport trouvé dans le dossier 'outputs'.")
        return

    # --- Chargement des rapports markdown (.md) ---
    loader = DirectoryLoader(str(data_root), glob="**/*.md")
    raw_documents = loader.load()

    if not raw_documents:
        print("❌ Aucun fichier Markdown à indexer.")
        return

    # --- Chunking ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
    )
    chunks = text_splitter.split_documents(raw_documents)

    # --- Vectorisation via ChromaDB ---
    chroma_client = chromadb.PersistentClient(path=str(db_path))
    collection = chroma_client.get_or_create_collection(
        name="lead_reports_collection",
        metadata={"hnsw:space": "cosine"}
    )

    documents = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [f"report_{i}" for i in range(len(chunks))]
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ {len(documents)} rapports indexés dans ChromaDB.")

    # --- Initialisation LLM ---
    llm_manager = LLMManager()

    # --- Boucle Q/R ---
    while True:
        question = input("\n💬 Pose une question sur un rapport (ou 'exit') : ")
        if question.lower() in ["exit", "quit"]:
            break

        results = collection.query(query_texts=[question], n_results=5)
        context_chunks = results["documents"][0]
        context = "\n\n".join(context_chunks)

        # --- Réponse ---
        answer = llm_manager.ask_with_context(question, context)
        print("\n🤖 Réponse :\n", answer)

if __name__ == "__main__":
    main()

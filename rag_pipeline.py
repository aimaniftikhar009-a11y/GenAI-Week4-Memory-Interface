<<<<<<< HEAD

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

import chromadb


# STEP 1: Load API key
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )

client = genai.Client(api_key=API_KEY)


# STEP 2: Connect to existing ChromaDB
db_path = BASE_DIR / "chroma_db"

chroma_client = chromadb.PersistentClient(
    path=str(db_path)
)

collection = chroma_client.get_collection(
    name="document_chunks"
)


# STEP 3: Create query embedding
def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values


# STEP 4: Retrieve top 3 relevant chunks
def retrieve_context(question):
    if collection.count() == 0:
        return []

    query_embedding = create_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(3, collection.count()),
        include=["documents", "distances"]
    )

    documents = results["documents"][0]

    distances = results["distances"][0]

    # Ignore chunks that are too dissimilar.
    # ChromaDB uses cosine distance for this collection.
    context_chunks = []

    for document, distance in zip(documents, distances):
        if distance < 0.65:
            context_chunks.append(document)

    return context_chunks


# STEP 5: Build a strict prompt
def build_prompt(question, context_chunks):
    if not context_chunks:
        return None

    context = "\n\n".join(
        [
            f"<chunk id='{i}'>\n{chunk}\n</chunk>"
            for i, chunk in enumerate(context_chunks, start=1)
        ]
    )

    prompt = f"""
You are a helpful question-answering assistant.

STRICT RULES:
1. Answer using ONLY the provided context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer is not present in the context,
   reply exactly:
   I cannot find the answer in the provided documents.
5. Mention the chunk number used for your answer.

<context>
{context}
</context>

<question>
{question}
</question>

Write a clear, simple answer.
"""

    return prompt


# STEP 6: Generate answer using Gemini
def generate_answer(question):
    print("\nSearching the vector database...")

    context_chunks = retrieve_context(question)

    if not context_chunks:
        print("\nAnswer:")
        print(
            "I cannot find the answer in the provided documents."
        )
        print("\nSource: No relevant context found.")
        return

    prompt = build_prompt(question, context_chunks)

    print("Relevant chunks retrieved:", len(context_chunks))
    print("Generating answer with Gemini...")

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    answer = response.text

    if not answer:
        answer = (
            "I cannot find the answer in the provided documents."
        )

    print("\n" + "=" * 45)
    print("QUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)

    print("\nSOURCE CHUNKS:")
    for i, chunk in enumerate(context_chunks, start=1):
        print(f"\nChunk {i}:")
        print(chunk)

    print("\n" + "=" * 45)


# STEP 7: Run the RAG pipeline
if __name__ == "__main__":
    print("WEEK 3: FULL RAG PIPELINE")
    print("Type 'exit' to close the program.")

    while True:
        question = input("\nEnter your question: ").strip()

        if question.lower() == "exit":
            print("RAG Pipeline closed.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            generate_answer(question)

        except Exception as error:
            print("\nAn error occurred:")
            print(error)
            print(
                "\nCheck your API key, model access, "
                "and Week 2 database setup."
            )

print("Week 3 RAG Pipeline Started!")

if __name__ == "__main__":
    print("Python file is working correctly.")
=======

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

import chromadb


# STEP 1: Load API key
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )

client = genai.Client(api_key=API_KEY)


# STEP 2: Connect to existing ChromaDB
db_path = BASE_DIR / "chroma_db"

chroma_client = chromadb.PersistentClient(
    path=str(db_path)
)

collection = chroma_client.get_collection(
    name="document_chunks"
)


# STEP 3: Create query embedding
def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values


# STEP 4: Retrieve top 3 relevant chunks
def retrieve_context(question):
    if collection.count() == 0:
        return []

    query_embedding = create_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(3, collection.count()),
        include=["documents", "distances"]
    )

    documents = results["documents"][0]

    distances = results["distances"][0]

    # Ignore chunks that are too dissimilar.
    # ChromaDB uses cosine distance for this collection.
    context_chunks = []

    for document, distance in zip(documents, distances):
        if distance < 0.65:
            context_chunks.append(document)

    return context_chunks


# STEP 5: Build a strict prompt
def build_prompt(question, context_chunks):
    if not context_chunks:
        return None

    context = "\n\n".join(
        [
            f"<chunk id='{i}'>\n{chunk}\n</chunk>"
            for i, chunk in enumerate(context_chunks, start=1)
        ]
    )

    prompt = f"""
You are a helpful question-answering assistant.

STRICT RULES:
1. Answer using ONLY the provided context.
2. Do not use outside knowledge.
3. Do not invent facts.
4. If the answer is not present in the context,
   reply exactly:
   I cannot find the answer in the provided documents.
5. Mention the chunk number used for your answer.

<context>
{context}
</context>

<question>
{question}
</question>

Write a clear, simple answer.
"""

    return prompt


# STEP 6: Generate answer using Gemini
def generate_answer(question):
    print("\nSearching the vector database...")

    context_chunks = retrieve_context(question)

    if not context_chunks:
        print("\nAnswer:")
        print(
            "I cannot find the answer in the provided documents."
        )
        print("\nSource: No relevant context found.")
        return

    prompt = build_prompt(question, context_chunks)

    print("Relevant chunks retrieved:", len(context_chunks))
    print("Generating answer with Gemini...")

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    answer = response.text

    if not answer:
        answer = (
            "I cannot find the answer in the provided documents."
        )

    print("\n" + "=" * 45)
    print("QUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)

    print("\nSOURCE CHUNKS:")
    for i, chunk in enumerate(context_chunks, start=1):
        print(f"\nChunk {i}:")
        print(chunk)

    print("\n" + "=" * 45)


# STEP 7: Run the RAG pipeline
if __name__ == "__main__":
    print("WEEK 3: FULL RAG PIPELINE")
    print("Type 'exit' to close the program.")

    while True:
        question = input("\nEnter your question: ").strip()

        if question.lower() == "exit":
            print("RAG Pipeline closed.")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            generate_answer(question)

        except Exception as error:
            print("\nAn error occurred:")
            print(error)
            print(
                "\nCheck your API key, model access, "
                "and Week 2 database setup."
            )

print("Week 3 RAG Pipeline Started!")

if __name__ == "__main__":
    print("Python file is working correctly.")
>>>>>>> 33beab7 (Add Week 4 AI Memory Interface project)

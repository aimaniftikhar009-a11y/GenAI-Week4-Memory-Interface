import os
from pathlib import Path

import streamlit as st
import chromadb
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY is missing. Please check your .env file.")
    st.stop()

# Gemini client
client = genai.Client(api_key=API_KEY)

# Configuration
EMBEDDING_MODEL = "gemini-embedding-2"
CHAT_MODEL = CHAT_MODEL = "gemini-3.8-flash"

DB_PATH = Path("chroma_db")

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Document Assistant")
st.caption("Ask questions about your documents. I can remember our conversation.")

# Initialize chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Connect to the existing ChromaDB database
@st.cache_resource
def get_collection():
    db_client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        return db_client.get_collection(name="document_chunks")
    except Exception:
        return None

collection = get_collection()


def retrieve_context(question):
    if collection is None:
        return "No document collection was found. Please build the vector database first."

    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question
        )

        embedding = result.embeddings[0].values

        search_result = collection.query(
            query_embeddings=[embedding],
            n_results=3
        )

        documents = search_result.get("documents", [[]])[0]

        if not documents:
            return "No relevant document information was found."

        return "\n\n".join(documents)

    except Exception as error:
        return f"Document search failed: {error}"


def generate_answer(question):
    context = retrieve_context(question)

    # Include recent conversation history for conversational memory
    history = []
    for message in st.session_state.messages[-10:]:
        role = "User" if message["role"] == "user" else "Assistant"
        history.append(f"{role}: {message['content']}")

    conversation = "\n".join(history)

    prompt = f"""
You are a helpful AI document assistant.

Answer the user's question using the document context when relevant.
Use the conversation history to understand follow-up questions.
If the answer is not available in the document, clearly say so.
Do not invent facts.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{conversation}

CURRENT QUESTION:
{question}

Give a clear, simple answer.
"""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt
    )

    return response.text or "Sorry, I could not generate an answer."


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Chat input
question = st.chat_input("Ask a question about your documents...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                answer = generate_answer(question)
                st.markdown(answer)
            except Exception as error:
                answer = f"An error occurred: {error}"
                st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
import dotenv
import os
import streamlit as st
from langchain_openai import ChatOpenAI 
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# vecstore path
CHROMA_PATH = "vectorstore_db"

# load dotenv
dotenv.load_dotenv()

# Load .env file if not running in Streamlit Cloud
if  st.secrets:
    openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
else:   
    openai_api_key = os.getenv("OPENAI_API_KEY")

##### ===== LLM ===== #####
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key = openai_api_key)

#### ===== VectorStore ===== #####
vectorstore_chroma = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=OpenAIEmbeddings(openai_api_key = openai_api_key ),
)

#### ==== Document Retriever ===== ####
retriever = vectorstore_chroma.as_retriever(k=3)
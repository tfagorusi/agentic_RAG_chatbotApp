import dotenv
import argparse
import os
import shutil
import hashlib
import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader  
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma


CHROMA_PATH = "vectorstore_db"
DATA_PATH = "data"

# load .env     
dotenv.load_dotenv()

# Load .env file if not running in Streamlit Cloud
if  st.secrets:
    openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
else:   
    openai_api_key = os.getenv("OPENAI_API_KEY")



def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--clear", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.clear:
        print("✨ Clearing Database")
        clear_database()
    else:
        # Create (or update) the data store.
        print('👉 Creating vectorstore...')
        documents = load_documents()
        chunks = split_documents(documents)     # split docs into chunks
        add_to_chroma(chunks)                      # add chunks to vectorstore


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=OpenAIEmbeddings(openai_api_key = openai_api_key)
    )

    # Calculate Page IDs and chunk hash
    chunks= calculate_chunk_ids(chunks)
   
    # Check if some documents already exist in chroma
    existing_items = db.get(include=['metadatas'])  # IDs are always included by default
    existing_ids = set([doc['id']  for doc in existing_items['metadatas']])
    existing_hashes = {doc['id']: doc['hash'] for doc in existing_items['metadatas']}
    print(f"👉 Number of existing documents in DB: {len(existing_ids)}")

    # Add or Update the documents.
    changed_chunks = []
    new_chunks = []
    # Iterate over the new chunks hashes and compare with stored data
    for chunk in chunks:
        chunk_id = chunk.metadata['id']
        chunk_hash = chunk.metadata['hash']

        # Check if the chunk exists and if the hash has changed
        if chunk_id in existing_hashes:
            if chunk_hash != existing_hashes[chunk_id]:
                # store chunk that changed
                changed_chunks.append(chunk)
        else:
            # store new chunk
            new_chunks.append(chunk)

    # add documents that don't exist in the DB.
    if len(new_chunks):
        print(f"👉 Number of new documents added to DB: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(documents=new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")

    # update DB with documents that changed.
    if len(changed_chunks):
        print(f"👉 Number of existing documents that changed: {len(changed_chunks)}")
        changed_chunk_ids = [chunk.metadata["id"] for chunk in changed_chunks]
        db.update_documents(documents=changed_chunks, ids=changed_chunk_ids)
        print("✅ Changed document(s) updated in DB sucessfully !!!")
    else:
        print("✅ No existing document changed")
        

def calculate_chunk_ids(chunks):

    # This will create IDs like "data/myPDF.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page metadata.
        chunk.metadata["id"] = chunk_id

        # generate hash each chunk: this is important because it helps keep track of changes in the chunk's content
        chunk.metadata['hash'] =  generate_hash(chunk.page_content)

    return chunks

def generate_hash(content):
    # Generate a unique hash for each chunk
    return hashlib.md5(content.encode()).hexdigest()


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("✅ Database removed!")
    else:
        print('👉 No database found!')


if __name__ == "__main__":
    main()

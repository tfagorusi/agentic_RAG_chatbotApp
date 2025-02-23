# Agentic-RAG-chatbot

This an agentic retrieval-augment generation (RAG) chatbot. It uses a retriever to obtain infromation from a database to answer questions related to football and basketball rules. For questions related to current events, the RAG agent retrieves information via a web-search tool.

## How to Use

-  Ask the chatbot questions related to football and basketball rules, and recents events.


## Look and Feel
Streamlit App: [agentic-rag-chatbot-app](https://agentic-rag-chatbot-app.streamlit.app)

![RAG chatbot app](tmp/app_ftrontend.png)

## Application Setup: Running on Local Machine
Follow the instructions below within the screen terminal:

- Clone the repository 

- Change directory into the cloned (or downloaded) **agent_RAG_Chatbot** folder
    ```
    cd <YOUR PATH>/agentic_RAG_chatbotAPP
    ```
  
- Create a virtual environment. Run the following:
    ```
    python3 -m venv venv  # create virtual environment
    source venv/bin/activate  # on Windows: venv\Scripts\activate
    python3 -m pip install --upgrade pip setuptools wheel
    ```

- Install `requirements.txt` file.
    ```
    pip install -r requirements.txt
    ```
    **Note:** For local run, comment out `pysqlite3-binary` in `requirements.txt` before pip installing the dependencies.

- Run `create_vectorstore.py` to create a vector store (or database) named **vectorstore_db**. The vectorstore is where addtional knowledge or information are retrieved to answer questions. In this scenario, the vector store has been created using some sample files in the data folder
    ```
    python create_vectorestore.py
    ```
- Add your OPENAI api key in the `secrets.toml` file contained in the **.streamlit** folder.

    ```
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    ```

- Launch the chatbot application locally:
    **Note:** Before launching the app, comment out these lines in `ragChatbot_app.py` as shown below:
  ```
  # __import__('pysqlite3')
  # import sys
  # sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
  ```
    Run app:
    ```
    streamlit run ragChatbot_app.py
    ```

## Customization: Retriever Data
- **Data Format:** You can add any file(s) of your choices into the `data` folder. Then run `create_vectorstore.py`. The format of the file(s) must be in PDF. For this project, two files have been added ("FIBA_rules_2024.pdf, FIFA_rules_21_22.pdf"). These are the files were used to create a vector store database for information retrieval. 
- **Prompt:** Update the retrieval_tool "description" (or prompt) in `src/rag_agent.py` to accomodate the new data.
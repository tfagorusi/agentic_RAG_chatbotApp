import dotenv
import os
import streamlit as st
from langchain_openai import ChatOpenAI 
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools.retriever import create_retriever_tool
from src.retriever import retriever


# load dotenv
dotenv.load_dotenv()

# Load .env file if not running in Streamlit Cloud
if  st.secrets:
    openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
else:   
    openai_api_key = os.getenv("OPENAI_API_KEY")



##### ===== LLM MODEL ===== #####
model = ChatOpenAI(model="gpt-4o-mini", temperature=0,openai_api_key=openai_api_key)

##### ===== DEFINE TOOLS ===== #####
# we'd use two tools: a search engine tool (using DuckDuckGo)and then a retriever over local index (chroma_db)
search_tool = DuckDuckGoSearchResults(
    description="""Useful for when you need to answer questions about current and/or latest events and news.
    Retrieve only relavant information. Input should be a search query.""") # DuckDuckGo search tool

retriever_tool = create_retriever_tool(
    retriever = retriever,
    name = "Rulebook",
    description = """Useful only when you need to answer questions on football and basketball game rules.
        For any questions related to football and basketball, you must use this tool!
        Don't make up any information that's not from the question and context.
        Stay within your domain football and basketball in all responses. 
        Use the entire prompt as input to the tool. For instance, if the prompt is
        "What is the rule for a handball offense in football?", the input should be
        "What is the rule for a handball offense in football?".
        Be polite in your response. If you don't know an answer, say you don't know.
        """
)

tools = [search_tool, retriever_tool]

##### ====== AGENT ====== #####
system_message="""You are a helpful assistant that use tools answer user questions. If you retrieve any document, explain the tools used to retrieve 
the documents and the steps taken to come up with a final response. Be polite in your response.
For instance, if a tool was used to retrieve documents, include these responses in your output:
{"answer": This field to give a detailed response to the question asked based retrieved documents. 
"intermediate_steps": This is a field to explain how you arrived at your answer and the information sources, relevant sections and page numbers in a professional manner}
If a question is not directly related to context, do not retrieve anything"""
rag_agentExecutor = create_react_agent(model, tools,state_modifier=system_message,checkpointer = MemorySaver())

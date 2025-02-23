__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import streamlit as st
import json
from src.rag_agent import rag_agentExecutor


with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This an agentic retrieval-augment generation (RAG) chatbot.
        It uses a retriever to obtain inormation from a database to answer questions about the football 
        and basketball rules. For questions related to current events,
        the RAG agent retrieves information via a web-search tool.
        """
    )

    st.header("Example Questions")
    st.markdown("- What is the current weather in New York?")
    st.markdown("- How many substitutions are allowed in a football match under standard FIFA regulations?")
    st.markdown("- What constitutes a direct free kick in football, and where can it be taken from?")
    st.markdown("- What is the rule for a handball offense in football?")
    st.markdown("- Under what circumstances can a goalkeeper handle the ball outside the penalty area?")
    st.markdown("- What is the shot clock in basketball, and what happens if a team fails to attempt a shot within that time?")
    st.markdown("- How many personal fouls does it take for a player to be disqualified from a basketball game?")
    st.markdown("- What is the rule for traveling in basketball, and how is it penalized?")
    st.markdown("- How is a three-point shot determined in football?")
    st.markdown("- What is APPLE's stock price?")

st.title(" Agentic RAG Chatbot")
st.info(
    "Ask me questions about football, basketball game rules and current events !"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message.keys():
            st.markdown(message["content"])
        
        if "agent_mode" in message.keys():
            with st.status("Agent mode", state="complete"):
                st.info(message["agent_mode"])

        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])

# Accept user input
if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Searching for an answer..."):
        response = rag_agentExecutor.invoke(
            {"messages": [("human", prompt)]},
            config = {"configurable": {"thread_id": "test-thread"}},
            )['messages']
        
        # format the context to show
        try:
            if len(response):
                    content = response[-1].content

                    if response[-2].name == "Rulebook":
                        # Parse string to dictionary
                        data = json.loads(content)
                        context = data.get("intermediate_steps")
                        mode = 'Retrieval'
                        answer = data.get("answer")
                    elif response[-2].name == "duckduckgo_results_json":
                        # Parse string to dictionary
                        data = json.loads(content)
                        context = data.get("intermediate_steps")
                        mode = 'Web-search'
                        answer = data.get("answer")
                    else:
                        context = ''
                        mode = 'Chat-model'
                        answer = content

            response = {'input': prompt,'intermediate_steps':context, 'output':answer, 'agent_mode':mode}

            output_text = response['output']
            explanation =response['intermediate_steps']
            agent_mode =  response['agent_mode']
        except Exception as e:
            output_text = """An error occurred while processing your message.
            Please try again or rephrase your message."""
            explanation = output_text
            agent_mode  = output_text


    st.chat_message("assistant").markdown(output_text)
    st.status("Agent mode", state="complete").info(agent_mode)
    st.status("How was this generated", state="complete").info(explanation)
    

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": output_text,
            "agent_mode": agent_mode,
            "explanation": explanation,
        }
    )
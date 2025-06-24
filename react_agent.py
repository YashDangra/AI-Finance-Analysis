# react_agent.py
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools import get_tools
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.chat_models import ChatOpenAI 
import numpy as np



load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Instantiate LangChain-compatible OpenAI model
client = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)


def run_react_agent(ticker: str, query: str, openai_api_key: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9, openai_api_key=openai_api_key)

    tools = get_tools(llm)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True  
    )

    # Provide ticker as input to the tool
    return agent.invoke(query + f" The company ticker is {ticker}.")

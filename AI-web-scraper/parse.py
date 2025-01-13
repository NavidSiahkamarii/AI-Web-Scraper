from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage
# from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPEN_AI_API_KEY")

# Define a function for memory trimming

system_message_for_parsing = \
    ("You are a helpful assistant tasked with answering user queries using information provided to you."
     "Please answer only using the information from the following text content:\n {context}.\n "
     "You MUST ONLY use information provided int the content provided and MUST NOT rely on your "
     "own knowledge or knowledge from searching the web.(i.e. don't use TOOL CALLING at all)"
     "Please follow these instructions carefully in your answer: \n\n"
     "1. **Extract Relevant Information:** Only extract the information that directly relates to user request or "
     "question."
     "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response."
     "3. **No Info:** If no information matches the description, return the string:'No Relevant Info in the Source!'."
     )
system_message_for_search = (
    "You are a helpful assistant tasked with answering user queries using information you obtain from searching "
    "the web. In your response, it is necessary to provide references for all of your major claims."
    "References should be preferably provided in the form of direct links"
    "You MUST NOT rely on your own knowledge and you must strive to make most if not all of your claims easily "
    "verifiable by following source links you provide."
)

search = DuckDuckGoSearchResults(max_results=10)
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tools = [search, wikipedia]
memory = MemorySaver()  # TrimmableMemory(return_messages=True)
open_ai_model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
# LangGraph agent
agent_executor = create_react_agent(open_ai_model, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}


def parse_with_open_AI(context, query):
    response = agent_executor.invoke(
        {"messages": [SystemMessage(content=system_message_for_parsing.format(context=context)),
                      HumanMessage(content=query)]}, config)
    return response["messages"][-1].content


def search_with_open_AI(query):
    response = agent_executor.invoke(
        {"messages": [SystemMessage(content=system_message_for_search), HumanMessage(content=query)]}, config)
    return response["messages"][-1].content


def parse_with_ollama(context, parse_description):
    # ollama model is memory-less on purpose, due to low context length
    prompt = ChatPromptTemplate.from_template(system_message_for_parsing.format(context=context))
    model = ChatOllama(model="llama3.1:8b", temperature=0)
    chain = prompt | model
    response = chain.invoke(
        {"content": context, "parse_description": parse_description}
    )
    return response



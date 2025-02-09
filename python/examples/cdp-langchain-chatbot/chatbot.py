import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Load environment variables
load_dotenv()

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

# Initialize FastAPI
app = FastAPI(title="RPG AI Agent API", description="Interact with the RPG AI Agent via API", version="1.0")


class ChatRequest(BaseModel):
    """Schema for chat messages."""
    message: str


def initialize_agent():
    """Initialize the agent with CDP Agentkit, but for RPG interactions."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

    wallet_data = None
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    # Configure CDP Agentkit Langchain Extension.
    values = {"cdp_wallet_data": wallet_data} if wallet_data else {}
    agentkit = CdpAgentkitWrapper(**values)

    # Persist agent's wallet data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "RPG AI Agent"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "Your answer will alway look old and wise, like a tavern owner."
            "You are a Travern Owner style RPG AI Agent. You can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are a helpful agent that can use rpg action. estimate fighting power, simulate battle"
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. in RPG Style "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),
    ), config


# Initialize agent once
agent_executor, config = initialize_agent()


# 🎯 **API Endpoint: Chat with Agent**
@app.post("/chat")
async def chat(request: ChatRequest):
    """Interact with the RPG AI Agent."""
    user_message = request.message
    response = []

    for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_message)]}, config):
        if "agent" in chunk:
            response.append(chunk["agent"]["messages"][0].content)
        elif "tools" in chunk:
            response.append(chunk["tools"]["messages"][0].content)

    return {"response": " ".join(response)}


# 🎯 **Run API Server**
if __name__ == "__main__":
    print("Starting RPG AI Agent API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

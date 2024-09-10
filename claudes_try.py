from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema.messages import BaseMessage
from typing import List, Generator

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model with streaming enabled
model = ChatOpenAI(
    model="gpt-4",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

chat_history: List[BaseMessage] = []

# Set an initial system message (optional)
system_message = SystemMessage(content="You are a helpful AI assistant.")
chat_history.append(system_message)

def stream_response(messages: List[BaseMessage]) -> Generator[str, None, None]:
    for chunk in model.stream(messages):
        yield chunk.content

# Chat loop
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=query))

    print("AI: ", end="", flush=True)
    full_response = ""
    for chunk in stream_response(chat_history):
        print(chunk, end="", flush=True)
        full_response += chunk
    print()  # New line after full response

    chat_history.append(AIMessage(content=full_response))

print("\n---- Message History ----")
for message in chat_history:
    print(f"{type(message).__name__}: {message.content}")
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler

# Load environment variables from .env
load_dotenv()

# Define a custom callback handler to capture streamed tokens
class SSECallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs):
        print(f"AI: {token}", end='', flush=True)  # Simulate SSE-like streaming

# Create a ChatOpenAI model with streaming enabled
model = ChatOpenAI(model="gpt-4", stream=True)  # Enable streaming

# Create a list to store messages
chat_history = []

# Add a system message (optional)
system_message = SystemMessage(content="You are a helpful AI assistant.")
chat_history.append(system_message)  # Add system message to chat history

# Chat loop
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=query))  # Add human message

    # Get AI response using history with streaming callback
    print("AI: ", end="", flush=True)  # Print "AI:" before streaming begins
    result = model.invoke(chat_history, callbacks=[SSECallbackHandler()])  # Pass the callback handler for streaming

    # Add the full AI message to the chat history once complete
    chat_history.append(AIMessage(content=result.content))  # Add the final response

print("\n---- Message History ----")
for message in chat_history:
    print(message)

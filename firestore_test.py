from dotenv import load_dotenv
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()

# # Setup Firebase Firestore
# PROJECT_ID = "langchain-crash-course-6503c"
# SESSION_ID = "user_session_new"  # This could be a username or a unique ID
# COLLECTION_NAME = "chat_history"

PROJECT_ID = "middleware-85dd0"
COLLECTION_NAME = "chat_history"
SESSION_ID = "user_session_new"

# Initialize Firestore Client
print("Initializing Firestore Client...")
client = firestore.Client(project=PROJECT_ID)
print(client)

# Initialize Firestore Chat Message History
print("Initializing Firestore Chat Message History...")
chat_history = FirestoreChatMessageHistory(
    session_id=SESSION_ID,
    collection=COLLECTION_NAME,
    client=client)

print("Chat History Initialized.")
print("Current Chat History:", chat_history.messages)


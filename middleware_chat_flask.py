from flask import Flask, request, Response, jsonify
from vapi import VapiPayload, VapiWebhookEnum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json

app = Flask(__name__)
load_dotenv()

model = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.7)
conversation_histories = {}

SYSTEM_PROMPT = """You're Andrew, an AI assistant who can help users with any questions they have. 
Provide concise, relevant answers without repeating previous information unless explicitly asked."""

def get_or_create_conversation(call_id):
    """
    Get an existing conversation history or create a new one if it doesn't exist.

    Args:
        call_id (str): The unique identifier for the call.

    Returns:
        list: The conversation history for the given call_id.
    """
    if call_id not in conversation_histories:
        conversation_histories[call_id] = [SystemMessage(content=SYSTEM_PROMPT)]
    return conversation_histories[call_id]

@app.route('/middleware', methods=['POST'])
def middleware():
    """
    Handle incoming webhook events from the Vapi service.

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code.
    """
    try:
        payload = request.get_json()['message']
        handlers = {
            VapiWebhookEnum.FUNCTION_CALL.value: function_call_handler,
            VapiWebhookEnum.STATUS_UPDATE.value: status_update_handler,
            VapiWebhookEnum.ASSISTANT_REQUEST.value: assistant_request_handler,
            VapiWebhookEnum.END_OF_CALL_REPORT.value: end_of_call_report_handler,
            VapiWebhookEnum.SPEECH_UPDATE.value: speech_update_handler,
            VapiWebhookEnum.CONVERSATION_UPDATE.value: conversation_update_handler,
            VapiWebhookEnum.TRANSCRIPT.value: transcript_handler,
            VapiWebhookEnum.HANG.value: hang_event_handler
        }
        handler = handlers.get(payload['type'])
        if not handler:
            raise ValueError('Unhandled message type')
        response = handler(payload)
        return jsonify(response), 200 if payload['type'] != VapiWebhookEnum.ASSISTANT_REQUEST.value else 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    """
    Handle chat completion requests.

    Returns:
        Response: A streaming response containing the AI's generated text.
    """
    data = request.get_json()
    messages = data.get("messages", [])
    call_id = data.get("call_id")
    
    history = get_or_create_conversation(call_id)
    
    if messages and messages[-1]["role"] == "user":
        history.append(HumanMessage(content=messages[-1]["content"]))
    
    return Response(generate_response(call_id), content_type='text/event-stream')

def generate_response(call_id):
    """
    Generate a streaming response from the AI model.

    Args:
        call_id (str): The unique identifier for the call.

    Yields:
        str: Chunks of the AI's response in the SSE format.
    """
    history = conversation_histories[call_id]
    full_response = ""

    for chunk in model.stream(history):
        if chunk.content:
            full_response += chunk.content
            yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk.content, 'role': 'assistant'}}]})}\n\n"

    conversation_histories[call_id].append(AIMessage(content=full_response))
    yield "data: [DONE]\n\n"

def assistant_request_handler(payload):
    """
    Handle assistant request events.

    Args:
        payload (dict): The payload containing the assistant request details.

    Returns:
        dict: The assistant configuration.

    Raises:
        ValueError: If the payload does not contain valid call details.
    """
    if 'call' not in payload:
        raise ValueError('Invalid call details provided.')
    
    call_id = payload['call']['id']
    get_or_create_conversation(call_id)
    
    return {
        'assistant': {
            "name": "Andrew",
            "model": {
                "provider": "custom-llm",
                "model": "not specified",
                "url": "https://b878-24-96-15-35.ngrok-free.app/",
                "temperature": 0.7,
                "systemPrompt": SYSTEM_PROMPT
            },
            "voice": {
                "provider": "azure",
                "voiceId": "andrew",
                "speed": 1
            },
            "firstMessage": "Hi, I'm Andrew. I'm on a flask server right now. How can I help you today?",
            "recordingEnabled": True
        }
    }

def function_call_handler(payload):
    """
    Handle function call events.

    Args:
        payload (dict): The payload containing the function call details.

    Returns:
        None

    Raises:
        ValueError: If the function call details are invalid.
    """
    function_call = payload.get('functionCall')
    if not function_call:
        raise ValueError("Invalid Request.")
    # Implement function call logic here
    return None

def status_update_handler(payload):
    """
    Handle status update events.

    Args:
        payload (dict): The payload containing the status update details.

    Returns:
        None
    """
    # Implement status update logic here
    return None

def end_of_call_report_handler(payload):
    """
    Handle end of call report events.

    Args:
        payload (dict): The payload containing the end of call report details.

    Returns:
        None
    """
    # Implement end of call report logic here
    return None

def speech_update_handler(payload):
    """
    Handle speech update events.

    Args:
        payload (dict): The payload containing the speech update details.

    Returns:
        None
    """
    # Implement speech update logic here
    return None

def conversation_update_handler(payload):
    """
    Handle conversation update events.

    Args:
        payload (dict): The payload containing the conversation update details.

    Returns:
        None
    """
    # Implement conversation update logic here
    return None

def transcript_handler(payload):
    """
    Handle transcript events.

    Args:
        payload (dict): The payload containing the transcript details.

    Returns:
        None
    """
    # Implement transcript handling logic here
    return None

def hang_event_handler(payload):
    """
    Handle hang event (end of call) and clean up the conversation history.

    Args:
        payload (dict): The payload containing the hang event details.

    Returns:
        None
    """
    call_id = payload['call']['id']
    if call_id in conversation_histories:
        del conversation_histories[call_id]
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
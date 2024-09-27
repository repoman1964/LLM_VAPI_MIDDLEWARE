from quart import Quart, request, Response, jsonify
from vapi import VapiPayload, VapiWebhookEnum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json
import asyncio

app = Quart(__name__)
load_dotenv()

model = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.7)
conversation_histories = {}

SYSTEM_PROMPT = """You're Andrew, an AI assistant who can help users with any questions they have. 
Provide concise, relevant answers without repeating previous information unless explicitly asked."""

def get_or_create_conversation(call_id):
    if call_id not in conversation_histories:
        conversation_histories[call_id] = [SystemMessage(content=SYSTEM_PROMPT)]
    return conversation_histories[call_id]

@app.route('/middleware', methods=['POST'])
async def middleware():
    try:
        payload = (await request.get_json())['message']
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
        response = await handler(payload)
        return jsonify(response), 200 if payload['type'] != VapiWebhookEnum.ASSISTANT_REQUEST.value else 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/completions', methods=['POST'])
async def chat_completions():
    data = await request.get_json()
    messages = data.get("messages", [])
    call_id = data.get("call_id")
    
    history = get_or_create_conversation(call_id)
    
    if messages and messages[-1]["role"] == "user":
        history.append(HumanMessage(content=messages[-1]["content"]))
    
    return Response(generate_response(call_id), content_type='text/event-stream')

async def generate_response(call_id):
    history = conversation_histories[call_id]
    full_response = ""

    def process_chunk(chunk):
        nonlocal full_response
        if chunk.content:
            full_response += chunk.content
            return f"data: {json.dumps({'choices': [{'delta': {'content': chunk.content, 'role': 'assistant'}}]})}\n\n"
        return None

    for chunk in model.stream(history):
        result = process_chunk(chunk)
        if result:
            yield result
        await asyncio.sleep(0)  # Allow other tasks to run

    conversation_histories[call_id].append(AIMessage(content=full_response))
    yield "data: [DONE]\n\n"

async def assistant_request_handler(payload):
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
            "firstMessage": "Hi, I'm Andrew. I'm now running on a Quart server. How can I assist you today?",
            "recordingEnabled": True
        }
    }

async def function_call_handler(payload):
    function_call = payload.get('functionCall')
    if not function_call:
        raise ValueError("Invalid Request.")
    # Implement function call logic here
    return None

async def status_update_handler(payload):
    # Implement status update logic here
    return None

async def end_of_call_report_handler(payload):
    # Implement end of call report logic here
    return None

async def speech_update_handler(payload):
    # Implement speech update logic here
    return None

async def conversation_update_handler(payload):
    # Implement conversation update logic here
    return None

async def transcript_handler(payload):
    # Implement transcript handling logic here
    return None

async def hang_event_handler(payload):
    call_id = payload['call']['id']
    if call_id in conversation_histories:
        del conversation_histories[call_id]
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
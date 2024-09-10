import os
from flask import Flask, Blueprint, request, Response, json, jsonify
import requests
import time
import sqlite3

from flask import Blueprint,request, jsonify, Response
from app.types.vapi import VapiPayload, VapiWebhookEnum

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json, time

app = Flask(__name__)

middleware_bp = Blueprint('middleware_api', __name__)

# Load environment variables from .env
load_dotenv()

# ENDPOINTS

@middleware_bp.route('/middleware', methods=['POST'])
async def middleware():
    try:
        req_body = request.get_json()
        payload: VapiPayload = req_body['message']
        print(payload['type'])
        print(VapiWebhookEnum.ASSISTANT_REQUEST.value)
        
        if payload['type'] == VapiWebhookEnum.FUNCTION_CALL.value:
            response = await function_call_handler(payload)
            return jsonify(response), 200
        elif payload['type'] == VapiWebhookEnum.STATUS_UPDATE.value:
            response = await status_update_handler(payload)
            return jsonify(response), 200
        elif payload['type'] == VapiWebhookEnum.ASSISTANT_REQUEST.value:
            response = await assistant_request_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.END_OF_CALL_REPORT.value:
            await end_of_call_report_handler(payload)
            return jsonify({}), 200
        elif payload['type'] == VapiWebhookEnum.SPEECH_UPDATE.value:
            response = await speech_update_handler(payload)
            return jsonify(response), 200
        elif payload['type'] == VapiWebhookEnum.CONVERSATION_UPDATE.value:
            response = await conversation_update_handler(payload)
            return jsonify(response), 200
        elif payload['type'] == VapiWebhookEnum.TRANSCRIPT.value:
            response = await transcript_handler(payload)
            return jsonify(response), 200
        elif payload['type'] == VapiWebhookEnum.HANG.value:
            response = await hang_event_handler(payload)
            return jsonify(response), 200
        else:
            raise ValueError('Unhandled message type')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# this is the server url set in the assistant_config. vapi sends to that endpoint + "/chat/completions"    
@middleware_bp.route('/chat/completions', methods=['POST'])
async def chat_completions():
    user_message_content = request.json.get('query', "Tell me about AI in 25 words.")

    # Get the 'messages' array from the JSON object
    messages = request.json.get("messages", [])

    # Find the most recent message where role is 'user'
    user_message_content = None
    for message in messages:
        if message.get("role") == "user":
            user_message_content = message.get("content")

    # testing
    # user_message_content = "Tell me about AI in 25 words."
    
    print(user_message_content)

    return Response(generate_response(user_message_content), content_type='text/event-stream')

# HANDLERS

def generate_response(query):
    # Create a ChatOpenAI model with streaming enabled
    model = ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        temperature=0.7
    )

    # Create a human message
    human_message = HumanMessage(content=query)

    # Stream the response
    for chunk in model.stream([human_message]):
        if chunk.content:
            json_data = json.dumps({
                'choices': [
                    {
                        'delta': {
                            'content': chunk.content + ' ',
                            'role': 'assistant'
                        }
                    }
                ]
            })
            yield f"data: {json_data}\n\n"
    yield "data: [DONE]\n\n"
          


  
async def function_call_handler(payload):
    """
    Handle Business logic here.
    You can handle function calls here. The payload will have function name and parameters.
    You can trigger the appropriate function based on your requirements and configurations.
    You can also have a set of validators along with each function which can be used to first validate the parameters and then call the functions.
    Here Assumption is that the functions are handling the fallback cases as well. They should return the appropriate response in case of any error.
    """

    function_call = payload.get('functionCall')

    if not function_call:
        raise ValueError("Invalid Request.")

    name = function_call.get('name')
    parameters = function_call.get('parameters')
  
    return None

async def status_update_handler(payload):
    """
    Handle Business logic here.
    Sent during a call whenever the status of the call has changed.
    Possible statuses are: "queued","ringing","in-progress","forwarding","ended".
    You can have certain logic or handlers based on the call status.
    You can also store the information in your database. For example whenever the call gets forwarded.
    """
    return None

async def end_of_call_report_handler(payload):
    """
    Handle Business logic here.
    You can store the information like summary, typescript, recordingUrl or even the full messages list in the database.
    """
    return None

async def speech_update_handler(payload):
    """
    Handle Business logic here.
    Sent during a speech status update during the call. It also lets u know who is speaking.
    You can enable this by passing "speech-update" in the serverMessages array while creating the assistant.
    """
    return None

async def conversation_update_handler(payload):
    """
    Handle Business logic here.
    Sent when an update is committed to the conversation history.
    You can enable this by passing "conversation_update-update" in the serverMessages array while creating the assistant.
    """
    return None

async def transcript_handler(payload):
    """
    Handle Business logic here.
    Sent during a call whenever the transcript is available for certain chunk in the stream.
    You can store the transcript in your database or have some other business logic.
    """
    return None

async def hang_event_handler(payload):
    """
    Handle Business logic here.
    Sent once the call is terminated by user.
    You can update the database or have some followup actions or workflow triggered.
    """
    return None 

async def assistant_request_handler(payload):
    """
    Handle Business logic here.
    You can fetch your database to see if there is an existing assistant associated with this call. If yes, return the assistant.
    You can also fetch some params from your database to create the assistant and return it.
    You can have various predefined static assistant here and return them based on the call details.
    """

    if payload and 'call' in payload:
        assistant_config = {
            "name": "Andrew",
            "model": {
                "provider": "custom-llm",
                "model": "ohwaa tagoo siam",
                "url": "https://760b-24-96-15-35.ngrok-free.app/api/",
                "temperature": 0.7,
                "systemPrompt": "You're Andrew, an AI assistant who can help user draft beautiful emails to their clients based on the user requirements."
            },
            "voice": {
                "provider": "azure",
                "voiceId": "andrew",
                "speed": 1
            },
            "firstMessage": "Hi, I'm Paula, your personal email assistant.",
            "recordingEnabled": True
        }
        return {'assistant': assistant_config}

    raise ValueError('Invalid call details provided.')



        
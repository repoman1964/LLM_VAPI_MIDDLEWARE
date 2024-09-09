from flask import Blueprint,request, jsonify, abort
from app.types.vapi import VapiPayload, VapiWebhookEnum, Assistant

middleware_bp = Blueprint('middleware_api', __name__)

@middleware_bp.route('/middleware', methods=['POST'])
async def middleware():
    try:
        req_body = request.get_json()
        payload: VapiPayload = req_body['message']
        print(payload['type'])
        print(VapiWebhookEnum.ASSISTANT_REQUEST.value)

        
        if payload['type'] == VapiWebhookEnum.FUNCTION_CALL.value:
            response = await function_call_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.STATUS_UPDATE.value:
            response = await status_update_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.ASSISTANT_REQUEST.value:
            response = await assistant_request_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.END_OF_CALL_REPORT.value:
            await end_of_call_report_handler(payload)
            return jsonify({}), 201
        elif payload['type'] == VapiWebhookEnum.SPEECH_UPDATE.value:
            response = await speech_update_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.TRANSCRIPT.value:
            response = await transcript_handler(payload)
            return jsonify(response), 201
        elif payload['type'] == VapiWebhookEnum.HANG.value:
            response = await hang_event_handler(payload)
            return jsonify(response), 201
        else:
            raise ValueError('Unhandled message type')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


        
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
        assistant = {
            'name': 'Paula',
            'model': {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'systemPrompt': "You're Paula, an AI assistant who can help user draft beautiful emails to their clients based on the user requirements. Then Call sendEmail function to actually send the email.",
                'functions': [
                    {
                        'name': 'sendEmail',
                        'description': 'Send email to the given email address and with the given content.',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'email': {
                                    'type': 'string',
                                    'description': 'Email to which we want to send the content.'
                                },
                                'content': {
                                    'type': 'string',
                                    'description': 'Actual Content of the email to be sent.'
                                }
                            },
                            'required': ['email']
                        }
                    }
                ]
            },
            'voice': {
                'provider': '11labs',
                'voiceId': 'paula'
            },
            'firstMessage': "Hi, I'm Paula, your personal email assistant."
        }
        return {'assistant': assistant}

    raise ValueError('Invalid call details provided.')



        
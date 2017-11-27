# Based off https://github.com/ModusCreateOrg/alexa-skill-demo/blob/master/lambda_function.py
#import urllib2
#import json


def lambda_handler(event, context):
    '''
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.echo-sdk-ams.app.bd304b90-xxxx-xxxx-xxxx-xxxxd4772bab"):
        raise ValueError("Invalid Application ID")
    '''
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_session_started(session_started_request, session):
    print
    "Starting new session."


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetAppointments":
        return get_appointment()
    elif intent_name == "GetMedication":
        return get_medication()
    elif intent_name == "GetFood":
        return get_food()
    elif intent_name == "GetAll":
        return get_all()
    elif intent_name == "GetHelp":
        return get_help()
    elif intent_name == "GetPledge":
        return get_pledge()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print
    "Ending session."
    # Cleanup goes here...


def handle_session_end_request():
    card_title = "Baby Bot - Thanks"
    speech_output = "Thank you for using the Baby Bot skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "BABY BOT"
    speech_output = "Welcome to the Alexa Baby Bot skill. " \
                    "You can ask me for your appointments, or " \
                    "ask me for your medications, or " \
                    "ask me for what you should eat, or " \
                    "talk to me, or " \
                    "ask me for help."
    reprompt_text = "Please talk to me."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }


def get_appointment():
    session_attributes = {}
    card_title = "Get Appointments"
    reprompt_text = ""
    should_end_session = True

    speech_output = "You have 1 appointment.  Dental Checkup. On: Sat, 13 Jan 2018, 2:10 PM. With: Dr Chin at: TTSH."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_medication():
    session_attributes = {}
    card_title = "Get Medications"
    reprompt_text = ""
    should_end_session = True

    speech_output = "You have 2 medications to take.  Medication 1:. 1 tablet Panadol after meal. do not eat before meal. Medication 2:. 2 tablets Lasix at 03:10 PM."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_food():
    session_attributes = {}
    card_title = "Get Food"
    reprompt_text = ""
    should_end_session = True

    speech_output = "Please eat Breakfast everyday"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_all():
    session_attributes = {}
    card_title = "Get All"
    reprompt_text = ""
    should_end_session = True

    speech_output = "You have 1 appointment.  Dental Checkup. On: Sat, 13 Jan 2018, 2:10 PM. With: Dr Chin at: TTSH. " \
                    "You have 2 medications to take.  Medication 1:. 1 tablet Panadol after meal. do not eat before meal. Medication 2:. 2 tablets Lasix at 03:10 PM. " \
                    "Please eat Breakfast everyday."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_help():
    session_attributes = {}
    card_title = "Get Help"
    reprompt_text = "Do you need an ambulance?"
    should_end_session = True

    speech_output = "Help is on the way"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_pledge():
    session_attributes = {}
    card_title = "Get Pledge"
    reprompt_text = ""
    should_end_session = True

    speech_output = "I’m so glad you asked. Do you know that you have received well wishes from the community through the Silver Bow pledge campaign? " \
                    "Today, James would like to send you a message to thank you for contributing to build Singapore into what it is today."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

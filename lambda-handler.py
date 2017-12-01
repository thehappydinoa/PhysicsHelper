#!/usr/bin/python2
import re

definitions = {
    # Concept : [Definition, Example] ("": ["", ""],)
    "": ["", ""]
}


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    cleanr = re.compile('<.*?>')
    cardContent = re.sub(cleanr, '', output).title()
    print("OUTPUT: " + cardContent)
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': cardContent
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "<speak>Welcome to the Physics Helper Alexa Skill, Ask me a question like: What are limits?</speak>"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = "<speak>Ask me a question like: What are limits?</speak>"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "<speak>Good bye</speak>"
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def notFound(concept):
    card_title = "Error"
    if not concept or concept == "" or concept == "":
        speech_output = "<speak>I could not find that one. Can I help you with anything else?</speak>"
    else:
        speech_output = "<speak>I could not find <emphasis level=\"moderate\">%s</emphasis>. Can I help you with anything else?</speak>" % concept
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


def conceptIntent(intent_request):
    try:
        concept = intent_request['intent']['slots']['concept']['value']
    except Exception as e:
        print(str(e))
        return notFound(None)
    try:
        card_title = "Info"
        speech_output = "<speak>%s An example would be <emphasis level=\"moderate\">%s</emphasis>. Can I help you with anything else?</speak>" % (
            definitions[concept][0], definitions[concept][1])
        should_end_session = False
        return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    except Exception as e:
        print(str(e))
        return notFound(concept)
    return notFound(None)


def definitionIntent(intent_request):
    try:
        concept = intent_request['intent']['slots']['concept']['value']
    except Exception as e:
        print(str(e))
        return notFound(None)
    try:
        card_title = "Info"
        speech_output = "<speak>%s. Can I help you with anything else?</speak>" % (
            definitions[concept][0])
        should_end_session = False
        return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    except Exception as e:
        print(str(e))
        return notFound(concept)
    return notFound(None)


def exampleIntent(intent_request):
    try:
        concept = intent_request['intent']['slots']['concept']['value']
    except Exception as e:
        print(str(e))
        return notFound(None)
    try:
        card_title = "Info"
        speech_output = "<speak>An example of %s would be <emphasis level=\"moderate\">%s</emphasis>. Can I help you with anything else?</speak>" % (
            concept, definitions[concept][1])
        should_end_session = False
        return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    except Exception as e:
        print(str(e))
        return notFound(concept)
    return notFound(None)


def yesIntent():
    card_title = "How can I help you?"
    speech_output = "<speak>How can I help you?</speak>"
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def on_session_started(session_started_request, session):
    print("START on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("LAUNCH on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_intent(intent_request, session):
    intent_name = intent_request['intent']['name']

    print("INTENT " + intent_name + " requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    if intent_name == "conceptIntent":
        return conceptIntent(intent_request)
    if intent_name == "definitionIntent":
        return definitionIntent(intent_request)
    if intent_name == "exampleIntent":
        return exampleIntent(intent_request)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.YesIntent":
        return yesIntent()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.NoIntent":
        return handle_session_end_request()
    else:
        #raise ValueError("Invalid intent")
        return get_help_response()


def on_session_ended(session_ended_request, session):
    print("END on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    '''
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.472f92d7-1b88-42ca-be0b-a6f7d077c38e"):
        raise ValueError("Invalid Application ID")
    '''
    
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

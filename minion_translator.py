"""
This is a simple alexa translation skill, translating from English to Minonese (the
language of the minions). It was created by Duncan Bailey and is no way affiliated with
the Disney Corporation or any enitities of that business. This is Duncan Bailey's first alexa skill
and he used the sample What's my color skill to get started (Duncan Bailey was writing this in
the third person).

Maxguv da ta Minion Translator!
"""

from __future__ import print_function
import urllib2
import urllib

def text_to_minion(text):
    """Translates english text to minion using fun translations api"""
    url = 'http://api.funtranslations.com/translate/minion.json'
    values = {'text': text }
    headers = {'X-Funtranslations-Api-Secret': 'XXXXX---->SECRET<-----XXXX'}
    data = urllib.urlencode(values)
    data = data.encode('ascii') # data should be bytes
    req = urllib2.Request(url, data, headers)
    translated_into_minion = ""
    response = urllib2.urlopen(req)
    translated_into_minion = str(response.read())
    start = translated_into_minion.find('"translated"')
    end = translated_into_minion.find('"text"')
    translated_into_minion = translated_into_minion[start+15:end-11]
    return translated_into_minion

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Minion Translator" \
                    "Please tell me a word or phrase you would like to translate" \
                    "to the Minion language" \
                    "say something like, what is cat in minion"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me a word or phrase you would like to translate to minion, " \
                    "by saying something like what is cat in minion."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Minion Translator" \
                    "Kaylay a wed dia "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_word_to_translate_attributes(word_to_translate):
    return {"word_to_translate": word_to_translate}


def translate_to_minion_in_session(intent, session):
    """ Translates text to minion and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Words' in intent['slots']:
        word_to_translate = intent['slots']['Words']['value']
        session_attributes = create_word_to_translate_attributes(word_to_translate)
        speech_output = text_to_minion(word_to_translate)
        reprompt_text = "You can ask me for a word or phrase in the minion language by saying " \
                        "what is butterfly in minion"
    else:
        speech_output = "I'm not sure what word or phrase you would like to translate" \
                        "Please try again"
        reprompt_text = "I'm not sure what word or phrase you would like to translate" \
                        "You can tell what word or phrase you would like to translate by saying" \
                        "what is butterfly in minion"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))




# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "Translate":
        return translate_to_minion_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

import logging
import os
import requests
import random
sb_url = os.environ.get('sb_url')
rootLogger = logging.getLogger(__name__)

'''
A1. I’m so glad you asked. I love to talk, and I especially love to talk with you. 
Do you know that you have received well wishes from the community through the Silver Bow pledge campaign? 
Today, <first name> would like to share <(a quote from Thich Nhat Hanh)> with you: <“Because of your smile, you make life more beautiful.”>
 
A2. I’m so glad you asked. 
Do you know that you have received well wishes from the community through the Silver Bow pledge campaign? 
Today, <first name> would like to send you a message <to thank you for contributing to build Singapore into what it is today.>
 
A3. Thanks for asking.  
I have received well wishes that the community would like to share with you through the Silver Bow pledge campaign. 
<First name> sent you this message: <“Let people see the unique, amazing and wonderful person that you are.”>

A4. Sure, would be glad to, as I love to talk, and I especially love to talk with you. 
Do you know that you have received well wishes from the community through the Silver Bow pledge campaign? 
Today, <first name> would like to share <(a quote from Adrienne Kimberley)> with you: <“No one is you, and that is your superpower.”>
'''

response_template = {
    'message_intro': ["I’m so glad you asked. I love to talk, and I especially love to talk with you.",
                      "Thanks for asking.",
                      "Sure, I would be glad to."],
    'message_leadin': ["Do you know that you have received well wishes from the community through the Silver Bow pledge campaign?",
                       "I have received well wishes that the community would like to share with you through the Silver Bow pledge campaign."],
    'message_leadout': ["Today, {username} would like to share with you: {message}.",
                        "Today, {username} would like to send you a message: {message}.",
                        "{username} sent you this message: {message}."
                        ]
}


def get_pledge_msg(msg_info):
    rootLogger.info('pledge message')
    sb_info = get_info_from_SB(msg_info)
    rootLogger.info('Get pledge complete')
    # format response
    pledge_info = {'username': sb_info['data'][0]['username'],
                   'message': sb_info['data'][0]['message']}
    randomized_message_structure = " ".join([
        random.choice(response_template['message_intro']),
        random.choice(response_template['message_leadin']),
        random.choice(response_template['message_leadout'])])
    pledge_msg = randomized_message_structure.format(**pledge_info)
    rootLogger.debug(pledge_msg)
    return pledge_msg


def get_info_from_SB(param):
    # build object to be sent. redundant?
    # data_to_send = {'Alexa_id' : param['user_id']}

    # retrieve data from SB
    rootLogger.debug('Getting info from SB')
    # Send request to SB
    # r = requests.post('http://httpbin.org/post', data = {'key':'value'})
    sb_response = requests.get(sb_url)

    # Non-200 status code handling
    try:
        sb_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return rootLogger.debug(e)
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        return rootLogger.debug(e)

    # parse return data from PICA
    # iso8601.parse_date()
    # time of the appointment
    # type of service (e.g. meal service)
    # assigned healthcare worker
    # comments (this is optional e.g. assigned careworker will be running late)
    # data_recieved = r.json()
    data_retrieved = sb_response.json()

    return data_retrieved


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

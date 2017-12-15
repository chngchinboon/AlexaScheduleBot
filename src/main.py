from datetime import datetime, timedelta
import re
import logging
import os

from flask import Flask
from flask_ask import Ask, statement, question, session, context, request, version

import src.pledgeFunc as pledgeFunc
import src.picaFunc as picaFunc

import boto3

# Program Start
app = Flask(__name__)
#ask = Ask(app, "/Babybot") # only for ngrok
ask = Ask(app, "/")

'''
# Logging format
logFormatter = logging.Formatter("%(asctime)s  [%(levelname)s] [%(name)s] %(message)s")

def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)

    h = logging.StreamHandler(sys.stdout)

    # use whatever format you want here
    h.setFormatter(logging.Formatter(logFormatter))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    return logger

rootLogger = setup_logging()
'''
rootLogger = logging.getLogger()


_DATE_PATTERNS = {
    # "today", "tomorrow", "november twenty-fifth": 2015-11-25
    '^\d{4}-\d{2}-\d{2}$': ['%Y-%m-%d', 0],
    # "this week", "next week": 2015-W48
    '^\d{4}-W\d{2}$': ['%Y-W%U-%w', 7],
    # "this weekend": 2015-W48-WE
    '^\d{4}-W\d{2}-WE$': ['%Y-W%U-WE-%w', 2],
    # "this month": 2015-11
    '^\d{4}-\d{2}$': ['%Y-%m', 30],
    # "next year": 2016
    '^\d{4}$': ['%Y', 365],
}


def parse_time_frame(time_frame):
    # assumed input is a datetime.date object from flask-ask convert
    # build a dict with two fields of isoformat start and end
    # timestart=datetime.now().isoformat()
    # timeend=timeframe.isoformat()#may need to add timedelta(1)
    # if not time_frame:
    #    time_frame = 'Today'  # default timeframe to today

    # make so 'next decade' matches work against 'next year' regex
    time_frame = re.sub('X$', '0', time_frame)
    for re_pattern, format_pattern in list(_DATE_PATTERNS.items()):
        if re.match(re_pattern, time_frame):
            if '%U' in format_pattern[0]:
                # http://stackoverflow.com/a/17087427/1163855
                time_frame += '-0'
            date_start = datetime.strptime(time_frame, format_pattern[0]).date()
            date_end = date_start + timedelta(format_pattern[1])
            date_range = {'date_start': date_start.isoformat(), 'date_end': date_end.isoformat()} # convert to format for PICA
            # date_range = {'date_start': date_start.strftime("%Y/%m/%d"), 'date_end': date_end.strftime("%Y/%m/%d")}
            return date_range
    return None


def get_msg_info():
    rootLogger.info('Grabbing msg_info')
    msg_info = {}
    # msg_info["Request ID"] = request.requestId
    # msg_info["Request Type"] = request.type
    msg_info["Request Timestamp"] = request.timestamp
    # msg_info["Session New"] = session.new
    # msg_info["User ID"] = session.user.userId
    # msg_info["Alexa Version"] = version
    msg_info["Device ID"] = context.System.device.deviceId
    rootLogger.info('Msg_info retrieved')
    rootLogger.debug(msg_info)
    return msg_info


@app.route('/')
def homepage():
    return "Welcome to Baby bot!!"


@ask.launch
def start_skill():
    welcome_message = 'Hello there! How can I help you'
    return question(welcome_message).reprompt('How can I help you today?')

@ask.intent('GetInfo')
def get_info():
    info_message = 'I am Baby Bot. I am developed by the Institute of Systems Science, National University of Singapore'
    return statement(info_message)

@ask.intent('GetAppointments')  #, convert={'TimeFrame': 'date'})
def get_appointment(TimeFrame):
    rootLogger.info('Request for appointment received')
    msg_info = get_msg_info()
    if not TimeFrame:
        TimeFrame= datetime.now().strftime('%Y-%m-%d')
    response_msg = picaFunc.get_appointment_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved appointments msg')
    return statement(response_msg).simple_card(title='Get Appointment', content = response_msg)


@ask.intent('GetMedication')
def get_medication(TimeFrame):
    rootLogger.info('Request for medication received')
    msg_info = get_msg_info()
    if not TimeFrame:
        TimeFrame= datetime.now().strftime('%Y-%m-%d')
    response_msg = picaFunc.get_medication_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved medications msg')
    return statement(response_msg).simple_card(title='Get Medication', content = response_msg)


@ask.intent('GetFood')
def get_food(TimeFrame):
    rootLogger.info('Request for food received')
    msg_info = get_msg_info()
    if not TimeFrame:
        TimeFrame= datetime.now().strftime('%Y-%m-%d')
    response_msg = picaFunc.get_food_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved food msg')
    return statement(response_msg).simple_card(title='Get Food', content = response_msg)


@ask.intent('GetAll')
def get_all(TimeFrame):
    if not TimeFrame:
        TimeFrame= datetime.now().strftime('%Y-%m-%d')
    time_frame = parse_time_frame(TimeFrame)
    rootLogger.info('Request for all info received')
    msg_info = get_msg_info()
    all_msglist = []
    all_msglist.append(picaFunc.get_appointment_msg(msg_info, time_frame))
    all_msglist.append(picaFunc.get_medication_msg(msg_info, time_frame))
    all_msglist.append(picaFunc.get_food_msg(msg_info, time_frame))

    all_msg = ' '.join(all_msglist)
    rootLogger.debug(all_msg)
    rootLogger.info('Retrieved all info msg')
    return statement(all_msg).simple_card(title='Get All', content = all_msg)


@ask.intent('GetHelp')
def get_help():
    rootLogger.info('Request for help')
    msg_info = get_msg_info()
    response_msg = picaFunc.get_help_msg(msg_info)
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved help msg')
    return statement(response_msg).simple_card(title='Get Help', content = response_msg)


@ask.intent('GetPledge')
def get_pledge():
    rootLogger.info('Request for pledge')
    msg_info = get_msg_info()
    response_msg = pledgeFunc.get_pledge_msg(msg_info)
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved pledge msg')
    usage_log(msg_info["Device ID"], 'pledge', msg_info["Request Timestamp"].strftime("%Y/%m/%d"), datetime.now().strftime("%Y/%m/%d"), 'success')
    return statement(response_msg).simple_card(title='Get Pledge', content = response_msg)


@ask.intent('AMAZON.StopIntent')
def stop_intent():
    bye_text = 'Ok... bye'
    return statement(bye_text)

def db_connect():
    return boto3.client('dynamodb', aws_access_key_id = os.environ.get('DB_ACCESS_KEY_ID'),
                            aws_secret_access_key = os.environ.get('DB_SECRET'))

def usage_log(userID, usageType, requestTimestamp, responseTimestamp, responseStatus):
    rootlogger.debug('Connecting to DB')
    dynamo = db_connect()
    item = {
        'userID': {'S':userID},
        'usageType': {'S': usageType},
        'requestTimestamp': {'S': requestTimestamp},
        'responseTimestamp': {'S': responseTimestamp},
        'responseStatus': {'S': responseStatus}
    }
    dynamo.put_item(TableName = 'usage',Item = item)
    return rootLogger.debug('Logged usage')


if __name__ == '__main__':
    rootLogger.info('Started Up')
    app.run(debug=True)  # need to change to False when pushing to production



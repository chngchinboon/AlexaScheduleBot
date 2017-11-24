import sqlite3
# import iso8601
# import pytz
from datetime import datetime, timedelta
import re
import logging
import sys

from flask import Flask
from flask_ask import Ask, statement, question, session, context, request, version
import pledgeFunc
import picaFunc

# Program Start
app = Flask(__name__)
ask = Ask(app, "/Babybot")

# Logging format
logFormatter = logging.Formatter("%(asctime)s  [%(levelname)s] [%(name)s] %(message)s")

# Setup root logger handle
rootLogger = logging.getLogger(__name__)
rootLogger.setLevel(logging.DEBUG)


class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level


def setup_logger(rootLogger, filename, formatter, level=logging.INFO,strict=True):
    """Function setup as many loggers as you want"""
    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    if strict:
        handler.addFilter(MyFilter(level))
    rootLogger.addHandler(handler)

    return handler


debugHandler = setup_logger(rootLogger, '../data/debug.log', logFormatter, level=logging.DEBUG, strict=False)
infoHandler = setup_logger(rootLogger, '../data/info.log', logFormatter, level=logging.INFO)
errorHandler = setup_logger(rootLogger, '../data/error.log', logFormatter, level=logging.ERROR)
usageHandler = setup_logger(rootLogger, '../data/usage.log', logFormatter, level=logging.CRITICAL)

# Output to console for easy debugging. To remove when i get used to proper error logging/debugging
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


_DATE_PATTERNS = {
    # "today", "tomorrow", "november twenty-fifth": 2015-11-25
    '^\d{4}-\d{2}-\d{2}$': ['%Y-%m-%d', 1],
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
            date_range = {'date_start': date_start.isoformat(), 'date_end': date_end.isoformat()}
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
    welcome_message = 'Hello there! Welcome to Baby Bot developed by NUS ISS!'
    return question(welcome_message)


@ask.intent('GetAppointments', default={'TimeFrame': 'today'})  #, convert={'TimeFrame': 'date'})
def get_appointment(TimeFrame):
    rootLogger.info('Request for appointment received')
    msg_info = get_msg_info()
    response_msg = picaFunc.get_appointment_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved appointments msg')
    return statement(response_msg)


@ask.intent('GetMedication')
def get_medication(TimeFrame):
    rootLogger.info('Request for medication received')
    msg_info = get_msg_info()
    response_msg = picaFunc.get_medication_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved medications msg')
    return statement(response_msg)


@ask.intent('GetFood')
def get_food(TimeFrame):
    rootLogger.info('Request for food received')
    msg_info = get_msg_info()
    response_msg = picaFunc.get_food_msg(msg_info, parse_time_frame(TimeFrame))
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved food msg')
    return statement(response_msg)


@ask.intent('GetAll')
def get_all(TimeFrame):
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
    return statement(all_msg)


@ask.intent('GetHelp')
def get_help():
    rootLogger.info('Request for help')
    msg_info = get_msg_info()
    response_msg = picaFunc.get_help_msg(msg_info)
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved help msg')
    return statement(response_msg)


@ask.intent('GetPledge')
def get_pledge():
    rootLogger.info('Request for pledge')
    msg_info = get_msg_info()
    response_msg = pledgeFunc.get_pledge_msg(msg_info)
    rootLogger.debug(response_msg)
    rootLogger.info('Retrieved pledge msg')
    return statement(response_msg)


@ask.intent('AMAZON.StopIntent')
def stop_intent():
    bye_text = 'Ok... bye'
    return statement(bye_text)


if __name__ == '__main__':
    rootLogger.info('Started Up')
    app.run(debug=True)  # need to change to False when pushing to production
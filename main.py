import sqlite3
# import iso8601
# import pytz

import logging
import sys

import re
import sqlite3
from datetime import datetime, timedelta

from flask import Flask
from flask_ask import Ask, statement, question, session, context, request, version

###### Program Start
app = Flask(__name__)
ask = Ask(app, "/Babybot")

# Logging format
logFormatter=logging.Formatter("%(asctime)s  [%(levelname)s] [%(name)s] %(message)s")

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

debugHandler=setup_logger(rootLogger,'data/debug.log',logFormatter,level=logging.DEBUG,strict=False)
infoHandler=setup_logger(rootLogger,'data/info.log',logFormatter,level=logging.INFO)
errorHandler=setup_logger(rootLogger,'data/error.log',logFormatter,level=logging.ERROR)
usageHandler=setup_logger(rootLogger,'data/usage.log',logFormatter,level=logging.CRITICAL)

#Output to console for easy debugging. To remove when i get used to proper error logging/debugging
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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


def parse_timeframe(timeframe):
    # assumed input is a datetime.date object from flask-ask convert
    # build a dict with two fields of isoformat start and end
    # timestart=datetime.now().isoformat()
    # timeend=timeframe.isoformat()#may need to add timedelta(1)

    # make so 'next decade' matches work against 'next year' regex
    timeframe = re.sub('X$', '0', timeframe)
    for re_pattern, format_pattern in list(_DATE_PATTERNS.items()):
        if re.match(re_pattern, timeframe):
            if '%U' in format_pattern[0]:
                # http://stackoverflow.com/a/17087427/1163855
                timeframe += '-0'
            datestart = datetime.strptime(timeframe, format_pattern[0]).date()
            dateend = datestart + timedelta(format_pattern[1])
            daterange = {'date_start': datestart.isoformat(), 'date_end': dateend.isoformat()}
            return daterange
    return None


def get_infofromdb(tablename, timeframe='Today'):
    """
    exampledate=time.localtime()
    exampledatestr=time.strftime('%a, %d %b %Y %H:%M:%S',exampledate)
    examplecomment='Dental checkup at TTSH'
    schedulelist=[{'Datetime':exampledatestr,'comments':examplecomment}]
    """
    if tablename != 'PICA':
        # get from database #to be removed
        db = sqlite3.connect('data/testdb')
        db.row_factory = dict_factory
        cursor = db.cursor()
        cursor.execute('select * from ' + tablename + ' where username = "user1"')
        infolist = cursor.fetchall()
        db.close()
        return infolist

    # retrieve data from PICA
    else:
        # build object
        data_to_send = {'daterange': parse_timeframe(timeframe),
                        'alexa_id': context.System.device.deviceId
                        }
        rootLogger.debug(data_to_send)
        # Send request to PICA
        # r = requests.post('http://httpbin.org/post', data = {'key':'value'})
        # r = RQ.post(url, json = data_to_send)

        # parse return data from PICA
        # iso8601.parse_date()
        # time of the appointment
        # type of service (e.g. meal service)
        # assigned healthcare worker
        # comments (this is optional e.g. assigned careworker will be running late)
        # data_recieved = r.json()
        data_recieved = data_to_send
        return data_recieved


def get_msg_info():
    rootLogger.info('Grabbing msg_info')
    msg_info = {}
    msg_info["Request ID"] = request.requestId
    msg_info["Request Type"] = request.type
    msg_info["Request Timestamp"] = request.timestamp
    msg_info["Session New"] = session.new
    msg_info["User ID"] = session.user.userId
    msg_info["Alexa Version"] = version
    msg_info["Device ID"] = context.System.device.deviceId
    rootLogger.info('Msg_info retrieved')
    rootLogger.debug(msg_info)
    return msg_info


def log_usage(deviceID, msg_info, usage_info):
    # store usage into a database table
    tablename = 'usage'
    db = sqlite3.connect('data/testdb')
    # db.row_factory = dict_factory
    cursor = db.cursor()

    cursor.execute('insert * into ' + tablename + ' where username = msg_info["Device ID"]')
    db.close()  # might want to try using 'with' instead.


def get_appointment_msg(timeframe):
    rootLogger.info('Getting Appointments')

    msg_info = get_msg_info()

    if not msg_info["Device ID"]:
        tablename = 'appointment'
    else:
        tablename = 'PICA'

    rootLogger.info(timeframe)
    appointmentslist = get_infofromdb(tablename, timeframe)
    '''
    id INTEGER PRIMARY KEY,
    username TEXT,
    start_date TEXT, 
    contact_person TEXT,
    location TEXT,
    purpose TEXT)    
    '''
    if appointmentslist:
        numappointments = len(appointmentslist)
        appointment_msglist = []
        if numappointments > 1:
            appointment_msglist.append('You have {} appointments. '.format(numappointments))
        else:
            appointment_msglist.append('You have 1 appointment. ')

        for idx, appointment in enumerate(appointmentslist):
            if numappointments > 1:
                appointment_msglist.append('Appointment {}:'.format(idx + 1) + '.')
            if appointment['purpose']:
                appointment_msglist.append(appointment['purpose'] + '.')
            if appointment['start_date']:
                appointment_msglist.append('On: ' + appointment['start_date'] + '.')
            if appointment['contact_person']:
                appointment_msglist.append('With: ' + appointment['contact_person'])
            if appointment['location']:
                appointment_msglist.append('at: ' + appointment['location'] + '.')

    else:
        appointment_msglist = 'You have no appointments.'

    # appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    appointment_msg = ' '.join(appointment_msglist)
    return appointment_msg


def get_medication_msg():
    rootLogger.info('Getting Medication')

    msg_info = get_msg_info()

    if not msg_info["Device ID"]:
        tablename = 'medication'
    else:
        tablename = 'PICA'

    medicationlist = get_infofromdb(tablename)
    '''
    id INTEGER PRIMARY KEY, 
    username TEXT,
    mediname TEXT, 
    dosage TEXT,
    frequency TEXT,
    comments TEXT)
    '''

    if medicationlist:
        nummedication = len(medicationlist)
        medication_msglist = []
        if nummedication > 1:
            medication_msglist.append('You have {} medications to take. '.format(nummedication))
        else:
            medication_msglist.append('You have 1 medication. ')

        for idx, medication in enumerate(medicationlist):
            if nummedication > 1:
                medication_msglist.append('Medication {}:'.format(idx + 1) + '.')
            if medication['dosage']:
                medication_msglist.append(medication['dosage'])
            if medication['mediname']:
                medication_msglist.append(medication['mediname'])
            if medication['frequency']:
                medication_msglist.append(medication['frequency'] + '.')
            if medication['comments']:
                medication_msglist.append(medication['comments'] + '.')

    else:
        medication_msglist = 'You have no medicaiton to take.'

    # appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    medication_msg = ' '.join(medication_msglist)
    rootLogger.info("Get medication complete")
    return medication_msg


def get_food_msg():
    rootLogger.info('Getting Food')

    msg_info = get_msg_info()

    if not msg_info["Device ID"]:
        tablename = 'food'
    else:
        tablename = 'PICA'

    foodlist = get_infofromdb(tablename)
    '''
    id INTEGER PRIMARY KEY, 
    username TEXT,
    foodtype TEXT, 
    frequency TEXT)
    '''
    if foodlist:
        food_msglist = []

        food_msglist.append('Please eat')

        food_msglist2 = []
        for idx, food in enumerate(foodlist):
            if food['foodtype']:
                food_msglist2.append(food['foodtype'])
            if food['frequency']:
                food_msglist2.append(food['frequency'])

        food_msglist.append(' '.join(food_msglist2))
    else:
        food_msglist = 'Eat whatever you like.'

    # appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    food_msg = ' '.join(food_msglist)
    rootLogger.info('Get food complete')
    return food_msg


@app.route('/')
def homepage():
    return "Welcome to Baby bot!!"


@ask.launch
def start_skill():
    welcome_message = 'Hello there!'
    return question(welcome_message)


@ask.intent('GetAppointments', default={'TimeFrame': 'today'})#, convert={'TimeFrame': 'date'})
def get_appointment(TimeFrame):
    rootLogger.info('Request for timeframe received')
    return statement(get_appointment_msg(TimeFrame))


@ask.intent('GetMedication')
def get_medication():
    rootLogger.info('Request for medication received')
    return statement(get_medication_msg())


@ask.intent('GetFood')
def get_food():
    rootLogger.info('Request for food received')
    return statement(get_food_msg())


@ask.intent('GetAll')
def get_all():
    rootLogger.info('Request for all info received')
    all_msglist = []
    all_msglist.append(get_appointment_msg())
    all_msglist.append(get_medication_msg())
    all_msglist.append(get_food_msg())
    all_msg = ' '.join(all_msglist)

    return statement(all_msg)


@ask.intent('AMAZON.StopIntent')
def stop_intent():
    bye_text = 'Ok... bye'
    return statement(bye_text)


if __name__ == '__main__':
    rootLogger.info('Started Up')
    app.run(debug=True)  # need to change to False when pushing to production
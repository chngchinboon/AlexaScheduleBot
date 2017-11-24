import sqlite3
import logging
rootLogger = logging.getLogger(__name__)


def get_appointment_msg(msg_info,time_frame):
    rootLogger.info('Getting Appointments')
    if not msg_info["Device ID"]:   #test database
        param = {   'db_name': 'devdb',
                    'table_name': 'appointment',
                    'time_frame': time_frame,
                    'user_id': 'user1'
                }
    else:   #setup dict for sending to api
        param = {   'db_name': 'PICA',
                    'time_frame': time_frame,
                    'user_id': msg_info["Device ID"]
                }


    #rootLogger.info(timeframe)
    appointmentslist = get_info_from_PICA(param)
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
    rootLogger.debug(appointment_msg)
    return appointment_msg


def get_medication_msg(msg_info,time_frame):
    rootLogger.info('Getting Medication')

    if not msg_info["Device ID"]:
        param = {   'db_name': 'devdb',
                    'table_name': 'medication',
                    'time_frame': time_frame,
                    'user_id': 'user1'
                }

    else:
        param = {   'db_name': 'PICA',
                    'time_frame': time_frame,
                    'user_id': msg_info["Device ID"]
                }

    medicationlist = get_info_from_PICA(param)
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
        medication_msglist = 'You have no medicatiton to take.'

    # appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    medication_msg = ' '.join(medication_msglist)
    rootLogger.info("Get medication complete")
    rootLogger.debug(medication_msg)
    return medication_msg


def get_food_msg(msg_info,time_frame):
    rootLogger.info('Getting Food')

    if not msg_info["Device ID"]:
        param = {   'db_name': 'devdb',
                    'table_name': 'food',
                    'time_frame': time_frame,
                    'user_id': 'user1'
                }

    else:
        param = {   'db_name': 'PICA',
                    'time_frame': time_frame,
                    'user_id': msg_info["Device ID"]
                }

    foodlist = get_info_from_PICA(param)
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
    rootLogger.debug(food_msg)
    return food_msg

def get_help_msg(msg_info):
    rootLogger.info('Getting help')

    help_msg = 'Contacted'

    if not msg_info["Device ID"]:
        source_msg = 'Amazon test service'
        status = True
    else:
        source_msg = 'PICA'
        status = push_info_to_PICA(msg_info["Request Timestamp"])

    if status:
        help_msg = ' '.join([help_msg,source_msg,'for help'])
        rootLogger.info('Get help complete')
    else:
        help_msg = 'Send help failed'
        #do follow up action like send sms instead.
        rootLogger.info('Get help failed')

    rootLogger.debug(help_msg)
    return help_msg

def get_info_from_PICA(param):
    """
    exampledate=time.localtime()
    exampledatestr=time.strftime('%a, %d %b %Y %H:%M:%S',exampledate)
    examplecomment='Dental checkup at TTSH'
    schedulelist=[{'Datetime':exampledatestr,'comments':examplecomment}]
    """

    if param['db_name'] == 'devdb':
        # get from database #to be removed
        db = sqlite3.connect('../data/testdb')
        db.row_factory = dict_factory
        cursor = db.cursor()
        cursor.execute('select * from ' + param['table_name'] + ' where username = "user1"')
        data_retrieved = cursor.fetchall()
        db.close()

    # retrieve data from PICA
    else:
        # build object to be sent. redundant?
        data_to_send = {    'Alexa_id' : param['user_id'],
                            'date_range' : param['time_frame']
                        }
        rootLogger.debug(data_to_send)
        # Send request to PICA
        # try:
        #    r = requests.post('http://httpbin.org/post', data = {'key':'value'})
        #    r = RQ.post(url, json = data_to_send)

        # parse return data from PICA
        # iso8601.parse_date()
        # time of the appointment
        # type of service (e.g. meal service)
        # assigned healthcare worker
        # comments (this is optional e.g. assigned careworker will be running late)
        # data_recieved = r.json()
        data_retrieved = data_to_send

    return data_retrieved

def push_info_to_PICA(param):
    # Send request to PICA
    # r = requests.post('http://httpbin.org/post', data = {'key':'value'})
    # r = RQ.post(url, json = data_to_send)

    # parse return data from PICA
    # assigned healthcare worker
    # comments (this is optional e.g. assigned careworker will be running late)

    # data_recieved = r.json()

    #data_recieved = data_to_send
    status=True
    return status


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

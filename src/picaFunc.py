# import sqlite3
# import iso8601
import logging
import os
import requests

rootLogger = logging.getLogger(__name__)
pica_url = os.environ.get('pica_url')

def get_appointment_msg(msg_info,time_frame):
    rootLogger.info('Getting Appointments')
    '''
    if not msg_info["Device ID"]:   #test database
        param = {   'db_name': 'devdb',
                    'table_name': 'appointment',
                    'time_frame': time_frame,
                    'user_id': 'user1'
                }
    '''
    # else:   #setup dict for sending to api
    param = {   'db_name': 'appt',
                'time_frame': time_frame,
                'user_id': msg_info["Device ID"]
            }
    # [{'date': '2017-12-04T00:00:00.000Z', 'time': '12:00nn', 'service_type': 'Meal Service',
      # 'assigned_careworker': '####'}]

    #rootLogger.info(timeframe)
    appointmentslist, status = get_info_from_PICA(param)

    if status=='ok':
        if appointmentslist:
            appointmentslist = [x for x in appointmentslist if x is not None]  # handling weird occasional null output from pica
            numappointments = len(appointmentslist)
            appointment_msglist = []
            # inside appointments
            # Midday meal (service type) will arrive at date/time and be provided by Careworker Name (assigned careworker)
            if numappointments > 1:
                appointment_msglist.append('You have {} appointments. '.format(numappointments))
            else:
                appointment_msglist.append('You have 1 appointment. ')

            for idx, appointment in enumerate(appointmentslist):
                if numappointments > 1:
                    appointment_msglist.append('Appointment {}:'.format(idx + 1))

                if 'appointed_person' in appointment: # handle in-house appointment
                    # Midday meal (service type) will arrive at date/time and be provided by Careworker Name (appointed_person)
                    if appointment['service_type']:
                        appointment_msglist.append(appointment['service_type'] + ' will arrive at')
                    if appointment['date']:
                        appointment_msglist.append(appointment['date'][0:10] + ',') #poor implementation! to revisit once PICA figures out what they have
                    if appointment['time']:
                        if 'nn' in appointment['time']:
                            appointment_msglist.append(appointment['time'][0:2]+' noon') #poor implementation! to revisit once PICA figures out what they have
                        else:
                            appointment_msglist.append(appointment['time'])
                    if appointment['appointed_person']:
                        appointment_msglist.append('and be provided by ' + appointment['appointed_person'] + '.')

                if 'location' in appointment: # handle out-house appointment
                    # (service_type) on date/time, at (location)
                    if appointment['service_type']:
                        appointment_msglist.append(appointment['service_type'])
                    if appointment['date']:
                        appointment_msglist.append('on ' + appointment['date'][0:10] + ',') #poor implementation! to revisit once PICA figures out what they have
                    if appointment['time']:
                        if 'nn' in appointment['time']:
                            appointment_msglist.append(appointment['time'][0:2]+' noon') #poor implementation! to revisit once PICA figures out what they have
                        else:
                            appointment_msglist.append(appointment['time'])
                    if appointment['location']:
                        appointment_msglist.append('at ' + appointment['location'] + '.')

            appointment_msg = ' '.join(appointment_msglist)

        else:
            appointment_msg = 'You have no appointments.'



    elif status == 'Connection Error':
        appointment_msg = "You have 1 appointment.  Dental Checkup. On: Sat, 13 Jan 2018, 2:10 PM. With: Dr Chin at: TTSH. "
        # appointment_msg = "Sorry we are experiencing technical difficulties retrieving data. Please check back later."
        rootLogger.error('PICA connection Error')
    elif status == 'Connection Timeout':
        appointment_msg = "You have 1 appointment.  Dental Checkup. On: Sat, 13 Jan 2018, 2:10 PM. With: Dr Chin at: TTSH. "
        # appointment_msg = "Sorry we are experiencing technical difficulties retrieving data. Please check back later."
        rootLogger.error('PICA connection Timeout')
    else:
        appointment_msg = 'Error in Appointment function'

    # appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    rootLogger.info("Get Appointment complete")
    rootLogger.debug(appointment_msg)
    return appointment_msg


def get_medication_msg(msg_info,time_frame):
    rootLogger.info('Getting Medication')
    '''
    if not msg_info["Device ID"]:
        param = {   'db_name': 'devdb',
                    'table_name': 'medication',
                    'time_frame': time_frame,
                    'user_id': 'user1'
                }
    '''
    #else:
    param = {   'db_name': 'meds',
                'time_frame': time_frame,
                'user_id': msg_info["Device ID"]
            }

    medicationlist, status = get_info_from_PICA(param)
    if status == 'ok':
        if medicationlist:
            medicationlist = [x for x in medicationlist if x is not None] #handling weird occasional null output from pica
            nummedication = len(medicationlist)
            medication_msglist = []
            if nummedication > 1:
                medication_msglist.append('You have {} medications. '.format(nummedication))
            else:
                medication_msglist.append('You have 1 medication. ')

            for idx, medication in enumerate(medicationlist):
                if nummedication > 1:
                    medication_msglist.append('Medication {}:'.format(idx + 1) + '.')
                if medication['date']:
                    medication_msglist.append('On ' + medication['date'][0:10] + ',') #poor implementation! to revisit once PICA figures out what they have
                if medication['time']:
                    if 'nn' in medication['time']:
                        medication_msglist.append('at ' + medication['time'][0:2]+' noon') #poor implementation! to revisit once PICA figures out what they have
                    else:
                        medication_msglist.append('at ' + medication['time'])
                if medication['medications']:
                    for med in medication['medications']:
                        medication_msglist.append(med + ',')

            medication_msg = ' '.join(medication_msglist)

        else:
            medication_msg = 'You have no medication to take.'


    elif status == 'Connection Error':
        medication_msg = "You have 2 medications to take.  Medication 1:. 1 tablet Panadol after meal. do not eat before meal. Medication 2:. 2 tablets Lasix at 03:10 PM."
        # medication_msg = "Sorry we are experiencing technical difficulties retrieving data. Please check back later."
        rootLogger.error('PICA connection Error')
    elif status == 'Connection Timeout':
        medication_msg = "You have 2 medications to take.  Medication 1:. 1 tablet Panadol after meal. do not eat before meal. Medication 2:. 2 tablets Lasix at 03:10 PM."
        # medication_msg = "Sorry we are experiencing technical difficulties retrieving data. Please check back later."
        rootLogger.error('PICA connection Timeout')
    else:
        medication_msg = 'Error in Medication function'

    #medication_msg = "You have 2 medications to take.  Medication 1:. 1 tablet Panadol after meal. do not eat before meal. Medication 2:. 2 tablets Lasix at 03:10 PM."
    rootLogger.info("Get medication complete")
    rootLogger.debug(medication_msg)
    return medication_msg


def get_food_msg(msg_info,time_frame):
    rootLogger.info('Getting Food')
    '''
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

    foodlist, status = get_info_from_PICA(param)
    if status == 'ok':
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

    elif status == 'Connection Error':
        food_msg = 'PICA food API is down'
    elif status == 'Connection Timeout':
        food_msg = "PICA Appointment API Timed out. " \
                   "Please eat Breakfast everyday"
    else:
        food_msg = 'Error in food function'
    '''
    food_msg = "If you are not very hungry, you can have hot milo or porridge"
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
        # help_msg = 'Send help API is down'
        help_msg = 'Okay, Help is on its way'
        #do follow up action like send sms instead.
        rootLogger.info('Get help failed')

    rootLogger.debug(help_msg)
    return help_msg

def get_info_from_PICA(param):

    # retrieve data from PICA

    # build object to be sent. redundant?
    # data_to_send = {    'Alexa_id' : param['user_id'],
    #                    'date_range' : param['time_frame']
    #                }

    #url = '/'.join([pica_url,param['db_name'], param['time_frame']['date_start'], param['time_frame']['date_end'], param['user_id']])
    url = '/'.join([pica_url,param['db_name']])
    data_to_send = {'alexa_id': param['user_id'],
                    'startDate' : param['time_frame']['date_start'],
                    'endDate': param['time_frame']['date_end']}
    #rootLogger.debug(url)
    # Send request to PICA
    # try:
        # r = requests.post('http://httpbin.org/post', data = {'key':'value'})

    try:
        # pica_response = requests.get(url, timeout=2)
        pica_response = requests.get(url, params=data_to_send, timeout=2)
        pica_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        rootLogger.debug(e)
    except requests.exceptions.ConnectionError as e:
        rootLogger.debug("Error Connecting:")
        status = 'Connection Error'
        data_retrieved = ''
    except requests.exceptions.Timeout as e:
        rootLogger.debug("Timeout Error:" )
        status = 'Connection Timeout'
        data_retrieved = ''
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        rootLogger.debug(e)
    else:
        data_retrieved = pica_response.json()
        status = 'ok'

    # parse return data from PICA
    # iso8601.parse_date()
    # time of the appointment
    # type of service (e.g. meal service)
    # assigned healthcare worker
    # comments (this is optional e.g. assigned careworker will be running late)
    # data_recieved = r.json()


    return data_retrieved, status

def push_info_to_PICA(param):
    # Send request to PICA
    # r = requests.post('http://httpbin.org/post', data = {'key':'value'})
    # r = RQ.post(url, json = data_to_send)

    # parse return data from PICA
    # assigned healthcare worker
    # comments (this is optional e.g. assigned careworker will be running late)

    # data_recieved = r.json()

    #data_recieved = data_to_send
    status=False
    return status


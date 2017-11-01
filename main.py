from flask import Flask
from flask_ask import Ask, statement, question, session
import time

import sqlite3


app = Flask(__name__)

ask=Ask(app,"/Babybot")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_infofromdb(tablename):    
    '''
    exampledate=time.localtime()
    exampledatestr=time.strftime('%a, %d %b %Y %H:%M:%S',exampledate)
    examplecomment='Dental checkup at TTSH'
    schedulelist=[{'Datetime':exampledatestr,'comments':examplecomment}]
    '''
    #get from database
    db = sqlite3.connect('data/testdb')
    db.row_factory = dict_factory
    cursor = db.cursor()

    cursor.execute('select * from '+ tablename +' where username = "user1"')
    infolist=cursor.fetchall()  
    db.close()
    return infolist

def get_appointment_msg():
    print('Getting Appointments')
    tablename='appointment'
        
    appointmentslist=get_infofromdb(tablename)
    '''
    id INTEGER PRIMARY KEY,
    username TEXT,
    start_date TEXT, 
    contact_person TEXT,
    location TEXT,
    purpose TEXT)    
    '''
    if appointmentslist:
        numappointments=len(appointmentslist)
        appointment_msglist=[]
        if numappointments>1:
            appointment_msglist.append('You have {} appointments. '.format(numappointments))
        else:
            appointment_msglist.append('You have 1 appointment. ')
        
        for idx,appointment in enumerate(appointmentslist):
            if numappointments>1:
                appointment_msglist.append('Appointment {}:'.format(idx+1)+'.')
            if appointment['purpose']:
                appointment_msglist.append(appointment['purpose']+'.')
            if appointment['start_date']:
                appointment_msglist.append('On: '+ appointment['start_date']+'.')
            if appointment['contact_person']:
                appointment_msglist.append('With: '+ appointment['contact_person'])
            if appointment['location']:
                appointment_msglist.append('at: '+ appointment['location']+'.')
            
    else:
        appointment_msglist='You have no appointments.'
            
    #appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    appointment_msg=' '.join(appointment_msglist)
    return appointment_msg

def get_medication_msg():
    tablename='medication'
    medicationlist=get_infofromdb(tablename)
    '''
    id INTEGER PRIMARY KEY, 
    username TEXT,
    mediname TEXT, 
    dosage TEXT,
    frequency TEXT,
    comments TEXT)
    '''

    if medicationlist:
        nummedication=len(medicationlist)
        medication_msglist=[]
        if nummedication>1:
            medication_msglist.append('You have {} medications to take. '.format(nummedication))
        else:
            medication_msglist.append('You have 1 medication. ')
        
        for idx,medication in enumerate(medicationlist):
            if nummedication>1:
                medication_msglist.append('Medication {}:'.format(idx+1)+'.')
            if medication['dosage']:
                medication_msglist.append(medication['dosage'])
            if medication['mediname']:    
                medication_msglist.append(medication['mediname'])            
            if medication['frequency']:
                medication_msglist.append(medication['frequency']+'.')
            if medication['comments']:
                medication_msglist.append(medication['comments']+'.')
            
    else:
        medication_msglist='You have no medicaiton to take.'
            
    #appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    medication_msg=' '.join(medication_msglist)
    return medication_msg

def get_food_msg():
    tablename='food'
    foodlist=get_infofromdb(tablename)
    '''
    id INTEGER PRIMARY KEY, 
    username TEXT,
    foodtype TEXT, 
    frequency TEXT)
    '''
    if foodlist:        
        food_msglist=[]
        
        food_msglist.append('Please eat')        
        
        food_msglist2=[]
        for idx,food in enumerate(foodlist):
            if food['foodtype']:
                food_msglist2.append(food['foodtype'])
            if food['frequency']:
                food_msglist2.append(food['frequency'])

        food_msglist.append(' '.join(food_msglist2))    
    else:
        food_msglist='Eat whatever you like.'
            
    #appointment_msg='Your current schedules are {}'.format(appointment_msgstr)
    food_msg=' '.join(food_msglist)
    return food_msg

@app.route('/')
def homepage():
    return "Welcome to Baby bot!!"

@ask.launch
def start_skill():
    welcome_message='Hello there!'
    return question(welcome_message)

@ask.intent('GetAppointments')
def get_appointment():    
    return statement(get_appointment_msg())

@ask.intent('GetMedication')
def get_medication():
    return statement(get_medication_msg())

@ask.intent('GetFood')
def get_food():    
    return statement(get_food_msg())

@ask.intent('GetAll')
def get_all():
    all_msglist=[]
    all_msglist.append(get_appointment_msg())
    all_msglist.append(get_medication_msg())
    all_msglist.append(get_food_msg())
    all_msg=' '.join(all_msglist)

    return statement(all_msg)

@ask.intent('AMAZON.StopIntent')
def stop_intent():
    bye_text='Ok... bye'
    return statement(bye_text)

if __name__ == '__main__':
    app.run(debug=True)




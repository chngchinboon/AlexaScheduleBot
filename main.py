from flask import Flask
from flask_ask import Ask, statement, question, session
import time

app = Flask(__name__)

ask=Ask(app,"/AlexaScheduleBot")

def get_schedulelist():    
    #date time comments
    exampledate=time.localtime()
    exampledatestr=time.strftime('%a, %d %b %Y %H:%M:%S',exampledate)
    examplecomment='Dental checkup at TTSH'
    schedulelist=[{'Datetime':exampledatestr,'comments':examplecomment}]
    return schedulelist

@app.route('/')
def homepage():
    return "Hi there, how ya doin?"

@ask.launch
def start_skill():
    welcome_message='Hellow there, would you like to know your saved schedules?'
    return question(welcome_message)

@ask.intent('YesIntent'):
def share_schedule():
    schedulelist=get_schedulelist()
    for schedule in schedulelist:
        schedule_msgstr=i['Datetime']+' on '+i['comments']
    schedule_msg='Your current schedules are {}'.format(schedule_msgstr)
    return statement(schedule_msg)

@ask.intent('NoIntent'):
def no_intent():
    bye_text='Ok... bye'
    return statement(bye_text)









if __name__ == '__main__':
    app.run(debug=True)



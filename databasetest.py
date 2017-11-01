# -*- coding: utf-8 -*-
"""
Created on Wed Nov 01 15:41:41 2017

@author: Owner
"""
import time
import sqlite3
db = sqlite3.connect('data/testdb')

cursor = db.cursor()

cursor.execute('''
    CREATE TABLE userdetails(
    id INTEGER PRIMARY KEY, 
    userame TEXT, 
    emergencyno TEXT,  
    email TEXT,
    affiliation TEXT)
''')

cursor.execute('''
    CREATE TABLE appointment(
    id INTEGER PRIMARY KEY,
    username TEXT,
    start_date TEXT, 
    contact_person TEXT,
    location TEXT,
    purpose TEXT)    
''')
    
cursor.execute('''
    CREATE TABLE food(
    id INTEGER PRIMARY KEY, 
    username TEXT,
    foodtype TEXT, 
    frequency TEXT)
''')
    
cursor.execute('''
    CREATE TABLE medication(
    id INTEGER PRIMARY KEY, 
    username TEXT,
    mediname TEXT, 
    dosage TEXT,
    frequency TEXT,
    comments TEXT)
''')  
    
db.commit()


#example userdetails
username1='user1'
emergencyno1='12345678'
email1='test@test.com'
affiliation1='NUS'

username2='user2'
emergencyno2='12345678'
email2='test2@test.com'
affiliation2='ISS'

userlist=[(username1, emergencyno1, email1, affiliation1),
          (username2, emergencyno2, email2, affiliation2)]

cursor.executemany('''INSERT INTO userdetails(userame, emergencyno, email, affiliation)
                  VALUES(?,?,?,?)''', userlist)

#example appointment
#username1
start_date1=time.strftime('%a, %d %b %Y, %#I:%M %p',time.localtime(time.time()+50*24*60*60)) #50 day later
contact_person1='Dr Chin'
location1='TTSH'
purpose1='Dental Checkup'  

cursor.execute('''INSERT INTO appointment(username, start_date, contact_person, location, purpose)
                    VALUES(?,?,?,?,?)''', (username1, start_date1, contact_person1, location1, purpose1))  

#example food
#username TEXT,
foodtype1='Breakfast'
frequency1='everyday'

cursor.execute('''INSERT INTO food(username, foodtype, frequency)
                    VALUES(?,?,?)''', (username1, foodtype1, frequency1))  

#example medication
#username TEXT,
mediname1='Panadol'
dosage1='1 tablet'
frequency1='after meal'
comments1='do not eat before meal'

mediname2='Lasix'
dosage2='2 tablets'
frequency2=None
comments2='at '+time.strftime('%I:%M %p',time.localtime(time.time()+60*60)) #1hr

medicationlist=[(username1, mediname1, dosage1, frequency1,comments1),
                (username1, mediname2, dosage2, frequency2,comments2)]

cursor.executemany('''INSERT INTO medication(username, mediname, dosage, frequency, comments)
                    VALUES(?,?,?,?,?)''', medicationlist) 

db.commit()


#cursor.execute('select * from medication where username = "user1"')
#print cursor.fetchall()

db.close()

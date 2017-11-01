Intent schema

{
    "intents": [
    {
        "intent": "GetAll"             
    },
    
    {
        "intent": "GetAppointments"        
    },    
     
    {
        "intent": "GetMedication"        
    },    
     
    {
        "intent": "GetFood"        
    },    
     
    {
        "intent": "AMAZON.StopIntent"        
    },     
                
    ]
}

#for reference    
{
    "intent": "GetAppointments"        
    "slots":[
        {
          "name": "TimeFrame",
          "type": "LIST_OF_TERMS"
        }
    ]
},    
  
    
 
    
    
    
Sample Utterances

GetAppointments what appointments do i have {TimeFrame}
GetAppointments who do i need to meet {TimeFrame}
GetAppointments meet who {TimeFrame}

GetMedication what medicine do i need to eat
GetMedication what medication do i need to eat
GetMedication what medicine
GetMedication medicine eat what
GetMedication what medication

GetFood what do i need to eat
GetFood what should i eat
GetFood eat what

GetAll list all my reminders
GetAll tell me everything
GetAll to refresh me
GetAll remind me of everything
GetAll to remind me all


NoIntent no
NoIntent go away
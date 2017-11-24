Intent schema

{
    "intents": [
    {
        "intent": "GetAll"             
    },
    
    {
        "intent": "GetAppointments",
        "slots":[{
              "name": "TimeFrame",
              "type": "AMAZON.DATE"
                  }]        
    },    
     
    {
        "intent": "GetMedication"        
    },    
     
    {
        "intent": "GetFood"        
    },

    {
        "intent": "GetHelp"
    },

    {
        "intent": "GetPledge"
    },
        {
        "intent": "AMAZON.StopIntent"        
    },     
                
    ]
}

#for reference    
{
    "intent": "GetAppointments",        
    "slots":[
        {
          "name": "TimeFrame",
          "type": "AMAZON.DATE"
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

GetHelp help me please
GetHelp please help
GetHelp please send help
GetHelp I've fallen please send help

GetPledge pledge me
GetPledge what's new today
GetPledge how are you today
GetPledge would you talk to me please
GetPledge talk to me


NoIntent no
NoIntent go away
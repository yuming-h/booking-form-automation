from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

cal_id = {
    103: 'sus.ubc.ca_uftrmmskndipsbndg151dtl5b8@group.calendar.google.com',
    104: 'sus.ubc.ca_5s71t4b60qmlfll20ktfp5a78g@group.calendar.google.com',
    105: 'sus.ubc.ca_5ml80mepktclmrihpjugh4g8k8@group.calendar.google.com'
}
def format_datetime(datetime):
    yr = str(datetime.year)
    month = str(datetime.month)
    day = str(datetime.day)
    hour = str(datetime.hour)
    minute = str(datetime.minute)
    if len(month) < 2:
        month = '0'+month
    if len(day) < 2:
        day = '0'+day
    if len(hour) < 2:
        hour = '0'+hour
    if len(minute) < 2:
        minute = '0'+minute
    return yr+'-'+month+'-'+day+'T'+hour+':'+minute+':00'

def format_date(date):
    li = date.split('/')
    return li[2]+li[0]+li[1]+'T235900Z'

def update_calendar(booking):
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('cal_credential.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    event = {
        'summary': booking['org'] + ' - ' + booking['eventname'],
        'description': 'Event Number ' + str(booking['number']) + '\n' + 'Booked Areas: ' + booking['floors'] + '\n' + 'Event supervisor: ' + booking['sup'][0],
        'start': {
            'dateTime': format_datetime(booking['daterange'][0]),
            'timeZone': 'America/Los_Angeles'
            },
        'end': {
            'dateTime': format_datetime(booking['daterange'][1]), 
            'timeZone': 'America/Los_Angeles'
            },
                
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

def update_room_calendar(booking):
    print(format_date(booking['enddate']))
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('cal_credential.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    event = {
        'summary': booking['org'],
        'description': 'Booked by: ' + booking['name'],
        'start': {
            'dateTime': format_datetime(booking['daterange'][0]),
            'timeZone': 'America/Los_Angeles'
            },
        'end': {
            'dateTime': format_datetime(booking['daterange'][1]), 
            'timeZone': 'America/Los_Angeles'
            },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;UNTIL="+ format_date(booking['enddate'])
        ],
    }

    event = service.events().insert(calendarId=cal_id[booking['room']], body=event).execute()
 


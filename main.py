import requests
import configparser
import pickle
import os.path
from datetime import datetime, timedelta
from supervisors import selectSupervisor
from booking_type import BookingType, getBookingType
from supervisor_email import send_supervisor_confirmation
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow #pylint: disable=import-error
from google.auth.transport.requests import Request



SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_NAME = 'Form Responses 1'

config = configparser.ConfigParser()
config.read('config')
defaultConfig = config['DEFAULT']
EVENTS_FORM_ID = defaultConfig['eventsFormID']
ROOMS_FORM_ID = defaultConfig['roomsFormID']
EMAIL = defaultConfig['email']
PASS = defaultConfig['password']

def parseDateTime(date, start, end):
    startDate = datetime.strptime(date+' '+start, '%m/%d/%Y %I:%M:%S %p')
    t = datetime.strptime(end, '%I:%M:%S %p')
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    endDate = startDate + delta

    return (startDate, endDate)

def main():

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token, encoding='latin1')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets() #pylint: disable=maybe-no-member
    
    eventBookings = sheet.values().get(spreadsheetId=EVENTS_FORM_ID,
        range=SHEET_NAME).execute().get('values', [])
    
    roomBookings = sheet.values().get(spreadsheetId=ROOMS_FORM_ID,
        range=SHEET_NAME).execute().get('values', [])
    
    print('='*50)
    print('Event Bookings:')
    print('='*50)
    print('\n')
    
    firstEvent = defaultConfig.getint('lastEvent')
    for i in range(firstEvent, len(eventBookings)):
        responses = eventBookings[i]
        booking = {
            'org': responses[2],
            'name': responses[3],
            'title': responses[4],
            'phone': responses[5],
            'email': responses[6],
            'type': getBookingType[responses[7]],
            'daterange': parseDateTime(responses[8], responses[9], responses[10]),

            'eventname': responses[11],
            'desc': responses[12],
            'public': True if responses[13] == 'Public' else False,
            'count': int(responses[14]),
            'floors': responses[15],
            'audio': responses[16],
            'speaker': True if '550W' in responses[17] else False,
            'alc': True if responses[21] == 'Yes' else False,
            'sup': None
        }

        for a,b in booking.items():
            if a == 'daterange':
                print(a, ': ', b[0].strftime('%m/%d/%Y %H:%M%p - '),
                     b[1].strftime('%H:%M%p'))
            else:
                print(a, ': ', b)


        approval = input('Approve this booking? [y/n]: ')
        while approval not in ['y','n']:
            approval = input('That is not a valid option. Approve this booking? [y/n]: ')
        
        if approval == 'y':

            needSupervisor = input('Assign a supervisor? [y/n]: ')
            while needSupervisor not in ['y','n']:
                needSupervisor = input('Assign a Supervisor? [y/n]: ')
            
            if needSupervisor == 'y':
                booking['sup'] = selectSupervisor()
                print('Sending Email to Supervisor ...')
    #            send_supervisor_confirmation(booking, email, pw)


if __name__ == '__main__':
   main()

input("No requests left! Press Enter to exit.")
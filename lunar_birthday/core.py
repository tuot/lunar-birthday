import datetime
import json
import logging
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from zhdate import ZhDate

logging.basicConfig(level=logging.ERROR)


class LunarBirthday():
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/contacts.readonly',
    ]
    credentials_file = os.path.join(os.getcwd(), 'credentials.json')
    people_birthday_file = 'birthdays.json'
    person_fields = 'birthdays,events,names'
    lunar_calendar_name = 'Lunar Birthday'
    time_zone = 'Asia/Shanghai'

    def __init__(self):
        pass

    def get_creds(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file(
                'token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds


    def __get_calendar_service(self):
        # ref: https://developers.google.com/calendar/api/quickstart/python
        creds = self.get_creds()
        service = build('calendar', 'v3', credentials=creds)
        return service

    def __get_contacts_service(self):
        # ref: https://developers.google.com/people/quickstart/python

        creds = self.get_creds()
        service = build('people', 'v1', credentials=creds)
        return service

    def get_contacts_birthdays(self):
        birthdays_list = []
        service = self.__get_contacts_service()
        page_token = None
        while True:
            req = service.people().connections().list(
                resourceName='people/me',
                pageToken=page_token,
                personFields=self.person_fields)
            response = req.execute()
            connections = response.get('connections', [])
            for people in connections:
                if people.get('names'):
                    people_item = {
                        'name': people.get('names')[0]['displayName'],
                        'events': []
                    }
                if people.get('events'):
                    events = people.get('events')
                    for item in events:
                        item.pop('metadata')
                        item.pop('type')
                        people_item['events'].append(item)
                if people.get('birthdays'):
                    birthdays = people.get('birthdays')
                    for item in birthdays:
                        item.pop('metadata')
                        people_item['events'].append(item)
                if people_item.get('events'):
                    birthdays_list.append(people_item)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        with open(self.people_birthday_file, 'w', encoding='utf-8') as f:
            json.dump(birthdays_list, f, ensure_ascii=False, indent=4)

    def __create_birthday_event(self,
                                name,
                                date,
                                description=None,
                                is_lunar=False):
        event = {
            'summary': name,
            'description': description,
            'start': {
                'date': '{year}-{month}-{day}'.format(**date),
                'timeZone': self.time_zone,
            },
            'end': {
                'date': '{year}-{month}-{day}'.format(**date),
                'timeZone': self.time_zone,
            },
            'reminders': {
                'useDefault': True
            },
        }
        if not is_lunar:
            event.update({
                'recurrence': ["RRULE:FREQ=YEARLY"],
            })
        return event

    def __get_lunar_calendar_id(self):
        service = self.__get_calendar_service()
        calendar_list = service.calendarList().list().execute()
        for item in calendar_list['items']:
            if item['summary'] == self.lunar_calendar_name:
                calendar_id = item['id']
                service.calendars().delete(calendarId=calendar_id).execute()
                break

        calendar = {
            'summary': self.lunar_calendar_name,
            'timeZone': self.time_zone,
        }
        lunar_calendar = service.calendars().insert(
            body=calendar).execute()
        calendar_id = lunar_calendar['id']

        return calendar_id

    def insert_event_to_calendar(self):
        with open(self.people_birthday_file, 'r', encoding='utf-8') as f:
            birthdays = json.load(f)

        calendar_id = self.__get_lunar_calendar_id()

        service = self.__get_calendar_service()
        batch = service.new_batch_http_request()
        for people in birthdays:
            if people.get('events'):
                name = people['name']
                logging.info(name)
                events = people.get('events')
                for event in events:
                    year = event['date']['year']
                    formattedType = event.get('formattedType', '')
                    now_year = datetime.datetime.now().date().year
                    if formattedType.find('农历') != -1:
                        while now_year < 2100:
                            date = ZhDate(now_year, event['date']['month'],
                                          event['date']['day'])
                            lunar_date = {
                                'year': date.to_datetime().date().year,
                                'month': date.to_datetime().date().month,
                                'day': date.to_datetime().date().day,
                            }
                            create_event = self.__create_birthday_event(
                                f'{name}的{now_year-year}岁{formattedType}',
                                lunar_date,
                                description=date.chinese(),
                                is_lunar=True)
                            batch.add(service.events().insert(
                                calendarId=calendar_id,
                                body=create_event))
                            now_year += 1

                    else:  # 阳历生日
                        if formattedType == '':
                            formattedType = '岁生日'
                        elif formattedType == 'Anniversary':
                            formattedType = '周年纪念日'
                        while now_year < 2100:
                            event['date']['year'] = now_year
                            create_event = self.__create_birthday_event(
                                f'{name}的{now_year-year}{formattedType}',
                                event['date'])
                            batch.add(service.events().insert(
                                calendarId=calendar_id,
                                body=create_event))
                            now_year += 1
        batch.execute()

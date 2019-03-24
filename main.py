#!/usr/bin/python

import httplib2
import sys
import json
import datetime

from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow

from zhdate import ZhDate

client_id = '108884890762-0jpidgfadtlp0f90urv6513vah5uphbu.apps.googleusercontent.com'
client_secret = 'u9gk_gb4pyoE_WeGqQj6iBY5'

scope = ['https://www.googleapis.com/auth/calendar',
         'https://www.googleapis.com/auth/contacts.readonly']

flow = OAuth2WebServerFlow(client_id, client_secret, scope)

person_fields = 'addresses,ageRanges,biographies,birthdays,braggingRights,coverPhotos,emailAddresses,events,genders,imClients,interests,locales,memberships,metadata,names,nicknames,occupations,organizations,phoneNumbers,photos,relations,relationshipInterests,relationshipStatuses,residences,sipAddresses,skills,taglines,urls,userDefined'


def get_calendar_service():
    storage = Storage('credentials.json')

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(
            flow, storage, tools.argparser.parse_args())

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('calendar', 'v3', http=http)

    return service


def get_contacts_service():
    storage = Storage('credentials.json')

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(
            flow, storage, tools.argparser.parse_args())

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build(serviceName='people', version='v1', http=http)

    return service


def get_contacts_birthdays():
    birthdays_list = []
    service = get_contacts_service()
    page_token = None
    while True:
        req = service.people().connections().list(resourceName='people/me',
                                                  pageToken=page_token,
                                                  personFields=person_fields)
        response = req.execute()
        connections = response.get('connections', [])
        for people in connections:
            people_item = {
                'name': people.get('names')[0]['displayName'],
                'events': []
            }
            if people.get('events'):
                events = people.get('events')
                for item in events:
                    print(item)
                    item.pop('metadata')
                    item.pop('type')
                    people_item['events'].append(
                        item
                    )
            if people.get('birthdays'):
                birthdays = people.get('birthdays')
                for item in birthdays:
                    print(item)
                    item.pop('metadata')
                    people_item['events'].append(
                        item
                    )
            if people_item.get('events'):
                birthdays_list.append(people_item)
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    with open('birthdays.json', 'w', encoding='utf-8') as f:
        json.dump(birthdays_list, f, ensure_ascii=False, indent=4)


def get_calendar_events(service, calendar_id):
    try:
        request = service.events().list(calendarId=calendar_id)
        while request != None:
            response = request.execute()
            event_list = response.get('items', [])
            print(json.dumps(event_list, ensure_ascii=False, indent=4))
            for event in event_list:
                print(repr(event.get('summary', 'NO SUMMARY')) + '\n')
            request = service.events().list_next(request, response)
    except AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize')


def create_birthday_event(summary, date, description=None, is_lunar=False):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'date': '{year}-{month}-{day}'.format(**date),
            'timeZone': 'Asia/Shanghai',
        },
        'end': {
            'date': '{year}-{month}-{day}'.format(**date),
            'timeZone': 'Asia/Shanghai',
        },
        'reminders': {'useDefault': True},
    }
    if is_lunar:
        pass
    else:
        event.update({
            'recurrence': [
                "RRULE:FREQ=YEARLY"
            ],
        })
    return event


def callback_insert_event(*args, **kwargs):

    print(args)
    print(kwargs)


def get_lunar_calendar_id(service):
    calendar_list = service.calendarList().list().execute()
    for item in calendar_list['items']:
        if item['summary'] == 'Lunar Birthday':
            calendar_id = item['id']
            break
    else:
        calendar = {
            'summary': 'Lunar Birthday',
            'timeZone': 'Asia/Shanghai',
        }

        lunar_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = lunar_calendar['id']

    return calendar_id


def insert_event_to_calendar(service, calendar_id=None):

    with open('birthdays.json', 'r', encoding='utf-8') as f:
        birthdays = json.load(f)
    for people in birthdays:
        if people.get('events'):
            name = people['name']
            print(name)
            events = people.get('events')
            batch = service.new_batch_http_request(
                callback=callback_insert_event)
            for event in events:
                formattedType = event.get('formattedType', '')
                if formattedType.find('农历') != -1:
                    now_year = datetime.datetime.now().date().year
                    while now_year < 2100:
                        date = ZhDate(
                            now_year, event['date']['month'], event['date']['day'])
                        lunar_date = {
                            'year': date.to_datetime().date().year,
                            'month': date.to_datetime().date().month,
                            'day': date.to_datetime().date().day,
                        }
                        create_event = create_birthday_event(
                            '{}的{}'.format(name, formattedType), lunar_date,
                            description=date.chinese(),
                            is_lunar=True)
                        batch.add(service.events().insert(
                            calendarId=calendar_id, body=create_event))
                        now_year += 1

                else:  # 阳历生日
                    if formattedType == '':
                        formattedType = '生日'
                    elif formattedType == 'Anniversary':
                        formattedType = '周年纪念日'

                    create_event = create_birthday_event(
                        '{}的{}'.format(name, formattedType), event['date'])
                    batch.add(service.events().insert(
                        calendarId=calendar_id, body=create_event))
            batch.execute()


def main():

    # get_contacts_birthdays()

    service = get_calendar_service()
    lunar_calendar_id = get_lunar_calendar_id(service)

    insert_event_to_calendar(service, lunar_calendar_id)

    # get_calendar_events(service, lunar_calendar_id)


if __name__ == '__main__':
    main()

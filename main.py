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

client_id = '108884890762-0jpidgfadtlp0f90urv6513vah5uphbu.apps.googleusercontent.com'
client_secret = 'u9gk_gb4pyoE_WeGqQj6iBY5'

scope = ['https://www.googleapis.com/auth/calendar',
         'https://www.googleapis.com/auth/contacts.readonly']

flow = OAuth2WebServerFlow(client_id, client_secret, scope)


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


def main():

    birthdays_list = []
    service = get_contacts_service()
    page_token = None
    while True:
        response = service.people().connections().list(resourceName='people/me',
                                                       pageToken=page_token,
                                                       personFields='names,biographies,birthdays').execute()
        connections = response.get('connections', [])
        for people in connections:
            contacts_biographies = people.get('biographies')
            if contacts_biographies:
                people_item = {
                    'name': people.get('names')[0]['displayName']
                }
                if contacts_biographies:
                    value = contacts_biographies[0]['value']
                    try:
                        datetime.datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        print(value + '日期填写错误')
                    else:
                        people_item['birthday'] = value
                        people_item['is_lunar'] = True
                        birthdays_list.append(people_item)
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    with open('birthdays.json', 'w', encoding='utf-8') as f:
        json.dump(birthdays_list, f, ensure_ascii=False, indent=4)
    # page_token = None
    # while True:
    #     calendar_list = service.calendarList().list(pageToken=page_token).execute()
    #     for calendar_list_entry in calendar_list['items']:
    #         print(calendar_list_entry['summary'])
    #     page_token = calendar_list.get('nextPageToken')
    #     if not page_token:
    #         break


    # try:
    #     request = service.events().list(calendarId='#contacts@group.v.calendar.google.com')
    #     while request != None:
    #         response = request.execute()
    #         event_list = response.get('items', [])
    #         print(json.dumps(event_list, ensure_ascii=False, indent=4))
    #         for event in event_list:
    #             print(repr(event.get('summary', 'NO SUMMARY')) + '\n')
    #         request = service.events().list_next(request, response)
    # except AccessTokenRefreshError:
    #     print('The credentials have been revoked or expired, please re-run'
    #           'the application to re-authorize')
if __name__ == '__main__':
    main()

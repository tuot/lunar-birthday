#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import sys
import json

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

    service = get_contacts_service()
    resp = service.contactGroups().list().execute()

    contactGroups_resourceName = ''
    for item in resp.get('contactGroups', []):
        if item['formattedName'] == '农历生日':
            contactGroups_resourceName = item['resourceName']

    resp = service.contactGroups().get(resourceName=contactGroups_resourceName,
                                       maxMembers=100).execute()
    if resp:
        pass

    page_token = None
    while True:
        response = service.people().connections().list(resourceName='people/me',
                                                       pageToken=page_token,
                                                       personFields='addresses,ageRanges,biographies,birthdays,braggingRights,coverPhotos,emailAddresses,events,genders,imClients,interests,locales,memberships,metadata,names,nicknames,occupations,organizations,phoneNumbers,photos,relations,relationshipInterests,relationshipStatuses,residences,sipAddresses,skills,taglines,urls,userDefined').execute()
        connections = response.get('connections', [])
        for people in connections:
            print(people.get('names'))
            if people.get('names')[0].get('displayName') == '爸爸':
                print(people.get('birthdays'))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

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

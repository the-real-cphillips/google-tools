#!/usr/bin/env python
from __future__ import print_function

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import json
import sys

import backoff
import googleapiclient


def auth(scope, fn='credentials.json', svc='gmail', version='v1'):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(fn, scope)
        creds = tools.run_flow(flow, store)
    service = build(svc, version, http=creds.authorize(Http()))
    return service


class Purge:

    
    def __init__(self, connection):
        self.connection = connection


    def get_label_id(self, label_name, userId='me'):
      try:
        response = self.connection.users().labels().list(userId=userId).execute()
        labels = response['labels']
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
      except googleapiclient.errors.HttpError as error:
        print(f'An error occurred: {error}')


    def gather(self, userId='me', query='', labels=None):
        to_process = {}
        message_count = 0

        if labels:
            request = self.connection.users().messages().list(userId=userId, q=query, labelIds=[labels])
        else:
            request = self.connection.users().messages().list(userId=userId, q=query)
        response = request.execute()
        try:
            messages = response['messages']
            for message in messages:
                to_process[message_count] = message['id']
            page_count = 1
            print("[I] Gathering Pages")
            while response.get('nextPageToken'):
                request = self.connection.users().messages().list_next(previous_request=request, previous_response=response)
                response = request.execute()
                page_count += 1
                messages += response['messages']
            print("[√] Total Page Count: {}".format(page_count))
            for message in messages:
                message_count += 1
                to_process[message_count] = message['id']
            self.to_process = to_process
        except KeyError as e:
            print("[X] No Matches Found, Please Check Your Query Strng")
            sys.exit(1)


    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError)
    def purge(self, message_list, action, userId='me'):
        count = 0
        for item in message_list:
            resource = getattr(self.connection.users().messages(), action)
            dynamic_request = resource(userId=userId, id=message_list[item])
            try:
                response = dynamic_request.execute()
                count += 1
                print("[√] Action: {} - {} of {} - Message ID: {}".format(action, count, len(message_list) , message_list[item]))
            except googleapiclient.errors.HttpError as e:
                if e.resp.status == 404:
                    print("[X] Error: ID {} Not Found".format(message_list[item]))
                else:
                    print("[X] Error: ID {} {}".format(message_list[item], e))
                count -= 1
        print("[√] Processed: {} of {} Messages".format(count, len(message_list)))
        return True


    def batch_process(self, message_list, action, userId='me'):
        list_of_ids = []

        for key, value in message_list.items():
            list_of_ids.append(value)

        chunks = [list_of_ids[x:x+1000] for x in range(0, len(list_of_ids), 1000)]

        for page in range(0, len(chunks)):
            if action.lower() == 'archive':
                resource = getattr(self.connection.users().messages(), 'batchModify')
                body = { 
                        "ids": chunks[page],
                        "removeLabelIds": ["INBOX"],
                        }
            else:
                resource = getattr(self.connection.users().messages(), 'batchDelete')
                body = { 
                        "ids": chunks[page],
                        }

            dynamic_request = resource(userId=userId, body=body)
            response = dynamic_request.execute()
            print("[√] SUCCESS {} Messages have been {}d! - {}".format(len(chunks[page]), action, page))
        print("[√] SUCCESS Total Number of Processed Messages: {}".format(len(list_of_ids)))



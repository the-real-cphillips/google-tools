#!/usr/bin/env python
from __future__ import print_function

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import json
import sys

import backoff
import googleapiclient


def auth(scope='https://mail.google.com', fn='credentials.json', svc='gmail', version='v1'):
    """Auth
    This handles the authorization.

    On First run, this will pop up a browser window, and request access
    Subsequent runs will not pop up the browser window, unless you change your
    scope, or your credentials file.  If you change either, you need to remove the
    `tokens.json` file that a successful auth creates

    You need:
    - a JSON File that has proper credentials, see the README for this
      - Default is : credentials.json, but you can pass `fn=<whatever>.json` as you like
    - an Auth Scope.
      - Default is `https://mail.google.com
      - More info Available in the README and here: https://developers.google.com/gmail/api/auth/scopes

    Params:
        scope - str - https://mail.google.com
        file_name - str - credentials.json

    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(fn, scope)
        creds = tools.run_flow(flow, store)
    service = build(svc, version, http=creds.authorize(Http()))
    return service


class Purge:
    """Purge
    The Gmail Web UI doesn't handle purging large amounts of messages/threads
    Thus this was born!
    It's also a good project for me to practice some Python :)
    """

    def __init__(self, connection):
        self.connection = connection

    def get_label_id(self, label_name, userId='me'):
        """Get Label ID
        This accepts a Friendly Label Name that a user has created, and converts it to it's ID.
        This is used to pass on to the `gather` class method, if using Labels in your query.

        Params:
        - label_name - str
        - userId - str - Defaults to 'me', special keyword for your account.
        """

        try:
            response = self.connection.users().labels().list(userId=userId).execute()
            labels = response['labels']
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
        except googleapiclient.errors.HttpError as error:
            print(f'An error occurred: {error}')

    def gather(self, userId='me', query='', label=None):
        """Gather
        This gathers the messages that will be processed through the purge features

        Params:
        - userId - str - Default: 'me'
        - query - str - This follows the standard GMAIL Search strings
          - ie: older_than:20d etc...
        - label - str - Default is None, if you want to use a label, be sure to use `get_label_id` first
        """

        to_process = {}
        message_count = 0

        if label:
            request = self.connection.users().messages().list(userId=userId, q=query, labelIds=[label])
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
            print(f'[√] Total Page Count: {page_count}')
            for message in messages:
                message_count += 1
                to_process[message_count] = message['id']
            self.to_process = to_process
        except KeyError as e:
            print("[X] No Matches Found, Please Check Your Query Strng")
            sys.exit(1)

    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError)
    def purge(self, message_list, action, userId='me'):
        """Purge
        This is the main action where things get deleted or trashed.
        If you are looking for an archive option, that doesn't exist yet.

        Params:
        - message_list - dict - dict format is { int : 'str' }
          - ie  {
                0: '160a907427a1ca95',
                1: '160a90342f9f8c29'
                }
          - you get this after you've ran Object.gather()
            - Object.to_process is available with the necessary dict.
            - pass that into this.
        - action - str - delete or trash, no default.
        """

        if action.lower() == 'archive':
            print("[X] Error illegal action, only 'delete' and 'trash' allowed")
            sys.exit(2)
            return False

        count = 0
        for item in message_list:
            resource = getattr(self.connection.users().messages(), action)
            dynamic_request = resource(userId=userId, id=message_list[item])
            try:
                response = dynamic_request.execute()
                count += 1
                print(f'[√] Action: {action} - {count} of {len(message_list)} - Message ID: {message_list[item]}')
            except googleapiclient.errors.HttpError as error:
                if e.resp.status == 404:
                    print(f'[X] Error: ID {message_list[item]} Not Found')
                else:
                    print(f'[X] Error: ID {mesage_list[item]} {error}')
                count -= 1
        print(f'[√] Processed: {count} of {len(message_list)} Messages')
        return True

    @backoff.on_exception(backoff.expo, googleapiclient.errors.HttpError)
    def batch_process(self, message_list, action, userId='me'):
        """Batch Process
        This is where we handle Batches of either Archiving or Deletion
        Trash cannot be done in bulk.
        This takes a list larger than 1000 items and splits it into chunks.
        Those chunks are then processed in batch, this is due to batch having a 1000 item limit.

        Params:
        - message_list - dict - dict format is { int : 'str' }
          - ie  {
                0: '160a907427a1ca95',
                1: '160a90342f9f8c29'
                }
          - you get this after you've ran Object.gather()
            - Object.to_process is available with the necessary dict.
            - pass that into this.
        - action - str - 'delete' or 'archive'
        """

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
            print(f'[√] SUCCESS {len(chunks[page])} Messages have been {action}d! - {page}')
        print(f'[√] SUCCESS Total Number of Processed Messages: {len(list_of_ids)}')
        return True



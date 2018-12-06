#!/usr/bin/env python
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient import errors
import backoff

messages_to_delete = []

# Auth Stuff
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

def auth(scope, fn='credentials.json', svc='gmail', version='v1'):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(fn, scope)
        creds = tools.run_flow(flow, store)
    service = build(svc, version, http=creds.authorize(Http()))
    return service


@backoff.on_exception(backoff.expo,
            errors.HttpError,
            max_time=60)
def gather_messages(auth, userId='me', query='',  num_per_page=5000):
    request = auth.users().messages().list(userId=userId, q=query, maxResults=num_per_page)
    response = request.execute()
    try:
        messages = response['messages']
        for message in messages:
            messages_to_delete.append(message['id'])
        count = 0
        print("[I] Gathering Pages")
        while response.get('nextPageToken'):
            request = auth.users().messages().list_next(previous_request=request, previous_response=response)
            response = request.execute()
            count += 1
            messages += response['messages']
        print("[√] Total Page Count: {}".format(count))
        for message in messages:
            messages_to_delete.append(message['id'])
        return len(messages_to_delete)
    except KeyError as e:
        print("[X] No Matches Found, Please Check Your Query Strng")


@backoff.on_exception(backoff.expo,
            errors.HttpError,
            max_time=60)
def delete_messages(auth, messageList, userId='me'):
    count = 0
    try:
        for message in messageList:
            request = auth.users().messages().trash(userId=userId, id=message)
            count += 1
            response = request.execute()
            print("[√] Deleting {} of {}".format(count, len(messageList)))
        print("[√] Deleted: {} Messages".format(count))
        return True
    except errors.HttpError as e:
        print("[X] Error: {}".format(e))


def main():
    a = auth(SCOPES)
    query_string = input("[?] Enter your query (standard gmail format): ")
    delete_option = input("[?] Would you like to delete the matched messages? Y/N: ")
    print("[√] Gathering Messages using query_string: '{}'".format(query_string))
    gather_messages(a, query=query_string)
    
    if delete_option.lower() == 'y':
        delete_messages(a, messages_to_delete)
    else:
        print("[I] Not Deleting, Would have deleted: {} message(s)".format(len(messages_to_delete)))


if __name__ == '__main__' :
    main()

#!/usr/bin/env python
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import backoff
import googleapiclient
import sys

messages_to_delete = []

# Auth Stuff
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://mail.google.com'


def auth(scope=SCOPES, fn='credentials.json', svc='gmail', version='v1'):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(fn, scope)
        creds = tools.run_flow(flow, store)
    service = build(svc, version, http=creds.authorize(Http()))
    return service


@backoff.on_exception(backoff.expo,
            googleapiclient.errors.HttpError)
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
        sys.exit(1)


@backoff.on_exception(backoff.expo,
            googleapiclient.errors.HttpError)
def trash_messages(auth, messageList, userId='me'):
    count = 0
    try:
        for message in messageList:
            request = auth.users().messages().trash(userId=userId, id=message)
            count += 1
            response = request.execute()
            print("[√] Trashing {} of {} - Message ID: {}".format(count, len(messageList), message))
        print("[√] Trashed: {} Messages".format(count))
        return True
    except googleapiclient.errors.HttpError as e:
        print("[X] Error: {}".format(e))


@backoff.on_exception(backoff.expo,
            googleapiclient.errors.HttpError)
def delete_messages(auth, messageList, approval, userId='me'):
    if approval.lower() == 'y':
        chunks = [messageList[x:x+1000] for x in range(0, len(messageList), 1000)]
        for page in range(0,len(chunks)):
            request = auth.users().messages().batchDelete(
                userId='me', 
                body= 
                {
                    "ids": chunks[page]
                }
            )
            response = request.execute()
            print("[√] SUCCESS {} Messages have been deleted! - {}".format(len(chunks[page]), page))
        print("[√] SUCCESS Total Number of Delete Messages: {}".format(len(messageList)))
    else:
        print("[I] Not Deleting, Would have deleted: {} message(s)".format(len(messageList)))



def main():
    a = auth(SCOPES)
    query_string = input("[?] Enter your query (standard gmail format): ")
    option = input("[?] Gather Matched Amount? Move to Trash? or Delete? (delete | gather | trash): ")
    print("[√] Gathering Messages using query_string: '{}'".format(query_string))
    gather_messages(a, query=query_string)
    
    if option.lower() == 't' or option.lower() == 'trash':
        trash_messages(a, messages_to_delete)
    elif option.lower() == 'd' or option.lower() == 'delete':
        approval = input("[???] Preparing to delete {} messages. Approve? (Y/N) ".format(len(messages_to_delete)))
        delete_messages(a, messages_to_delete, approval.lower())
    elif option.lower() == 'g' or option.lower() == 'gather':
        print("Total Matched Messages: {}".format(len(messages_to_delete)))
    else:
        print("Invalid Option: please use 'delete', gather', or `trash`")


if __name__ == '__main__' :
    main()

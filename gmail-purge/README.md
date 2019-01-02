# PURGE!

I had went all in on Google Inbox... shunning Gmail forever, I let it do it's thing
turns out, bad idea.

Google is killing off Inbox... I need to get my gmail straight...

So I wrote this.

you need API keys for this from Google you can do this in projects.
I'll flesh this out a bit more to explain the full setup.

## Step 1 - Create the Project
- Go Here - https://console.developers.google.com
- click `Create Project` button
- Follow the steps to create the project

## Step 2 - Enabling the Gmail API
- In the main screen of Google APIs, find `ENABLE APIS AND SERVICES`
  - or search for Gmail API
- Once you find Gmail API click it and then click "ENABLE"
- You should be taken to a page that shows some status and graph.

## Step 3 - Obtaining Credentials
These steps are done from the Hamburger menu on the main page.
NOTE: Gmail requires OAUTH 2.0 credentials
- Find `API & Services`
- Find `Credentials`, Click It!
- Click `Create Credentials` in the middle of the window
- Create an OAuth Client Id
  - If it's your first time it's going setup your OAuth consent screen.
  - No modifications need to be done here.
- Once that's done, you'll have the option to Download the json.
- Download that json, and copy it into this directory named `credentials.json`

You should be ready at this point to do what you need, so let's continue

## Install

- clone this repo
- create a virtualenv
- activate your virtualenv
- run `pip install -r requirements.txt`
- then run `./purge.py`
  - NOTE: First run will do some OAuth stuff, you'll need to authorize it, this creates a unique `token.json` that handles the permission scopes.


## DONE!

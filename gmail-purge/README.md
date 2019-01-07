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
- then run See the examples below!
  - NOTE: First run will do some OAuth stuff, you'll need to authorize it, this creates a unique `token.json` that handles the permission scopes.

## DONE!

## Usage Examples:

This section assumes you've done the above installation steps, ie you have creds and a virtualenv

#### Example 1 - Gathering (semi-dry-run)
Say you're curious about how many email messages might be processed before running the archive/delete/trash portion, you can pass `-a gather` to `purge.py` and it will output how many pages of messages, and the total count of messages


```
> ./purge -a gather -q "label:my-special-label"

[I] Gathering Pages
[√] Total Page Count: 1
[√] Total Message Count: 11

```




#### Example 2 - Deleting some stuff

Gmail has this notion of "category" it's those neatly bundled things:
- Forums
- Promotions
- Social
- Updates

I never read those, so I targeted the `category:Forums` and chose anything `older_than:365d`
You can string the query along however you like, just be sure to wrap in Double-Quotes

As you can see in the output, it was a lot of messages `5803`.
This caught that and gave the option of processing in Bulk.

Both `delete` and `archive` have this feature, sadly `trash` does not...


```
> ./purge.py -a delete -q "older_than:36d AND category:Forums"

thering Pages
[√] Total Page Count: 59
[?] There are 5803 messages
[?] Would you like to process these in bulk? (Y/N): Y
[I] Processing in Bulk
[√] Bulk Action: SUCCESS 1000 Messages have been deleted! - 0
[√] Bulk Action: SUCCESS 1000 Messages have been deleted! - 1
[√] Bulk Action: SUCCESS 1000 Messages have been deleted! - 2
[√] Bulk Action: SUCCESS 1000 Messages have been deleted! - 3
[√] Bulk Action: SUCCESS 1000 Messages have been deleted! - 4
[√] Bulk Action: SUCCESS 803 Messages have been deleted! - 5
[√] Bulk Action: SUCCESS Total Number of Processed Messages: 5803
```



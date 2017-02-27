"""
Slack File Deletion Script
---------------------------------


*****  UNFINISHED ; STILL NEEDS SOME FINAL OAUTH TWEAKS  *****


Simple script used to clean up the files associated with your team's Slack account.

Used for general maintenance of the non-paid tiers of Slack, where the file size limits
can become obtrusive (especially for larger teams). This is the AWS version of the script,
meaning it's meant to be implemented with something like AWS Lambda or Google Cloud
Platform. Between Slack's slash commands, API Gateway, and AWS Lambda, this can be made
available to all users within your Slack team.

Since there isn't a way for an admin/owner of a Slack team to reach delete uploaded to
private messages, this is the easiest way to clean up your team's uploaded files. After
it's all set up, all you'd need to do is have your users enter "/files-delete" (or
whatever else you choose for the slash command) to clear out their files.

See the comments below for where to fill in your team's information, client ID/secret, 
and where you can impose filters on which files get deleted. Also, when you upload this
to Lambda/GCP, you'll need to include the libraries within the zip file for it to work.

Writen by Alex Melagrano
"""


# Imports / Setup
from slacker import Slacker
import requests
import sys
# from splinter import Browser
import mechanicalsoup
# import boto3
import json
# import logging

"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
"""

# Variables
CLIENT_ID = "..."               # client_id, found in Slack integration page
CLIENT_SECRET = "..."           # client_secret, found in Slack integration page
TEAM_NAME = "..."               # name of the team you're integrating this app into

EXPECTED_SLACK_TOKEN = "..."    # token unique to the slash command; confirms request came from Slack


# UX Print Statements
print("<-------------------------------------------------------->")
print("Beginning file deletion process. \n")

# Main function; give it the token, and it'll run its course
def file_delete(CLIENT_ID, CLIENT_SECRET, TEAM_NAME, EXPECTED_SLACK_TOKEN):
    
    # app authentication > get code > use code to get token > $profit$
        
    # App authorization - results in the code needed for the OAuth call
    authUrl = ("https://slack.com/oauth/authorize?")
    authUrlData = {
        "client_id": CLIENT_ID,
        "scope": "files:read files:write:user"
    }
    print("Built the authUrl, and making the GET request")
    authRequest = requests.get(authUrl, params=authUrlData)
    
    print("Made the auth request: status " + str(authRequest.status_code))
    if authRequest.status_code != 200:
        print("Something went wrong with the app authentication - here's the url it went to:")
        print(authRequest.url + "\n")
        sys.exit()
     
    print(authRequest.url + "\n")
    
    # Gets redirected to Slack's team login page - uses Selenium's webdriver to fill out and submit the webform
    print("Starting up the MechanicalSoup bit")
    browser = mechanicalsoup.Browser()

    print("Storing the page location")
    slack_page = browser.get(authRequest.url)
    print(slack_page.url + "\n")    
    
    print("Selecting the form element for the domain page")
    team_form = slack_page.soup.select("form")[0]
    
    print("Setting the team domain value to " + TEAM_NAME)
    team_form.select("#domain")[0]['value'] = TEAM_NAME
    
    print("Submitting the team domain form")
    auth_page = browser.submit(team_form, slack_page.url)
    print(auth_page.url + "\n")
    
    auth_page_2 = browser.get(auth_page.url)
    print(auth_page_2.url + "\n")
    
    # Provides the team domain, gets redirected to an authorization page
    print("Selecting the form element for the auth page")
    auth_form = auth_page_2.soup.select("form")[0]
    
    print("Submitting the authorization form")
    code_page = browser.submit(auth_form, auth_page_2.url)
    print(code_page.url + "\n")
    
#    with Browser() as browser:
#        # Go to the team login page, fill in the team field, then submit
#        browser.visit(authRequest.url)
#        print("Went to the url: \n" + authRequest.url + "\n")
#        
#        browser.fill('domain', TEAM_NAME)
#        print("Filled out the field")
#        
#        button = browser.find_by_id("submit_team_domain")
#        button.click()
#        
#        # Checks if the page actually loaded
#        if browser.is_text_present("This will allow File Deleter to"):
#            print("The little shit worked!")
#        else:
#            print("No good. Here's where we ended up: \n" + browser.url + "\n")
    
    # =========== TEMP EXIT ==============
    sys.exit()
    # =========== TEMP EXIT ==============
    
    
    # Splits the code off of the post-authorization url
    code = codeUrl.split("code=")[1].split("&")[0]
    print("Stored the code itself: " + code)
    
    
    # OAuth request - results in the API token
    tokenUrl = ("https://slack.com/api/oauth.access?")
    tokenUrlData = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }
    print("Built the tokenUrl")
    
    try:
        tokenRequest = requests.get(tokenUrl, params=tokenUrlData)
        print("Made the token request")
    except:
        print("Token request failed")
        sys.exit()
    
    # One token to rule them all!
    token = tokenRequest.json()["access_token"]
    print("Stored the token: " + token)
    
    # Pass it to Slacker - all API calls will be mad simple now
    slack = Slacker(token)
    
    
    # Gets a list of files available
    #  - optional filters include username, channel, timestamps before and after, file typs 
    #    (posts, snippits, images, google docs, zips, PDF's), and page/item restrictions
    fileQuery = slack.files.list()
    
    if fileQuery.body['ok']:
        print("Connected to the Slack API.")
        print("Status: ok")
        
        numFiles = fileQuery.body['paging']['total']   # total number of files
        numPages = fileQuery.body['paging']['pages']   # number of pages they take up, 100 files per
        allFiles = []                                  # list of all files
        problemFiles = []                              # list of files that couldn't be deleted
        curPage = 1                                    # page index
        
        while (curPage <= numPages):
            newFiles = slack.files.list(page=curPage).body['files']
            
            # Creates list of files, in order of their timestamp (oldest > newest)
            for file in newFiles:
                allFiles.insert(0, file)
                
            curPage += 1
            
        print("Retrieved and stored the files.")
        print("There are {} files available for deletion, across {} pages;").format(numFiles, numPages)

        # Iterate through list, deleting as many as the user specified
        if response == "y":
            print("Beginning file deletion; will notify on every 10% completed.")
            curFile = 1
            percent = 10

            for file in allFiles:
                curId = file['id']

                # File deletion call + error handling
                try:
                    resp = slack.files.delete(file_=curId)
                    print("Deleted file number {}, with ID ").format(curFile) + file['id'] + "\n"
                except:
                    print("File number {}, ID={}, couldn't be deleted.").format(curFile, curID)
                    problemFiles.append(curFile)

                if (curFile/numToDelete) >= percent:
                    print("=================== {}% complete ===================").format(percent)
                    percent += 10
                    
                curFile += 1

            print("\nFile deletion complete! {} files remaining, and {} couldn't be deleted.").format(fileQuery.body['paging']['total'], problemFiles)
            print("<-------------------------------------------------------->")

        if response == "n":
            print("File deletion exited.")
            print("<-------------------------------------------------------->")

        # error handling (ALWAYS CHECK FOR AN 'ok' RESPONSE):
        #  - file_not_found	    // The file does not exist, or is not visible to the calling user.
        #  - file_deleted	    // The file has already been deleted.
        #  - cant_delete_file	// Authenticated user does not have permission to delete this file.
        #  - not_authed	        // No authentication token provided.
        #  - invalid_auth	    // Invalid authentication token.
        #  - account_inactive	// Authentication token is for a deleted user or team.
        #  - invalid_arg_name	// The method was passed an argument whose name falls outside the bounds of common decency. This includes very long names and names with non-alphanumeric characters other than _. If you get this error, it is typically an indication that you have made a very malformed API call.
        #  - invalid_array_arg	// The method was passed a PHP-style array argument (e.g. with a name like foo[7]). These are never valid with the Slack API.
        #  - invalid_charset	// The method was called via a POST request, but the charset specified in the Content-Type header was invalid. Valid charset names are: utf-8 iso-8859-1.
        #  - invalid_form_data	//The method was called via a POST request with Content-Type application/x-www-form-urlencoded or multipart/form-data, but the form data was either missing or syntactically invalid.
        #  - invalid_post_type	// The method was called via a POST request, but the specified Content-Type was invalid. Valid types are: application/json application/x-www-form-urlencoded multipart/form-data text/plain.
        #  - missing_post_type	// The method was called via a POST request and included a data payload, but the request did not include a Content-Type header.
        #  - request_timeout	// The method was called via a POST request, but the POST data was either missing or truncated.
    
    else:
        print("Couldn't connect to the API. Make sure you used the right key, \nand have the correct permissions to access this.")
        
        
# Handles the Lambda function; takes POST request data, maps to file_delete function
def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != EXPECTED_SLACK_TOKEN:
        logger.error("Request token (%s) does not match the expected Slack token", token)
        return respond(Exception('Invalid request token'))

    print("Confirmed Slack token. Printing event params below.\n")
    
    user = params['user_name'][0]
    print("User: {}").format(user)
    command = params['command'][0]
    print("Command: {}").format(command)
    channel = params['channel_name'][0]
    print("Channel: {}").format(channel)
    command_text = params['text'][0]
    print("Command text: {}\n").format(command_text)
    
    # Calls main function; errors handled internally
    file_delete(CLIENT_ID, CLIENT_SECRET, EXPECTED_SLACK_TOKEN)
    
    return respond(None, "Process complete!")



# Runs the function
# file_delete( ... )


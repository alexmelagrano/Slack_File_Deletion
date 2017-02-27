"""
Slack Personal File Deletion Script
---------------------------------

Simple script used to clean up the files associated with your Slack account.

Used for general maintenance of the non-paid tiers of Slack, where the file size limits
can become obtrusive (especially for larger teams). Simply pass it your API token and it
will help you delete your uploaded files.

This is the test/personal version of the script, which runs off of a Slack Test API (and 
doesn't include the OAuth portion). This means that they key itself doesn't have the scope
to access the files of all team members, and therefore can only touch files that are within
your private messages, and anything in public channels.

Alternatively, if you have functioning OAuth code elsewhere and can provide this script with
your full API token, it can use that as well.

[ USE ] :: you'll need a test API, and it will prompt you for the rest!

Writen by Alex Melagrano
"""


# Imports
from slacker import Slacker
import sys

# Main function; give it the token, and it'll run its course
def file_delete(token):
    
    # Connecting to the API
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
            
        print("Retrieved and stored the files.\n")
        print("You have {} files available for deletion, across {} pages;").format(numFiles, numPages)
        
        # Prompts user for how many files they wish to delete
        # probably a better way to do this, but it works
        print("How many of them would you like to get rid of? It will start with the oldest files.\n")
        validQuantity = False
        numToDelete = 0
        while validQuantity == False:
            numToDelete = int(raw_input("# of files to delete: "))
            if numToDelete == 0:
                print("File deletion exited. Please rerun the script if this was a mistake.")
                print("<-------------------------------------------------------->")
                sys.exit()
            if numToDelete <= numFiles and numToDelete > 0:
                validQuantity = True
            else:
                print("Not a valid file amount - please enter a different number next time!")
            
        response = raw_input("Are you sure you want to delete {} files? y/n ").format(numToDelete)
        print("")

        # Iterate through list, deleting as many as the user specified
        if response == "y":
            print("Beginning file deletion; will notify upon completion.\n")
            curFile = 1

            for file in allFiles:
                curId = file['id']

                if curFile <= numToDelete:
                    print("Deleting file number {}, with ID ").format(curFile) + file['id'] + "\n"
                    # File deletion call + error handling
                    try:
                        resp = slack.files.delete(file_=curId)
                    except:
                        print("File number {}, ID={}, couldn't be deleted.").format(curFile, curID)
                        problemFiles.append(curFile)   
                curFile += 1

                filesLeft = numFiles - numToDelete + len(problemFiles)
            print("\nFile deletion complete! {} files remaining, and {} couldn't be deleted.").format(filesLeft, len(problemFiles))
            print("<-------------------------------------------------------->")

        if response == "n":
            print("File deletion exited. Please rerun the script if this was a mistake.")
            print("<-------------------------------------------------------->")

    else:
        print("Couldn't connect to the API. Make sure you used the right key, \nand have the correct permissions to access this.")
        
        
# UX Print Statements (prompts user for API key, initiates the file_delete function)
print("<-------------------------------------------------------->")
print("Trying to delete Slack files - if you'd like to proceed,")
print("enter your Slack API key below. \n")
key = raw_input("API key: ")
file_delete(key)
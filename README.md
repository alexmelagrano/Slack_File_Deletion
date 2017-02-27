# Slack File Deletion

A simple script to erase all files associated with your Slack account.

We all know that not every team has access to a paid tier of Slack, meaning the 5GB file limit will eventually become an issue. This is an easy solution to help you and your team to make the most of the free tier.


## Versions

__The ["personal" version](../slack_file_deleter_personal.py)__ is something you can run on your local machine, along with a test API, to delete the files within your private message threads, or any public channels. You can also run this with a full API token, though the OAuth code is not included.

__The ["aws" version](../slack_file_deleter_aws.py)__ is intended to be set up within an AWS Lambda function, which would be triggered by Slack's slash commands and the AWS API Gateway. For that, you'll need to include this code along with source files for the Slacker library in the zip file you upload into Lambda.

***

This script was built using [Slack's API](https://api.slack.com/) and [os' Slacker interface](https://github.com/os/slacker), which only requires a quick `pip install slacker` to get going. For any questions on how to set up the AWS portion of this, check out [Savjee's 9-part tutorial](https://www.youtube.com/playlist?list=PLzvRQMJ9HDiSQMe68cti8cupI0mzLk1Gc) on YouTube.

Developed at [MullenLowe](http://us.mullenlowe.com/)'s Boston office.
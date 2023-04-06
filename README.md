# twitter-web-app
Dash web app that utilizes the Twitter API to pull public tweet data based on the username and returns the tweet on hover.
Users will need to set their Twitter API token as the following environment variable: `TWITTERTOKEN`

![example_v2.gif](image_files%2Fexample_v2.gif)

## Usernames
comma-separated Twitter usernames without a space: google,amazon

## Start date
The start date of the request in yyyy-mm-dd format. This field is required.

## End date
The end date of the request in yyyy-mm-dd format. If null, will use today's date as the end date

## Deployment
The `Dockerfile` should be good enough to get you started with PaaS - i.e., Heroku, Render, Back4App, etc.

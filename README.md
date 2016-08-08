# [slack-to-mail](https://github.com/jamesperng/slack-to-mail/)

have mailing lists automatically created for each slack channel

### docker hub

https://hub.docker.com/r/jperng/slack-to-mail/

### Installation

#### Docker
  - If you don't have docker there are instructions [here](https://docs.docker.com/engine/installation/)
  - `docker pull jperng/slack-to-mail`

#### Python
  - If you don't have python you can install it [here](https://www.python.org/downloads/)
  - clone this repository

### Usage

#### Setup
  - You need to get a Slack auth token [here](https://api.slack.com/docs/oauth-test-tokens)
  - You need to get a Mailgun API Key: `https://mailgun.com/app/domains/<domain name>`
    - if you don't have a domain on mailgun, go here, click add a new domain, and follow the instructions.
  - Set your environment variables
    - `export SLACK_TOKEN=<slack auth token>`
    - `export MAILGUN_API_KEY=<mailgun api key>`

#### Docker
  - `docker run -e="SLACK_TOKEN=$SLACK_TOKEN" -e="MAILGUN_API_KEY=$MAILGUN_API_KEY" jperng/slack-to-mail <domain> <access level = readonly|members|everyone(default)>`

#### Python
  - `cd` into the repository
  - `python slack-grab.py <domain> <access level = readonly|members|everyone(default)>`

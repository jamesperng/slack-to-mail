from __future__ import print_function
import os
import sys
import requests
from slacker import Slacker

def create_map(slack):
    """
    Creates a dictionary mapping slack channel names to a list of channel members emails
    @slack(slacker.Slacker)=slacker.Slacker session from slacker auth token
    returns a dictionary{(string):[string]}
    """
    # get list of users
    print("gathering channels and emails from slack...")
    sys.stdout.flush()
    users = slack.users.list().body['members']

    # create dictionary mapping users to emails
    users_dict = {}
    for user in users:
        if 'email' in user['profile']:
            users_dict[user['id']] = user['profile']['email']

  # create dictionary mapping slack channels to email lists
    channels = slack.channels.list().body['channels']
    channel_dict = {}
    for i in channels:
        channel_dict[i['name']] = []
        for j in i['members']:
            if j in users_dict:
                channel_dict[i['name']].append("{\"address\": \"" + users_dict[j] + "\"}")
    return channel_dict

def add_list_members(name, emails, api_key, domain):
    """
    Adds all the recipient emails to the mailing list: <name>@<domain>
    @name(string)=name of the mailing list
    @emails[string]=recipient emails of the mailing list
    @api_key(string)=mailgun api key
    returns nothing
    """
    requests.post(
        "https://api.mailgun.net/v3/lists/" + name + "@" + domain + "/members.json",
        auth=('api', api_key),
        data={'upsert': True,
              'members': "[" + ", ".join(emails) + "]"})
    print("{0:50}{1}@{2}".format("updated mail recipients for:", name, domain))
    sys.stdout.flush()

def update_mailing_list(name, api_key, domain, default_access_level="everyone"):
    """
    Updates a mailing list for <name>@<domain>
    @name(string)=name of the mailing list
    @api_key(string)=mailgun api key
    returns nothing
    """
    requests.put(
        "https://api.mailgun.net/v3/lists/" + name + "@" + domain,
        auth=('api', api_key),
        data={'access_level': default_access_level})
    print("{0:50}{1}@{2}".format("updated mailing list:", name, domain))
    sys.stdout.flush()

def create_mailing_list(name, emails, api_key, domain, default_access_level="everyone"):
    """
    Creates a mailing list for <name>@<domain>
    if the mailing list already exists, updates the mailing list
    @name(string)=name of the mailing list
    @emails[string]=recipient emails of mailing list
    @api_key(string)=mailgun api key
    returns nothing
    """
    resp = requests.post(
        "https://api.mailgun.net/v3/lists",
        auth=('api', api_key),
        data={'address': name+'@' + domain,
              'access_level': default_access_level})
    if b"Duplicate object" in resp.content:
        update_mailing_list(name, api_key, domain)
    else:
        print("{0:50}{1}@{2}".format("created mailing list:", name, domain))
        sys.stdout.flush()
    add_list_members(name, emails, api_key, domain)


def run(domain):
    """
    Gets map fo slack channel names to channel member emails
    Creates a mailing list for each channel name to its channel members
    returns nothing
    """
    if domain == "--help":
        print("{0:20}{1}\n".format("Usage:", " python slack-grab.py <domain name> <access level>"))
        print("{0:20}{1}\n".format("Docker Usage:", " docker run -e=\"SLACK_TOKEN=<slack auth token>\" -e=\"MAILGUN_API_KEY=<mailgun api key>\" jperng/slack-to-mail <domain name> <access level>"))
        print("{0:21}{1}".format("", "valid access levels are: readonly|members|everyone(default)"))
        return
    slack_auth_token = os.environ.get('SLACK_TOKEN')
    if len(slack_auth_token) == 0:
        print("missing $SLACK_TOKEN environment variable")
        return
    slack = Slacker(slack_auth_token)
    stm_map = create_map(slack)
    mg_api_key = os.environ.get('MAILGUN_API_KEY')
    if len(mg_api_key) == 0:
        print("missing $MAILGUN_API_KEY environment variable")
        return
    if len(sys.argv) > 2:
        if sys.argv[2] in ["readonly", "members", "everyone"]:
            for name, emails in stm_map.items():
                create_mailing_list(name, emails, mg_api_key, domain, sys.argv[4])
        else:
            print("invalid access level: {0}".format(sys.argv[2]))
            print("valid access levels are: readonly|members|everyone")
            return
    else:
        for name, emails in stm_map.items():
            create_mailing_list(name, emails, mg_api_key, domain)

if len(sys.argv) < 2:
    print("Error: missing domain name")
    print("add --help flag for usage")
else:
    run(sys.argv[1])

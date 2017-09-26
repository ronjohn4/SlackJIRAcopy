import os
import time
import requests
import json
from slackclient import SlackClient


BOT_ID = os.environ.get("BOT_ID")
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
AT_BOT = "<@" + BOT_ID + ">"


def CreateIssue(project, summary, description):
    payload = {
        "fields": {
            "project":
                {
                    "key": project
                },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Story"
            }
        }
    }
    url = 'https://levelsbeyond.atlassian.net/rest/api/2/issue/'
    response = requests.post(url, data=json.dumps(payload), auth=GetAuth(), headers={'content-type':'application/json'})

    if response.status_code == 201:
        return True
    else:
        return False


def GetKey(key):
    url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?jql=key={0}'.format(key)
    r = requests.get(url, auth=GetAuth())
    json_return = json.loads(r.text)

    if 'total' in json_return and json_return['total'] == 1:
        return json_return['issues'][0]
    else:
        return False


def VerifyProject(project):
    url = 'https://levelsbeyond.atlassian.net/rest/api/2/project/{0}'.format(project)
    r = requests.get(url, auth=GetAuth())
    json_return = json.loads(r.text)

    if 'key' in json_return and json_return['key'] == project:
        return True
    else:
        return False

def ParseParms(parms):
    parmlist = parms.split()
    if len(parmlist) == 2:
        return parmlist[0], parmlist[1]
    else:
        return None, None


def GetAuth():
    return ('username', 'password')


def handle_command(command, channel):
    key, project = ParseParms(command)

    if key:
        if project and VerifyProject(project):
            sourceissue = GetKey(key)
            if sourceissue:
                summary = sourceissue['key'] + ' - ' + sourceissue['fields']['summary']
                description = sourceissue['fields']['description']

                if CreateIssue(project, summary, description):
                    response = 'Key {0} duplicated into project {1}!'.format(key, project)
                else:
                    response = 'sorry... key {0} could NOT be duplicated into project {1}'.format(key, project)
            else:
                response = 'sorry... key {0} not found.'.format(key)
        else:
            response = 'sorry... target project {0} not found.'.format(project)
    else:
        response = 'sorry... I don''t understand the  request (e.g. @jiracp key project)'


    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().upper(), output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        print("JIRAcp connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
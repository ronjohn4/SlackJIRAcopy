import requests
import json


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
    return False



def GetKey(key):
    url = 'https://levelsbeyond.atlassian.net/rest/api/2/search?jql=key={0}'.format(key)
    r = requests.get(url, auth=GetAuth())
    json_return = json.loads(r.text)

    if 'total' in json_return and json_return['total'] == 1:
        return json_return['issues'][0]
    return False


def VerifyProject(project):
    url = 'https://levelsbeyond.atlassian.net/rest/api/2/project/{0}'.format(project)
    r = requests.get(url, auth=GetAuth())
    json_return = json.loads(r.text)

    if 'key' in json_return and json_return['key'] == project:
        return True
    return False

def ParseParms(parms):
    parmlist = parms.split()
    if len(parmlist) == 2:
        return parmlist[0], parmlist[1]
    return None, None


def GetAuth():
    return ('rjohnson', 'Miter9le')



if __name__ == "__main__":
    # # test VerifyKey()
    # print('key=ABC-8282:', GetKey('ABC-8282'))
    # print('key=no-key:', GetKey('no-key'))
    #
    # # test VerifyProject()
    # print('project=ABC:', VerifyProject('ABC'))
    # print('project=DEF:', VerifyProject('DEF'))
    #
    # # test ParseParms()
    # print('BAD:', ParseParms('BAD'))
    # print('TOO MANY PARMS:', ParseParms('TOO MANY PARMS'))
    # print(':', ParseParms(''))
    # print('ABC-8282 UXT:', ParseParms('ABC-8282 UXT'))


    key, project = ParseParms('ABC-8282 UXT')
    print(key)
    print(project)

    if key == None:
        print('@jiracp key project')

    sourceissue = GetKey(key)
    if sourceissue == None:
        print('Source key {0} not found.'.format(key))

    print(sourceissue)

    summary = sourceissue['key'] + ' - ' + sourceissue['fields']['summary']
    description = sourceissue['fields']['description']

    CreateIssue(project,summary,description)


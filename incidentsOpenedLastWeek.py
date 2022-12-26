"""
Jira API calls to get all the incidents opened last week
    - The returned list of incidents is parsed to extract all the interesting data
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# Prepare the accumulators
incidentsByAssignee={}
incidentsByStatus={}
incidentsByApplication={}
incidentsByTier={}
incidentsBySeverity={}
incidentsByOperation={}
incidentsByOperationAndApplication={}
 
jiraToken = input("Enter the Jira Token String: ")
url = "https://salto-io.atlassian.net/rest/api/3/search"
auth = HTTPBasicAuth("jonah.pressman@salto.io",jiraToken)
headers = {
  "Accept": "application/json", 
  "Content-Type": "application/json"
}

# Configure the data body of the request to get the number of incident issues opened last week
# This is to calculate the iterations for pagination and offsets for each iteration.
payload = json.dumps( {
  'jql': 'project = INCIDENT AND created >= startOfWeek(-7d) AND created <= endOfWeek(-7d)',
  'startAt': 0,
  'maxResults': 0,
  'fieldsByKeys': False,
  'fields': [
    "status"]
})

response = requests.request(
  "POST",
  url,
  data=payload,
  headers=headers,
  auth=auth
)

formattedOutput = json.loads(response.text)
totalIncidentsOpenedLastWeek = formattedOutput["total"]

# We are going to retrieve 100 incident issues with each call 
for apiCallIteration in range(0,totalIncidentsOpenedLastWeek,100):
  #
  # customfield_10058 is orgTier
  # customfield_10046 is Incident Severity
  #
  payload = json.dumps( {
  'jql': 'project = INCIDENT AND created >= startOfWeek(-7d) AND created <= endOfWeek(-7d)',
  'startAt': apiCallIteration,
  'maxResults': 100,
  'fieldsByKeys': False,
  'fields': [
    "assignee",
    "labels",
    "description",
    "customfield_10058",
    "customfield_10046",
    "summary",
    "status"] 
  })

  response = requests.request(
    "POST",
    url,
    data=payload,
    headers=headers,
    auth=auth
  )

  formattedOutput = json.loads(response.text)

  # Loop through each incident issue and collect the relevant details
  for iteration in range(0,len(formattedOutput["issues"])):
    essentialData = formattedOutput["issues"][iteration]
    fieldsInfo = essentialData["fields"]

    # Assignee
    assigneeInfo = fieldsInfo["assignee"]
    assigneeName = assigneeInfo["displayName"]
    if assigneeName not in incidentsByAssignee.keys():
      incidentsByAssignee[assigneeName] = 1
    else:
      incidentsByAssignee[assigneeName] +=1
        
    # Status
    statusInfo = fieldsInfo["status"]
    statusText = statusInfo["name"]
    if statusText not in incidentsByStatus.keys():
      incidentsByStatus[statusText] = 1
    else:
      incidentsByStatus[statusText] +=1
    
    # Application
    issueLabels = fieldsInfo["labels"]
    issueApplication = "Unknown"
    for labelIteration in range(0,len(issueLabels)-1):
      if "application:" in issueLabels[labelIteration]:
        issueApplication = issueLabels[labelIteration].split(":")[1]
        break
    if issueApplication not in incidentsByApplication.keys():
      incidentsByApplication[issueApplication] = 1
    else:
      incidentsByApplication[issueApplication] +=1
    
    # orgTier is a custom field - found in DevTools customfield_10058
    if fieldsInfo["customfield_10058"]:
      orgTierCustomField = fieldsInfo["customfield_10058"]
      orgTierName = orgTierCustomField["value"]
    else:
      orgTierName = "Unknown"
    if orgTierName not in incidentsByTier.keys():
      incidentsByTier[orgTierName] = 1
    else:
      incidentsByTier[orgTierName] +=1
    
    # Incident Severity is a custom field - found in DevTools customfield_10046
    if fieldsInfo["customfield_10046"]:
      severityCustomField = fieldsInfo["customfield_10046"]
      incidentSeverity = severityCustomField["value"]
    else:
      incidentSeverity = "Unknown"
    if incidentSeverity not in incidentsBySeverity.keys():
      incidentsBySeverity[incidentSeverity] = 1
    else:
      incidentsBySeverity[incidentSeverity] +=1
    
    # Activity
    if fieldsInfo["description"]:
      issueDescription = fieldsInfo["description"]
      issueDescriptionContent = issueDescription["content"]
      issueDescriptionContentDeep = issueDescriptionContent[0]
      issueDigDeeper = issueDescriptionContentDeep["content"]
      issueActivity = ""
      for textIteration in range(0,len(issueDigDeeper)):
        if issueDigDeeper[textIteration]["type"] == "text":
          issueDigDeepest = issueDigDeeper[textIteration]
          issueDetailText = issueDigDeepest["text"]
          if "Operation Type:" in issueDetailText:
            issueActivity = issueDetailText
            break
          if "scheduled-operation" in issueDetailText:
            issueActivity = "Operation Type: FETCH"
            break
    else:
      issueActivity= "Blank Issue Description"  
    if "Operation Type: FETCH" in issueActivity:
      issueOperationType = "FETCH"
    elif "Operation Type: DEPLOY" in issueActivity:
      issueOperationType = "DEPLOY"
    elif "Operation Type: PUSH" in issueActivity:
      issueOperationType = "PUSH"
    else:
      issueOperationType = "Unknown"
    if issueOperationType not in incidentsByOperation.keys():
      incidentsByOperation[issueOperationType] = 1
    else:
      incidentsByOperation[issueOperationType] +=1
        
    # Operation and Application
    oaKeyName = issueOperationType + "-" + issueApplication
    if oaKeyName not in incidentsByOperationAndApplication.keys():
      incidentsByOperationAndApplication[oaKeyName] = 1
    else:
      incidentsByOperationAndApplication[oaKeyName] +=1


# Interim Stats - not yet formatted
# print()
# print("Total Number of Incidents opened last week: ",formattedOutput["total"])
# print("IBAss = " + str(incidentsByAssignee))
# print("IBS = " + str(incidentsByStatus))
# print("IBApp = " + str(incidentsByApplication))
# print("IBT = " + str(incidentsByTier))
# print("IBSev = " + str(incidentsBySeverity))
# print("IBO = " + str(incidentsByOperation))
# print("IBOaA = " + str(incidentsByOperationAndApplication))

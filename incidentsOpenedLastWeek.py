"""
Jira API calls to get all the incidents opened last week
    - The returned list of incidents is parsed to extract all the interesting data
"""

import requests
from requests.auth import HTTPBasicAuth
import json

jiraToken = input("Enter the Jira Token String: ")
authString = "jonah.pressman@salto.io:"+jiraToken+"@"
url = "https://"+authString+"salto-io.atlassian.net/rest/api/3/search"
#auth = HTTPBasicAuth("jonah.pressman@salto.io", "jiraToken")

headers = {
  "Accept": "application/json"
}

query = {
  'jql': 'project = INCIDENT AND created >= startOfWeek(-7d) AND created <= endOfWeek(-7d)',
  'fieldsByKeys':False,
  'fields': [
    "assignee",
    "labels",
    "description",
    "customfield_10058",
    "summary"]
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query
)

formattedOutput = json.loads(response.text)
print("Total Number of Incidents opened last week: ",formattedOutput["total"])

# maximum number of results per call is 50
# take the number of total incidents and divide it by 50
# subtract 1 because the first call has already been made
# if not exaclty divisible by 50, add another iteration
# the result will be the number of additional calls to make


#Debug
#print (len(formattedOutput["issues"]))

for iteration in range(0,len(formattedOutput["issues"])):
  print("--------")
  print(str(iteration))
  #print(formattedOutput["issues"][iteration])
  essentialData = formattedOutput["issues"][iteration]
  issueKey = essentialData["key"]
  print ("Issue - " + issueKey) 
  
  fieldsInfo = essentialData["fields"]
  assigneeInfo = fieldsInfo["assignee"]
  assigneeName = assigneeInfo["displayName"]
  print ("Assigned to - " + assigneeName)
  
  issueLabels = fieldsInfo["labels"]
  issueApplication = "Unknown"
  for labelIteration in range(0,len(issueLabels)-1):
    if "application:" in issueLabels[labelIteration]:
      issueApplication = issueLabels[labelIteration].split(":")[1]
      break
  print ("Application - " + issueApplication)
  
  # orgTier is a custom field - found in DevTools customfield_10058
  if fieldsInfo["customfield_10058"]:
    orgTierCustomField = fieldsInfo["customfield_10058"]
    orgTierName = orgTierCustomField["value"]
  else:
    orgTierName = "Unknown"
  print ("Tier - " + orgTierName)
  
  if fieldsInfo["description"]:
    issueDescription = fieldsInfo["description"]
    issueDescriptionContent = issueDescription["content"]
    issueDescriptionContentDeep = issueDescriptionContent[0]
    issueDigDeeper = issueDescriptionContentDeep["content"]
    issueActivity = ""
    for textIteration in range(0,len(issueDigDeeper),2):
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
  print ("Operation Type - " + issueOperationType)
   
  #print (descriptionContent)
  #print (len(descriptionContent))

  input()
  
  #still need to deal with severity and then compile the stats.
  
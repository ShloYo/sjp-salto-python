"""
Get a CSM for a given customer e-mail address.
Lookup the e-mail address of the customer
From the customer infromation, get the customer organization
From the customer organization, extract the CSM information and name
All this using Vitally API calls.
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
import os

# Load environment variable(s) from file
load_dotenv()
vitallyApiToken = os.getenv("VITALLY_TOKEN")
vitallyAuthHeader = os.getenv("VITALLY_AUTH_HEADER")

customerEmailAddress = input("Enter the e-mail address of the customer: ")
print (customerEmailAddress)

url = "https://rest.vitally.io/resources/users"
headers = {
    "Accept": "application/json", 
    "Content-Type": "application/json"
}  
auth = HTTPBasicAuth(vitallyAuthHeader)
response = requests.get(
    url,
    headers,
    auth
)

print (response)

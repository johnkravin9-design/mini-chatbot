import requests
import json

# Test the reports API directly
response = requests.get('http://localhost:8000/api/admin/reports')
print("Status Code:", response.status_code)
print("Response:", response.json())

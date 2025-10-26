import requests
import json
import time

# Wait for server to be ready
time.sleep(2)

print("=== Creating Test Reports ===")

# First, login as admin to check current state
print("1. Checking admin access...")
try:
    login_data = {"username": "admin", "password": "any"}
    response = requests.post('http://localhost:8000/api/login', json=login_data)
    print("Admin login:", response.json().get('success', False))
    
    # Check current reports
    reports_response = requests.get('http://localhost:8000/api/admin/reports')
    if reports_response.status_code == 200:
        reports_data = reports_response.json()
        print(f"Current reports: {len(reports_data.get('reports', []))}")
        
        # If no reports, create some test ones
        if len(reports_data.get('reports', [])) == 0:
            print("2. Creating test reports...")
            
            # Login as regular user first
            user_login = {"username": "johnkravin", "password": "any"}
            user_response = requests.post('http://localhost:8000/api/login', json=user_login)
            
            if user_response.json().get('success'):
                # Create multiple test reports
                test_reports = [
                    {"target_type": "post", "target_id": 1, "report_type": "spam", "description": "This looks like automated content"},
                    {"target_type": "post", "target_id": 2, "report_type": "inappropriate_content", "description": "Content violates community guidelines"}
                ]
                
                for i, report_data in enumerate(test_reports):
                    report_response = requests.post('http://localhost:8000/api/report', json=report_data)
                    print(f"Report {i+1}: {report_response.json().get('success', False)}")
                
                print("3. Test reports created! Now check /admin/reports")
            else:
                print("Could not login as test user")
        else:
            print("Reports already exist, no need to create test data")
            
except Exception as e:
    print(f"Error: {e}")
    print("Make sure the server is running on http://localhost:8000")

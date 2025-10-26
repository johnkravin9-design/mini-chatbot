import requests
import json

def check_all_data():
    print("=== Aura Platform Data Diagnostic ===")
    
    # Check if server is running
    try:
        # Check stats
        stats_response = requests.get('http://localhost:8000/api/admin/stats')
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print("✅ Server is running")
            print(f"📊 Stats: {stats.get('stats', {})}")
        else:
            print("❌ Cannot access stats")
            return
    except:
        print("❌ Server not running or inaccessible")
        return
    
    # Check reports
    try:
        reports_response = requests.get('http://localhost:8000/api/admin/reports')
        if reports_response.status_code == 200:
            reports = reports_response.json()
            report_count = len(reports.get('reports', []))
            print(f"📋 Reports found: {report_count}")
            
            if report_count > 0:
                for i, report in enumerate(reports['reports']):
                    print(f"  {i+1}. {report['report_type']} - {report['status']}")
            else:
                print("  No reports in database")
        else:
            print("❌ Cannot access reports")
    except Exception as e:
        print(f"❌ Error checking reports: {e}")
    
    # Check users
    try:
        users_response = requests.get('http://localhost:8000/api/admin/users')
        if users_response.status_code == 200:
            users = users_response.json()
            user_count = len(users.get('users', []))
            print(f"👥 Users found: {user_count}")
        else:
            print("❌ Cannot access users")
    except Exception as e:
        print(f"❌ Error checking users: {e}")

check_all_data()

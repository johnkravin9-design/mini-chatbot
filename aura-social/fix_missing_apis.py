import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Check if reporting APIs exist
if '/api/report/types' not in content:
    print("Adding missing reporting APIs...")
    
    # Find a good place to insert the reporting APIs (after messaging APIs)
    insertion_point = '# Reporting APIs and other existing APIs remain the same...'
    
    if insertion_point in content:
        reporting_apis = '''
# Reporting APIs
@app.route('/api/report', methods=['POST'])
def create_report():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    data = request.json
    target_type = data.get('target_type')  # 'post' or 'user'
    target_id = data.get('target_id')
    report_type = data.get('report_type')
    description = data.get('description', '').strip()
    
    if not all([target_type, target_id, report_type]):
        return jsonify({"success": False, "error": "Missing required fields"})
    
    # Validate target exists
    if target_type == 'post':
        target = get_post_by_id(target_id)
    else:  # user
        target = get_user_by_id(target_id)
    
    if not target:
        return jsonify({"success": False, "error": "Target not found"})
    
    global report_id_counter
    new_report = Report(report_id_counter, session['user_id'], target_type, target_id, report_type, description)
    report_id_counter += 1
    
    reports_db.append(new_report)
    return jsonify({"success": True, "report": new_report.to_dict()})

@app.route('/api/report/types')
def get_report_types():
    types = [{"value": rt.value, "label": rt.value.replace('_', ' ').title()} for rt in ReportType]
    return jsonify({"success": True, "types": types})

# Post APIs
@app.route('/api/posts')
def get_posts():
    if is_admin():
        return jsonify(posts_db)
    else:
        approved_posts = [post for post in posts_db if post.get('is_approved', True)]
        return jsonify(approved_posts)

@app.route('/api/add_post', methods=['POST'])
def add_post():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    data = request.json
    user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
    
    if user and data.get('content'):
        new_post = {
            "post_id": len(posts_db) + 1,
            "user_id": user.user_id,
            "username": user.username,
            "display_name": user.display_name,
            "avatar": user.avatar,
            "content": data['content'],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reactions": {"like": 0},
            "comments": [],
            "is_approved": user.is_admin()
        }
        posts_db.append(new_post)
        return jsonify({"success": True, "post": new_post})
    
    return jsonify({"success": False, "error": "Invalid data"})

@app.route('/api/react/<int:post_id>', methods=['POST'])
def react_to_post(post_id):
    data = request.json
    reaction_type = data.get('reaction', 'like')
    
    for post in posts_db:
        if post['post_id'] == post_id and post.get('is_approved', True):
            if reaction_type in post['reactions']:
                post['reactions'][reaction_type] += 1
            else:
                post['reactions'][reaction_type] = 1
            return jsonify({"success": True, "reactions": post['reactions']})
    
    return jsonify({"success": False, "error": "Post not found"})
'''
        
        content = content.replace(insertion_point, insertion_point + reporting_apis)
        
        with open('app.py', 'w') as f:
            f.write(content)
        print("✅ Missing APIs added successfully!")
    else:
        print("❌ Could not find insertion point")
else:
    print("✅ Reporting APIs already exist")

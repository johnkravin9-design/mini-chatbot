import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Find where to insert the context processor (after socketio initialization)
# Look for the socketio line and insert context processor after it
socketio_pattern = r"(socketio = SocketIO\(app, cors_allowed_origins=\"\*\"\))"

replacement = r'''\1

# Context processor to make current_user available in all templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
        if user:
            return {'current_user': user.to_dict()}
    return {'current_user': None}
'''

# Replace the content
new_content = re.sub(socketio_pattern, replacement, content)

# Write the updated content back
with open('app.py', 'w') as f:
    f.write(new_content)

print("✅ Context processor added successfully!")

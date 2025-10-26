import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import datetime
from enum import Enum

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aura-social-secret-key-2024')
socketio = SocketIO(app, cors_allowed_origins="*")

# Context processor to make current_user available in all templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
        if user:
            return {'current_user': user.to_dict()}
    return {'current_user': None}

# [YOUR EXISTING CODE CONTINUES...]
socketio = SocketIO(app, cors_allowed_origins="*")

# [PASTE YOUR ENTIRE CURRENT app.py CONTENT HERE]
# But replace the secret key line with the one above

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import datetime
import hashlib
import os
from enum import Enum

app = Flask(__name__)
app.secret_key = 'aura_social_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Context processor to make current_user available in all templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
        if user:
            return {'current_user': user.to_dict()}
    return {'current_user': None}


# Enums for better structure
class ReportStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class ReportType(Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    FALSE_INFORMATION = "false_information"
    OTHER = "other"

class MessageStatus(Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"

# Databases
users_db = {}
posts_db = []
reports_db = []
conversations_db = {}
user_id_counter = 1
report_id_counter = 1
message_id_counter = 1

class User:
    def __init__(self, user_id, username, email, display_name, bio="", avatar="👤", role="user"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.display_name = display_name
        self.bio = bio
        self.avatar = avatar
        self.role = role
        self.joined_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.following = []
        self.followers = []
        self.is_active = True
        self.warning_count = 0
        self.is_online = False
        self.last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "bio": self.bio,
            "avatar": self.avatar,
            "role": self.role,
            "joined_date": self.joined_date,
            "following_count": len(self.following),
            "followers_count": len(self.followers),
            "is_active": self.is_active,
            "warning_count": self.warning_count,
            "is_online": self.is_online,
            "last_seen": self.last_seen
        }

    def is_admin(self):
        return self.role == "admin"

class Report:
    def __init__(self, report_id, reporter_id, target_type, target_id, report_type, description):
        self.report_id = report_id
        self.reporter_id = reporter_id
        self.target_type = target_type
        self.target_id = target_id
        self.report_type = report_type
        self.description = description
        self.status = ReportStatus.PENDING.value
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.resolved_at = None
        self.resolved_by = None
        self.action_taken = None

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "reporter_id": self.reporter_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "report_type": self.report_type,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolved_by": self.resolved_by,
            "action_taken": self.action_taken
        }

class Message:
    def __init__(self, message_id, conversation_id, sender_id, content, message_type="text"):
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = MessageStatus.SENT.value
        self.read_by = []

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "status": self.status,
            "read_by": self.read_by
        }

class Conversation:
    def __init__(self, conversation_id, participants, conversation_type="direct"):
        self.conversation_id = conversation_id
        self.participants = participants  # list of user_ids
        self.conversation_type = conversation_type
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_message_at = self.created_at
        self.last_message = None
        self.messages = []

    def to_dict(self):
        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "conversation_type": self.conversation_type,
            "created_at": self.created_at,
            "last_message_at": self.last_message_at,
            "last_message": self.last_message.to_dict() if self.last_message else None,
            "unread_count": len([m for m in self.messages if m.status != MessageStatus.READ.value])
        }

# Initialize sample data
def initialize_sample_data():
    global user_id_counter, report_id_counter, message_id_counter
    
    # Create admin and sample users
    admin_user = User(user_id_counter, "admin", "admin@aura.social", "Aura Administrator", 
                     "Platform Administrator", "👑", "admin")
    user_id_counter += 1
    
    user1 = User(user_id_counter, "johnkravin", "john@aura.social", "John Kravin", 
                 "Building the future of social media 🚀", "👨‍💻")
    user_id_counter += 1
    user2 = User(user_id_counter, "auratech", "tech@aura.social", "Aura Team", 
                 "Creating intelligent social experiences", "🤖")
    user_id_counter += 1
    
    users_db[admin_user.username] = admin_user
    users_db[user1.username] = user1
    users_db[user2.username] = user2
    
    # Sample posts
    posts_db.extend([
        {
            "post_id": 1,
            "user_id": user1.user_id,
            "username": user1.username,
            "display_name": user1.display_name,
            "avatar": user1.avatar,
            "content": "Building the future of social media with Aura! 🚀\n\nThis platform will change how we connect online.",
            "timestamp": "2024-01-15 10:30:00",
            "reactions": {"like": 5, "love": 2, "insightful": 3},
            "comments": [
                {"username": "auratech", "display_name": "Aura Team", "text": "This is revolutionary!", "timestamp": "2024-01-15 10:35:00"}
            ],
            "is_approved": True
        },
        {
            "post_id": 2,
            "user_id": user2.user_id,
            "username": user2.username,
            "display_name": user2.display_name,
            "avatar": user2.avatar,
            "content": "Aura Features:\n• Real-time Messaging\n• Smart Reporting System\n• Advanced Moderation\n• User Protection",
            "timestamp": "2024-01-15 09:15:00",
            "reactions": {"like": 8, "excited": 5, "curious": 4},
            "comments": [],
            "is_approved": True
        }
    ])
    
    # Sample conversations
    conv1 = Conversation("1_2", [user1.user_id, user2.user_id])
    conversations_db["1_2"] = conv1
    
    # Sample messages
    msg1 = Message(message_id_counter, "1_2", user1.user_id, "Hey Aura Team! I'm excited about building this platform together!")
    message_id_counter += 1
    msg2 = Message(message_id_counter, "1_2", user2.user_id, "We're excited too! The real-time messaging feature is going to be amazing! 🚀")
    message_id_counter += 1
    
    conv1.messages.extend([msg1, msg2])
    conv1.last_message = msg2
    conv1.last_message_at = msg2.timestamp

initialize_sample_data()

def is_admin():
    if 'user_id' in session:
        user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
        return user and user.is_admin()
    return False

def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return jsonify({"success": False, "error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def get_user_by_id(user_id):
    return next((u for u in users_db.values() if u.user_id == user_id), None)

def get_post_by_id(post_id):
    return next((p for p in posts_db if p['post_id'] == post_id), None)

def get_conversation_id(user1_id, user2_id):
    return f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

def get_or_create_conversation(user1_id, user2_id):
    conversation_id = get_conversation_id(user1_id, user2_id)
    if conversation_id not in conversations_db:
        conversations_db[conversation_id] = Conversation(conversation_id, [user1_id, user2_id])
    return conversations_db[conversation_id]

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        if user:
            user.is_online = True
            user.last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            emit('user_online', {'user_id': user_id, 'is_online': True}, broadcast=True)
            print(f"User {user.username} connected")

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        if user:
            user.is_online = False
            user.last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            emit('user_offline', {'user_id': user_id, 'is_online': False}, broadcast=True)
            print(f"User {user.username} disconnected")

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    join_room(conversation_id)
    print(f"User joined conversation: {conversation_id}")

@socketio.on('send_message')
def handle_send_message(data):
    global message_id_counter
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    
    if 'user_id' not in session:
        return
    
    sender_id = session['user_id']
    conversation = conversations_db.get(conversation_id)
    
    if conversation and sender_id in conversation.participants:
        # Create new message
        new_message = Message(message_id_counter, conversation_id, sender_id, content)
        message_id_counter += 1
        
        # Add to conversation
        conversation.messages.append(new_message)
        conversation.last_message = new_message
        conversation.last_message_at = new_message.timestamp
        
        # Broadcast to all participants in the conversation room
        message_data = {
            'message': new_message.to_dict(),
            'conversation_id': conversation_id,
            'sender': get_user_by_id(sender_id).to_dict()
        }
        
        emit('new_message', message_data, room=conversation_id)
        print(f"Message sent in conversation {conversation_id}: {content}")

@socketio.on('typing_start')
def handle_typing_start(data):
    conversation_id = data.get('conversation_id')
    user = get_user_by_id(session['user_id'])
    if user:
        emit('user_typing', {
            'conversation_id': conversation_id,
            'user_id': user.user_id,
            'username': user.username,
            'is_typing': True
        }, room=conversation_id, include_self=False)

@socketio.on('typing_stop')
def handle_typing_stop(data):
    conversation_id = data.get('conversation_id')
    user = get_user_by_id(session['user_id'])
    if user:
        emit('user_typing', {
            'conversation_id': conversation_id,
            'user_id': user.user_id,
            'username': user.username,
            'is_typing': False
        }, room=conversation_id, include_self=False)

@app.route('/')
def home():
    if 'user_id' in session:
        if is_admin():
            return redirect('/admin')
        return render_template('feed.html')
    return render_template('auth.html')

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('messages.html')

@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect('/')
    return render_template('admin_dashboard.html')

@app.route('/admin/reports')
def admin_reports():
    if not is_admin():
        return redirect('/')
    return render_template('admin_reports.html')

@app.route('/profile/<username>')
def profile(username):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user = users_db.get(username)
    if not user:
        return "User not found", 404
    
    user_posts = [post for post in posts_db if post['username'] == username and post.get('is_approved', True)]
    return render_template('profile.html', user=user.to_dict(), posts=user_posts)

@app.route('/my_profile')
def my_profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
    if user:
        user_posts = [post for post in posts_db if post['user_id'] == user.user_id and post.get('is_approved', True)]
        return render_template('profile.html', user=user.to_dict(), posts=user_posts, is_own_profile=True)
    return redirect(url_for('home'))

# Authentication APIs
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip().lower()
    email = data.get('email', '').strip().lower()
    display_name = data.get('display_name', '').strip()
    password = data.get('password', '')
    
    if not all([username, email, display_name, password]):
        return jsonify({"success": False, "error": "All fields are required"})
    
    if username in users_db:
        return jsonify({"success": False, "error": "Username already exists"})
    
    global user_id_counter
    new_user = User(user_id_counter, username, email, display_name)
    user_id_counter += 1
    
    users_db[username] = new_user
    
    session['user_id'] = new_user.user_id
    session['username'] = new_user.username
    
    return jsonify({"success": True, "user": new_user.to_dict()})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    
    user = users_db.get(username)
    if user and user.is_active:
        session['user_id'] = user.user_id
        session['username'] = user.username
        return jsonify({"success": True, "user": user.to_dict()})
    
    return jsonify({"success": False, "error": "Invalid credentials"})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/current_user')
def current_user():
    if 'user_id' in session:
        user = next((u for u in users_db.values() if u.user_id == session['user_id']), None)
        if user:
            return jsonify({"success": True, "user": user.to_dict()})
    return jsonify({"success": False})

# Messaging APIs
@app.route('/api/conversations')
def get_conversations():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    user_id = session['user_id']
    user_conversations = []
    
    for conv in conversations_db.values():
        if user_id in conv.participants:
            conv_data = conv.to_dict()
            # Add participant details
            other_participant_id = [pid for pid in conv.participants if pid != user_id][0]
            other_user = get_user_by_id(other_participant_id)
            conv_data['other_user'] = other_user.to_dict() if other_user else None
            user_conversations.append(conv_data)
    
    return jsonify({"success": True, "conversations": user_conversations})

@app.route('/api/conversation/<conversation_id>')
def get_conversation(conversation_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    conversation = conversations_db.get(conversation_id)
    if not conversation or session['user_id'] not in conversation.participants:
        return jsonify({"success": False, "error": "Conversation not found"})
    
    # Add user details to messages
    messages_with_users = []
    for msg in conversation.messages:
        msg_data = msg.to_dict()
        sender = get_user_by_id(msg.sender_id)
        msg_data['sender'] = sender.to_dict() if sender else None
        messages_with_users.append(msg_data)
    
    # Get other participant details
    other_participant_id = [pid for pid in conversation.participants if pid != session['user_id']][0]
    other_user = get_user_by_id(other_participant_id)
    
    return jsonify({
        "success": True, 
        "conversation": conversation.to_dict(),
        "messages": messages_with_users,
        "other_user": other_user.to_dict() if other_user else None
    })

@app.route('/api/conversation/with/<username>')
def get_or_create_conversation_with_user(username):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    target_user = users_db.get(username)
    if not target_user:
        return jsonify({"success": False, "error": "User not found"})
    
    conversation = get_or_create_conversation(session['user_id'], target_user.user_id)
    
    # Add user details to messages
    messages_with_users = []
    for msg in conversation.messages:
        msg_data = msg.to_dict()
        sender = get_user_by_id(msg.sender_id)
        msg_data['sender'] = sender.to_dict() if sender else None
        messages_with_users.append(msg_data)
    
    return jsonify({
        "success": True, 
        "conversation": conversation.to_dict(),
        "messages": messages_with_users,
        "other_user": target_user.to_dict()
    })

@app.route('/api/users/search')
def search_users():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"success": True, "users": []})
    
    matching_users = []
    for user in users_db.values():
        if (query in user.username.lower() or 
            query in user.display_name.lower()) and \
            user.user_id != session['user_id']:
            matching_users.append(user.to_dict())
    
    return jsonify({"success": True, "users": matching_users})

# Reporting APIs and other existing APIs remain the same...
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

# [Previous reporting and admin APIs go here - they're the same as before]

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)

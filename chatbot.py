import random

print("🤖 Mini-AI ChatBot - Type 'exit' to quit")

# Dictionary of keywords -> list of possible replies
responses = {
    "hi": ["Hey! 😎", "Hello there! 👋", "Hiya! 😜", "Yo! ✌️", "Heyyy 😁"],
    "hello": ["Hi! 😄", "Hello! 👋", "Hey! 😎", "Yo! 😜"],
    "how are you": ["I'm good! 😅", "Feeling awesome! 😎", "Chillin' 😎", "Pretty good, thanks! 😁"],
    "what is your name": ["Call me MiniGPT 😎", "I'm your mini AI friend 🤖", "You can call me ChatB 🤩"],
    "who are you": ["I'm your mini AI friend 🤖", "A tiny chatbot with big heart 😎", "Your virtual buddy! 😜"],
    "i love you": ["Aww! 😳 I appreciate that!", "Hehe 😅 Love you too!", "❤️ Right back atcha!"],
    "do you love me": ["Haha 😜 I'm just a bot!", "I like our chats 😎", "🤔 Love is complicated!"],
    "bye": ["Goodbye! 👋", "See you later! 😁", "Take care! 😜", "Catch you later! ✌️"],
    "default": ["Hmm… interesting 🤔", "I see… 😜", "Ah! 😂", "Oh really? 🤔", "Haha, tell me more! 😁"],
}

# Extra slang / casual patterns
slang_patterns = {
    "bruh": ["Bruh… 😂", "Haha bruh 😅", "What's up bruh? 😎"],
    "lol": ["Haha 😆", "LOL 😜", "Hehe 😁"],
    "omg": ["OMG 😱", "Wow 😲", "No way! 😳"],
    "idk": ["I feel you 😅", "Hmmm 🤔", "Yeah… me neither 😜"],
}

responses.update(slang_patterns)

# List of keywords for matching, sorted longest first
keywords = sorted(responses.keys(), key=lambda x: -len(x))

def find_reply(user_input):
    for key in keywords:
        if key in user_input:
            return random.choice(responses[key])
    return random.choice(responses["default"])

# Main chat loop
while True:
    user_input = input("You: ").lower().strip()
    if user_input in ["exit", "quit"]:
        print("Bot: Goodbye! 👋")
        break
    reply = find_reply(user_input)
    print("Bot:", reply)

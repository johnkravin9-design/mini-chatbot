import json
import os

class SimpleStorage:
    def __init__(self, filename='aura_data.json'):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {'users': [], 'posts': [], 'reports': []}
    
    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

# Test the storage
storage = SimpleStorage()
print("Current data:", storage.data)
print("Reports count:", len(storage.data.get('reports', [])))

import discord
import json
import modules.emojis as emojis

class user_data:
    def __init__(self, *, name : str = None):
        self.last_bait : str = None
        self.level : int = 0
        self.haj_profile : str = emojis.blahajar['blahaj']
        self.name : str = name

class blahaj_data:
    def __init__(self, filename : str):
        self.filename = filename
        self.user_data = {}
        self.load_data()
    
    def load_data(self):
        with open(self.filename, 'r') as f:
            self.user_data = json.load(f)

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.user_data, f, indent=4)

    def sync_changes(self, user : discord.User, data : user_data):
        if isinstance(data, user_data):
            self.user_data[str(user.id)] = data.__dict__
        else:
            self.user_data[str(user.id)] = data
        self.save_data()
    
    def get_data(self, user : discord.User) -> dict:
        if str(user.id) not in self.user_data.keys():
            return None
        return self.user_data[str(user.id)]

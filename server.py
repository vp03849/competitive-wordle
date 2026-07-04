import socket
import threading
import json
import random
import requests
from bs4 import BeautifulSoup

class WordleServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.game_state = {
            'players': {},
            'target_word': '',
            'game_active': False,
            'winner': None
        }
        self.words = self.scrape_words()
        
    def scrape_words(self):
        try:
            response = requests.get('https://perchance.org/fiveletter', timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text = soup.get_text()
            words = set()
            for word in text.split():
                cleaned = ''.join(c for c in word if c.isalpha()).upper()
                if len(cleaned) == 5:
                    words.add(cleaned)
            
            if len(words) < 50:
                words.update(['CRANE', 'SLATE', 'PAINT', 'AUDIO', 'HOUSE', 
                             'STONE', 'PRIME', 'CLOUD', 'BEACH', 'TIGER',
                             'PLANT', 'SMART', 'GRAIN', 'FRAME', 'SPACE'])
            
            word_list = list(words)
            print(f"Loaded {len(word_list)} words")
            return word_list
        except Exception as e:
            print(f"Error scraping words: {e}")
            return ['CRANE', 'SLATE', 'PAINT', 'AUDIO', 'HOUSE', 
                   'STONE', 'PRIME', 'CLOUD', 'BEACH', 'TIGER',
                   'PLANT', 'SMART', 'GRAIN', 'FRAME', 'SPACE']
    
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            client, address = self.server.accept()
            print(f"Connection from {address}")
            
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()
    
    def handle_client(self, client):
        player_name = None
        
        try:
            data = client.recv(1024).decode('utf-8')
            message = json.loads(data)
            
            if message['type'] == 'join':
                player_name = message['name']
                self.clients.append(client)
                self.game_state['players'][player_name] = {
                    'guesses': [],
                    'won': False,
                    'attempts': 0
                }
                
                self.send_to_client(client, {
                    'type': 'joined',
                    'game_state': self.game_state
                })
                
                self.broadcast({
                    'type': 'player_joined',
                    'name': player_name,
                    'game_state': self.game_state
                })
                
                print(f"Player {player_name} joined")
            
            while True:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                
                if message['type'] == 'start_game':
                    self.start_game()
                
                elif message['type'] == 'guess':
                    self.process_guess(message['name'], message['word'])
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            if player_name and player_name in self.game_state['players']:
                del self.game_state['players'][player_name]
                self.broadcast({
                    'type': 'player_left',
                    'name': player_name,
                    'game_state': self.game_state
                })
            if client in self.clients:
                self.clients.remove(client)
            client.close()
    
    def start_game(self):
        self.game_state['target_word'] = random.choice(self.words)
        self.game_state['game_active'] = True
        self.game_state['winner'] = None
        
        for player in self.game_state['players']:
            self.game_state['players'][player] = {
                'guesses': [],
                'won': False,
                'attempts': 0
            }
        
        print(f"Game started! Target word: {self.game_state['target_word']}")
        
        self.broadcast({
            'type': 'game_started',
            'game_state': self.game_state
        })
    
    def process_guess(self, player_name, guess):
        if not self.game_state['game_active']:
            return
        
        if player_name not in self.game_state['players']:
            return
        
        target = self.game_state['target_word']
        result = []
        
        target_chars = list(target)
        guess_chars = list(guess.upper())
        
        for i in range(5):
            if guess_chars[i] == target_chars[i]:
                result.append(2)
                target_chars[i] = None
            else:
                result.append(0)
        
        for i in range(5):
            if result[i] == 0 and guess_chars[i] in target_chars:
                result[i] = 1
                target_chars[target_chars.index(guess_chars[i])] = None
        
        self.game_state['players'][player_name]['guesses'].append({
            'word': guess.upper(),
            'result': result
        })
        self.game_state['players'][player_name]['attempts'] += 1
        
        if guess.upper() == target:
            self.game_state['players'][player_name]['won'] = True
            if not self.game_state['winner']:
                self.game_state['winner'] = player_name
                self.game_state['game_active'] = False
        
        self.broadcast({
            'type': 'guess_result',
            'player': player_name,
            'game_state': self.game_state
        })
    
    def send_to_client(self, client, message):
        try:
            client.send(json.dumps(message).encode('utf-8'))
        except:
            pass
    
    def broadcast(self, message):
        for client in self.clients[:]:
            self.send_to_client(client, message)

if __name__ == '__main__':
    server = WordleServer()
    server.start()
import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

class WordleClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client = None
        self.player_name = ""
        self.game_state = None
        
        self.root = tk.Tk()
        self.root.title("Multiplayer Wordle")
        self.root.geometry("800x700")
        self.root.configure(bg='#121213')
        
        self.setup_gui()
        
    def setup_gui(self):
        title = tk.Label(
            self.root, 
            text="MULTIPLAYER WORDLE",
            font=('Helvetica', 24, 'bold'),
            bg='#121213',
            fg='white'
        )
        title.pack(pady=10)
        
        self.status_frame = tk.Frame(self.root, bg='#121213')
        self.status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Click 'Connect' to join a game",
            font=('Helvetica', 12),
            bg='#121213',
            fg='#818384'
        )
        self.status_label.pack()
        
        self.players_frame = tk.Frame(self.root, bg='#121213')
        self.players_frame.pack(pady=5)
        
        tk.Label(
            self.players_frame,
            text="Players:",
            font=('Helvetica', 10, 'bold'),
            bg='#121213',
            fg='white'
        ).pack()
        
        self.players_label = tk.Label(
            self.players_frame,
            text="",
            font=('Helvetica', 10),
            bg='#121213',
            fg='#818384'
        )
        self.players_label.pack()
        
        self.board_frame = tk.Frame(self.root, bg='#121213')
        self.board_frame.pack(pady=20)
        
        self.cells = []
        for row in range(6):
            row_cells = []
            row_frame = tk.Frame(self.board_frame, bg='#121213')
            row_frame.pack(pady=2)
            for col in range(5):
                cell = tk.Label(
                    row_frame,
                    text='',
                    width=4,
                    height=2,
                    font=('Helvetica', 18, 'bold'),
                    bg='#3a3a3c',
                    fg='white',
                    relief='solid',
                    borderwidth=2
                )
                cell.pack(side='left', padx=2)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        input_frame = tk.Frame(self.root, bg='#121213')
        input_frame.pack(pady=10)
        
        self.guess_entry = tk.Entry(
            input_frame,
            font=('Helvetica', 16),
            width=15,
            bg='#3a3a3c',
            fg='white',
            insertbackground='white'
        )
        self.guess_entry.pack(side='left', padx=5)
        self.guess_entry.bind('<Return>', lambda e: self.submit_guess())
        
        self.submit_btn = tk.Button(
            input_frame,
            text="Submit Guess",
            command=self.submit_guess,
            font=('Helvetica', 12),
            bg='#538d4e',
            fg='white',
            state='disabled'
        )
        self.submit_btn.pack(side='left', padx=5)
        
        control_frame = tk.Frame(self.root, bg='#121213')
        control_frame.pack(pady=10)
        
        self.connect_btn = tk.Button(
            control_frame,
            text="Connect",
            command=self.connect_to_server,
            font=('Helvetica', 12),
            bg='#818384',
            fg='white',
            width=12
        )
        self.connect_btn.pack(side='left', padx=5)
        
        self.start_btn = tk.Button(
            control_frame,
            text="Start Game",
            command=self.start_game,
            font=('Helvetica', 12),
            bg='#b59f3b',
            fg='white',
            state='disabled',
            width=12
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.opponent_frame = tk.Frame(self.root, bg='#121213')
        self.opponent_frame.pack(pady=10)
        
        tk.Label(
            self.opponent_frame,
            text="Opponents' Progress:",
            font=('Helvetica', 10, 'bold'),
            bg='#121213',
            fg='white'
        ).pack()
        
        self.opponent_label = tk.Label(
            self.opponent_frame,
            text="",
            font=('Helvetica', 9),
            bg='#121213',
            fg='#818384',
            justify='left'
        )
        self.opponent_label.pack()
        
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.player_name = simpledialog.askstring("Player Name", "Enter your name:")
            if not self.player_name:
                return
            
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            
            message = {
                'type': 'join',
                'name': self.player_name
            }
            self.client.send(json.dumps(message).encode('utf-8'))
            
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            
            self.connect_btn.config(state='disabled')
            self.start_btn.config(state='normal')
            self.status_label.config(text=f"Connected as {self.player_name}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def receive_messages(self):
        try:
            while True:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.handle_message(message)
        except Exception as e:
            print(f"Error receiving messages: {e}")
            self.root.after(0, lambda: self.status_label.config(text="Disconnected from server"))
    
    def handle_message(self, message):
        msg_type = message['type']
        
        if msg_type in ['joined', 'player_joined', 'player_left']:
            self.game_state = message['game_state']
            self.update_players_display()
            
        elif msg_type == 'game_started':
            self.game_state = message['game_state']
            self.root.after(0, self.reset_board)
            self.root.after(0, lambda: self.submit_btn.config(state='normal'))
            self.root.after(0, lambda: self.status_label.config(text="Game in progress! Make your guess!"))
            
        elif msg_type == 'guess_result':
            self.game_state = message['game_state']
            self.root.after(0, self.update_board)
            self.root.after(0, self.update_opponent_display)
            
            if self.game_state['winner']:
                winner = self.game_state['winner']
                word = self.game_state['target_word']
                self.root.after(0, lambda: self.submit_btn.config(state='disabled'))
                if winner == self.player_name:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"YOU WON! The word was {word}",
                        fg='#538d4e'
                    ))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"{winner} won! The word was {word}",
                        fg='#b59f3b'
                    ))
    
    def update_players_display(self):
        if not self.game_state:
            return
        
        players = list(self.game_state['players'].keys())
        players_text = ", ".join(players)
        self.root.after(0, lambda: self.players_label.config(text=players_text))
    
    def update_opponent_display(self):
        if not self.game_state:
            return
        
        text = ""
        for player, data in self.game_state['players'].items():
            if player != self.player_name:
                attempts = data['attempts']
                won = "✓ WON" if data['won'] else f"{attempts} attempts"
                text += f"{player}: {won}\n"
        
        self.opponent_label.config(text=text)
    
    def start_game(self):
        if self.client:
            message = {
                'type': 'start_game'
            }
            self.client.send(json.dumps(message).encode('utf-8'))
    
    def submit_guess(self):
        guess = self.guess_entry.get().strip().upper()
        
        if len(guess) != 5:
            messagebox.showwarning("Invalid Guess", "Please enter a 5-letter word")
            return
        
        if not guess.isalpha():
            messagebox.showwarning("Invalid Guess", "Please enter only letters")
            return
        
        if self.client and self.game_state and self.game_state['game_active']:
            message = {
                'type': 'guess',
                'name': self.player_name,
                'word': guess
            }
            self.client.send(json.dumps(message).encode('utf-8'))
            self.guess_entry.delete(0, tk.END)
    
    def reset_board(self):
        for row in self.cells:
            for cell in row:
                cell.config(text='', bg='#3a3a3c')
        self.opponent_label.config(text='')
        self.status_label.config(text="Game in progress!", fg='#818384')
    
    def update_board(self):
        if not self.game_state or self.player_name not in self.game_state['players']:
            return
        
        guesses = self.game_state['players'][self.player_name]['guesses']
        
        for row_idx, guess_data in enumerate(guesses):
            word = guess_data['word']
            result = guess_data['result']
            
            for col_idx in range(5):
                self.cells[row_idx][col_idx].config(text=word[col_idx])
                
                if result[col_idx] == 2:
                    color = '#538d4e'  
                elif result[col_idx] == 1:
                    color = '#b59f3b'
                else:
                    color = '#3a3a3c' 
                
                self.cells[row_idx][col_idx].config(bg=color)
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    client = WordleClient()
    client.run()
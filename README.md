# Competitive Wordle

A competitive multiplayer Wordle game built in Python using TCP sockets and multithreading. The server manages the game state, while multiple clients connect to compete in real time.

## Features

* Multiplayer gameplay using TCP sockets
* Multithreaded server supporting multiple simultaneous clients
* Shared game state synchronized across all players
* Random 5-letter word selection
* Real-time updates when players join, leave, make guesses, or win

## Requirements

Install the required packages:

```bash
pip install requests beautifulsoup4
```

## Running the Application

### Local (Same Computer)

1. Open a terminal and start the server:

```bash
python server.py
```

2. Open one or more additional terminals and start the client:

```bash
python client.py
```

Each client runs independently and can join the same multiplayer game.

### Local Network (Same Wi-Fi)

To allow devices on the same local network to connect:

1. In `server.py`, change the host to:

```python
host = "0.0.0.0"
```

2. Find the server computer's private IP address (for example, `192.168.1.42`).

3. In `client.py`, set the host to the server computer's private IP:

```python
host = "192.168.1.42"
```

Clients connected to the same local network can now join the game.

## Internet Access

To allow players outside the local network to connect, the server must be hosted on a publicly accessible machine (such as a cloud virtual machine) or the home network must be configured with port forwarding and appropriate firewall rules.

## Technologies Used

* Python
* TCP Sockets
* Threading
* Tkinter
* JSON
* Requests
* BeautifulSoup

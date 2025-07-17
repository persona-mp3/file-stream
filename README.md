# Rengoku: Python Socket File Transfer System

Rengoku is a simple Python-based client-server application for reliable file/data transfer over TCP sockets. It involves custom packet handling, acknowledgments. It's to be used on the custom VCS made at [Yogit](https://github.com/persona-mp3/yogit.git).

## Features
- Custom TCP server and client implementation
- Packet-based data transmission with acknowledgments
- Handles multiple packets per connection
- Writes received data to files per client/author
- Modular code structure for easy extension



## Project Structure
```
client.py           # Client-side logic (send data/packets)
decoder_encoder.py  # (Optional) Encoding/decoding helpers
main.py             # Entry point or orchestrator
server.py           # Server-side logic (receive, decode, write)
utils/
  utils.py          # File handler and utility functions
```

## How It Works
### Server (`server.py`)
- Listens on a specified port (default: 6000)
- Accepts incoming client connections
- Receives a header with metadata (acknowledgment, packet count, author, etc.)
- For each packet:
  - Decodes and validates the packet type
  - Writes the received data to a file under `test/<author>`
- Sends acknowledgment responses to the client

### Client (`client.py`)
- Connects to the server's IP and port
- Sends an initial header with metadata (type, number of packets, author, etc.)
- Sends data in one or more packets, each with a custom header
- Waits for server acknowledgment after sending

## Usage
### 1. Start the Server
- First make sure you have python installed and clone to your local machine using ```git clone https://github.com/persona-mp3/file-stream```
- Switch into the directory using ```cd file-stream``` in where you cloned the repository


```bash
python server.py
```

### 2. Run the Client
Edit `client.py` to set the server IP, port, author, and data to send. Then run:
```bash
python client.py "name_of_file"
```

### 3. Check Output
Received files are saved in the `test/` directory, named after the author.

## Customization
- Change the port in `server.py` and `client.py` as needed.
- Extend `utils/utils.py` for advanced file handling or logging.
- Add more packet types or metadata fields for richer protocols.

## Requirements
- Python 3.7+
- No external dependencies (uses only Python standard library)


# Rengoku: Python Socket File Transfer System

Rengoku is a robust Python client-server application for reliable file and data transfer over TCP sockets. It features custom packet handling, acknowledgments, and modular utilities. Designed for use with the custom VCS at [Yogit](https://github.com/persona-mp3/yogit.git).

> **Windows Compatibility:**
> This project is officially supported and tested only on macOS and Linux. Windows is not recommended due to differences in socket and file handling, which may cause unexpected issues. For best results, use a Unix-based system.

## Features
- Custom TCP server and client with modular code
- Packet-based data transmission with per-packet acknowledgments
- Handles multi-packet file transfers
- Writes received data to files organized by client/author
- Easily extensible for new packet types or protocol changes

## Project Structure
```
client.py             # Client logic: sends files/packets
server.py             # Server logic: receives, decodes, writes
main.py               # (Optional) Orchestrator/entry point
decoder_encoder.py    # (Optional) Encoding/decoding helpers
utils/
  utils.py            # File handling and utility functions
encoders/
  pack_response.py    # Packet status/response helpers
  decode_packet.py    # Packet decoding logic
  packet_encoding_v1.py # Versioned encoding helpers
enc_v1/
  encode.py           # Version 1 encoding
  decode.py           # Version 1 decoding
tests/                # Unit tests for all modules
```

## How It Works
### Server (`server.py`)
- Listens on a configurable port (default: 6000)
- Accepts incoming TCP connections
- Receives a header with metadata (acknowledgment, packet count, author, etc.)
- For each packet:
  - Decodes and validates the packet type
  - Writes received data to a file under `test/<author>`
- Sends acknowledgment responses to the client after each packet

### Client (`client.py`)
- Connects to the server's IP and port
- Sends an initial header with metadata (type, number of packets, author, etc.)
- Splits files into chunks and sends each as a packet with a custom header
- Waits for server acknowledgment after each packet before continuing

## Usage
### 1. Start the Server
- Ensure Python 3.7+ is installed. Clone the repository:
  ```bash
  git clone https://github.com/persona-mp3/file-stream
  cd file-stream
  python3 server.py
  ```

### 2. Run the Client
- Edit `client.py` to set the server IP, port, and author if needed.
- To send a single file:
  ```bash
  python3 client.py "name_of_file"
  ```
- To send all files in the current directory:
  ```bash
  python3 client.py .
  ```

### 3. Check Output
Received files are saved in the `test/` directory, named after the author.

## Customization
- Change the port in `server.py` and `client.py` as needed
- Extend `utils/utils.py` for advanced file handling or logging
- Add new packet types or metadata fields for richer protocols


## Contribution
Contributions are welcome! If you'd like to help improve Rengoku, please follow these guidelines:

- Fork the repository and create a new branch for your feature or bugfix.
- Write clear, concise commit messages and document your code where necessary.
- Add or update tests in the `tests/` directory to cover your changes.
- Ensure your code passes all tests and does not break existing functionality.
- Open a pull request describing your changes and the motivation behind them.

> **Note:**
> A major refactor is planned for the future to further modularize the codebase, improve maintainability, and add new features. 

## Requirements
- Python 3.7+
- No external dependencies (uses only Python standard library)

## Usage
### 1. Start the Server
- First make sure you have python installed and clone to your local machine using ```git clone https://github.com/persona-mp3/file-stream```
- Switch into the directory using ```cd file-stream``` in where you cloned the repository


```bash
python3 server.py
```

### 2. Run the Client
Edit `client.py` to set the server IP, port, author, and data to send. Then run:
```bash
python3 client.py "name_of_file"

# or to use the whole directory instead:
python3 client.py .
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


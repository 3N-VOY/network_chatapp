# Network_chatapp
This project implements a multi-client chat application in Python, featuring RSA asymmetric encryption for secure communication and SSL for encryption during socket communication. The application utilizes threading for handling multiple clients concurrently.

# Features
Server-side Features
*	RSA Asymmetric Encryption: Generates Private and Public keys, Utilizes RSA keys for secure communication between the server and clients.
*	SSL/TLS for Secure Communication: Implements SSL/TLS for secure socket communication. Generated using OpenSSL.
*	Multithreading: Supports multiple clients concurrently using threading.
*	Chat History: Allows users to save and load chat history using commands.
*	User Authentication: Prompts users to enter a username for identification in the chat. Each client has a unique id generated and sent to the server which is stored in a dictionary along with the username.


# Client-side Features
*	RSA Asymmetric Encryption: Similar to the server, clients generate and use RSA keys for secure communication.
*	SSL/TLS for Secure Communication: Establishes a secure connection with the server using SSL/TLS. Generated using OpenSSL.
*	Multithreading: Supports simultaneous sending and receiving of messages.
*	User Authentication: User have to enter a username for identification in the chat. A unique id is generated and sent to the server for further identification.

# How to Run
Server Initialization
Run server.py to start the server.
Client Initialization:
Run client.py to start a client.
Multiple clients can be run simultaneously.
Chat Commands:
*	Use the /save command to save chat history.
*	Use the /load command to load chat history.
*	Type exit to disconnect from the chat.

# Requirements
* Python 3.x
* RSA library: Install using:
`pip install rsa`
* OpenSSL:
`pip install pyOpenSSL`



# Configuration
Ensure that the server.crt and server.key files are present for SSL/TLS communication.
Usage Example
*	Start the server:
`python server.py`
*	Start multiple clients:
`python client.py`
*	Enter a unique username for each client when prompted.
*	Communicate in the chat, save, and load chat history, and exit when desired.

# Notes
This application uses RSA keys for encryption and decryption to ensure secure communication.
SSL/TLS is employed to establish a secure connection between the server and clients.
Commands like /save and /load enhance user experience by allowing chat history management.


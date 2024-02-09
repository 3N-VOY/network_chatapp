import random
import sys
import threading
import socket
import rsa
import ssl

#initialize client data list
clients_data = []

#Function to showcase id generation 
def client_id_generate():
    return random.randrange(1000, 10000)

#function for client creation and data storage
def client_create(user_id, username, client, server_public_key, client_private_key):
    client_data = {
        'user_id': user_id,
        'username': username,
        'client': client,
        'server_public_key': server_public_key,
        'client_private_key': client_private_key
    }
    return client_data

#Function to initialize client connection
def client_connection():
    #setting up variables and generating RSA public/private keys
    username = None
    public_key, private_key = rsa.newkeys(1014)
    server_public_key = None

    
    # Create an SSL context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    #load server's certificate for ssl
    context.load_verify_locations("server.crt")  
    #initialize socket wrapping it with ssl
    client = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname='127.0.0.1')


    client.connect(('127.0.0.1', 59000))
    
    print("Server Certificate:", client.getpeercert())
   
    #private/public RSA keys exchange between client and server
    server_public_key = rsa.PublicKey.load_pkcs1(client.recv(1024))
    client.send(public_key.save_pkcs1("PEM"))

    #Creation of client storing data inlcluding rsa keys for communication
    client_created = client_create(client_id_generate(), username, client, server_public_key, private_key)
    clients_data.append(client_created)
    user_id = client_created['user_id']
    client.send(f'{user_id}'.encode('utf-8'))




    #username handling 
    message = client.recv(1024)
    decrypt = rsa.decrypt(message, find_privatekey(user_id)).decode('utf-8')
    if decrypt == 'Enter username':
        print(decrypt)
        username = f'{input("")}'
        client.send(rsa.encrypt(username.encode('utf-8'), find_serverkey(user_id)))
       
        for created_user in clients_data:
            if created_user['username'] == None:
                created_user['username'] = username

    else:
        print("Connection Error! ")         

#function grabbing the private key and use it when needed
def find_privatekey(user_id):
    for client_data in clients_data:
        if client_data['user_id'] == user_id:
            return client_data['client_private_key']

#function grabbing server's public key when needed
def find_serverkey(user_id):
    for client_data in clients_data:
        if client_data['user_id'] == user_id:
            return client_data['server_public_key']

#client recieving messages from server function
def client_receive(client_index):
 
    while True:
        try:
            for user in clients_data:
                client = user['client']
                user_id = user['user_id']

                #error handling
                encrypted_message = client.recv(1024)
                if not encrypted_message:
                    print("Server disconnected. Exiting...")
                    
                    print("Exiting the chat...")
                    print("You are now disconnected!")
                    client.close()
                    break
                #message filtering for the state implementing RSA decryption
                decrypted_message = rsa.decrypt(encrypted_message, find_privatekey(user_id)).decode('utf-8')
                
                if decrypted_message.startswith("/load"):
                    #retrieving chat history form saved messages 
                    history_messages = decrypted_message[len("/load"):].split('\n')
                    for history_message in history_messages:
                        if history_message:
                            print(history_message)
                
                else:
                    
                    print(decrypted_message)
        except Exception as e:
 
            print("")

            exit
            break
            
    
#client sending data to the server function
def client_send(client_index):
    #setting up the variables grabbed from the list inside the dictionary
    while True:
        try:
            for user in clients_data:
                client = user['client']
                user_id = user['user_id']
                username = user['username']
                #message setup with error handling
                message = f'{username}: {input("")}'
                client.send(rsa.encrypt(f'{message}'.encode('utf-8'), find_serverkey(user_id)))

                    
                
        except socket.error as e:
            print(f'Error sending message: {str(e)}')


client_connection()
#usage of multithreading for concurrency
receive_thread = threading.Thread(target=client_receive, args=(0,))
receive_thread.start()

send_thread = threading.Thread(target=client_send, args=(0,))
send_thread.start()

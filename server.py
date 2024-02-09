import threading
import socket
import rsa
import ssl

# Data storage for chat history and users using lists.
chat_history = []
users = []
#setting up constant for data isolation
lock = threading.Lock()

#function creating dictionaries to store user messages in the list
def create_user_messages(user_id, message):
    user_message = {
        'user_id' : user_id,
        'message' : message
    }
    return user_message


#function to create user profiles using dictionaries with the appropriate data to retrieve later 
# saved to the list
def create_user_dict(user_id, username, client, client_public_key, serverprivatekey):

    user_data = {
        'user_id': user_id,
        'username': username,
        'client': client,
        'client_public_key' : client_public_key,
        'serverprivatekey' : serverprivatekey
    }

    return user_data

#main function to start the server
def server_initialize():
    
#setting up the constants
#RSA Private and Public keys generation
    username = None
    public_key, private_key = rsa.newkeys(1014)
    host = '127.0.0.1'
    port = 59000

#creating the socket wrapping it up with ssl retrieving the keys for ssl
#which are saved in the files and generated using OpenSSL 
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    ssl_server = context.wrap_socket(server, server_side=True)
    
#Gettting the server ready to accept connections

    while True:
        print('Server is running and listening ...')
        client, address = ssl_server.accept()
        
  
#Once a connection is recieved server sends the public key to the client for encryption
#Server also receives client's public key for encryption
        client.send(public_key.save_pkcs1("PEM"))
        client_public_key = rsa.PublicKey.load_pkcs1(client.recv(1024))

      
#recieving user_id from client
        user_id = client.recv(1024).decode('utf-8')
        print('Received user_id:', user_id)

   
#creating user profile and adding it to the list 
        
        user_created = create_user_dict(user_id, username, client, client_public_key, private_key )
        users.append(user_created)
       


# Sending Prompt for username to the client
        client.send(rsa.encrypt('Enter username'.encode('utf-8'), find_publickey(user_id)))

# Receive the username
        username = rsa.decrypt(client.recv(1024), find_privatekey(user_id)).decode('utf-8')
        print('Received username:', username)
#Adding username to the user profile created before
        for created_user in users:
            if created_user['username'] == None:
                created_user['username'] = username
#Broadcasting message informing about the new user 
        broadcast(f'{username} has connected to the chat room')
#informing the client tha the is connected
        client.send(rsa.encrypt('You are now connected! To Exit the Chat -> exit'.encode('utf-8'), find_publickey(user_id)))

#finding user_id of the specific user
        for created_user in users:
            user_id = created_user['user_id']
#passing the necessary parameters to identify specific clients and starting the threads 
        thread = threading.Thread(target=handle_client, args=(client, user_id, ))
        thread.start()

#message filtering function for the appropriate commands 
def filter_message(decrypted_message):
    split = decrypted_message.split(':')
    filter_message = split[1].strip()
    print(f'filter_message:  {filter_message}')
    return filter_message

#function to save history using /save 
def save_history(client, message, user_id):
    with lock:
       
        
        try:   
            for user in users:
                username = user['username']
                user_id = user['user_id']
                if username:
                    save_message = create_user_messages(user_id,  message[len("/save"):])
                    chat_history.append(save_message)
                    print(f'Message {save_message} saved successfully for user {username}.' )
                else:
                    raise Exception(f'User with username {username} not found.')
                
        except ValueError as ve:
            print(f'ValueError: {ve}. Check the value types.')
                      
        except Exception as e:
            print(f'An error occurred: {e}. Message is not saved.')
        
            

            

#function to load history using /load
def load_history(client, message, user_id):
    user_messages = []
   
    with lock:
      
        for saved_message in chat_history:
            
            if user_id == saved_message['user_id']:
                user_messages.append(saved_message['message'])
        
        
        for user_message in user_messages:
            
            encrypted_message = rsa.encrypt(user_message.encode('utf-8'), find_publickey(user_id))
            client.send(encrypted_message)
            
        if not user_messages:
            client.send(rsa.encrypt("No saved messages for you.".encode('utf-8'), find_publickey(user_id)))

        user_messages.clear()    


#client handling function for recieving messages
def handle_client(client, user_id):
    while True:
        try:
            encrypted_message = client.recv(1024)
            
            #decrypting messages using RSA
            if not encrypted_message:
                handle_disconnect(client, user_id)
                break

            decrypted_message = rsa.decrypt(encrypted_message, find_privatekey(user_id)).decode('utf-8')
          
            #check message
            
            message_check = filter_message(decrypted_message)
            
            #server handling client exit. Confirmation with and message filtering

            if message_check == "exit":
                client.send(rsa.encrypt('Are you sure you want to exit? (y/n)'.encode('utf-8'), find_publickey(user_id)))
                try: 
                    encrypted_message = client.recv(1024)
                    decrypted_message = rsa.decrypt(encrypted_message, find_privatekey(user_id)).decode('utf-8')
                    message_check = filter_message(decrypted_message)
                   
                    if message_check == 'y':
                        
                        handle_disconnect(client, user_id)
                        break
                    elif message_check == 'n':
                        continue
                    else:
                        continue
                    
                except:
                    print(f'Something went wrong: ')
            
            #server save state using message filtering

            elif message_check.startswith("/save"):
                save_history(client, message_check, user_id )

            #server load state using message filtering

            elif message_check.startswith("/load"):
                load_history(client, message_check, user_id)     
            
            #Message broadcasting to everyone if none of the conditions are met

            else:
                broadcast(f': {decrypted_message}')

        except socket.error as e:
            handle_disconnect(client, user_id)

#function to find the corresponding public key of the client for decryption
#retrieving data from the created profile in the dictionary
def find_publickey(user_id):
    for created_user in users:
        if created_user['user_id'] == user_id:
            return created_user['client_public_key']

#function to find the corresponding private key of the client for encryption
#retrieving data from the created profile in the dictionary
def find_privatekey(user_id):
    for created_user in users:
        if created_user['user_id'] == user_id:
            return created_user['serverprivatekey']

#function for message broadcasting
def broadcast(message):

    with lock:
        for user in users:
            client = user['client']
            user_id = user['user_id']
           
           
            try:
                client.send(rsa.encrypt(message.encode('utf-8'), find_publickey(user_id)))
            except socket.error as e:
                handle_disconnect(client )

#function for handling disconnections of the corresponding client
def handle_disconnect(client, user_id ):
    with lock:
        # for created_user in users:
        #     username = created_user['username']
            
     
    
        for user in users:
            username = user['username']
            if user['user_id'] == user_id:
                users.remove(user)

    client.close()

    broadcast(f'{username} has left the chat room.')            



if __name__ == "__main__":
    try:
        server_initialize()
    except Exception as e:
        print(f'Error druing server initialization: {e}')
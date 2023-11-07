# Sample client code
import socket

# Create a client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("server_ip", 8080))  # Replace server_ip with the server's IP address

# Define functions for client commands (publish and fetch
    # Implement the logic to publish a file to the server
def publish_file(local_name, file_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((server_ip, 8080))  # Replace 'server_ip' with the actual server's IP
        
        # Send a publish request to the server
        publish_request = f"PUBLISH {local_name} {file_name}\n"
        client_socket.send(publish_request.encode())
        
        print(f"File '{local_name}' published as '{file_name}' on the server.")
    
    except ConnectionRefusedError:
        print("Connection to the server refused.")
    
    except Exception as e:
        print(f"Error publishing file: {str(e)}")
    
    finally:
        client_socket.close()

def fetch_file(file_name):
    # Create a socket to connect to the source (server or another client)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Replace 'server_ip' with the actual IP address of the source
        client_socket.connect(('server_ip', 8080))
        
        # Send a fetch request to the source
        fetch_request = f"FETCH {file_name}\n"
        client_socket.send(fetch_request.encode())
        
        # Receive the file data in chunks and save it locally
        with open(file_name, 'wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
        
        print(f"File '{file_name}' fetched successfully.")
    
    except ConnectionRefusedError:
        print(f"Connection to {hostname} refused.")
    
    except Exception as e:
        print(f"Error fetching file: {str(e)}")
    
    finally:
        client_socket.close()
    # Implement the logic to fetch a file from the server or other clients

# Use a command-line interface to accept user commands
if __name__=="__main__":
    while True:
        command = input("Enter a command: ")
        if command.startswith("publish"):
            _, local_name, file_name = command.split()
            publish_file(local_name, file_name)
        elif command.startswith("fetch"):
            _, file_name = command.split()
            fetch_file(file_name)
        else:
            print("Invalid command")

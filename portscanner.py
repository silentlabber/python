import socket

def port_scan(host, port):
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        # Attempt to connect to the specified port on the host
        result = sock.connect_ex((host, port))

        # Close the socket
        sock.close()

        # If the connection was successful, return True
        if result == 0:
            return True

    except socket.error:
        pass

    # If the connection failed or timed out, return False
    return False
  
host = '127.0.0.1'
start_port = 1
end_port = 1024

for port in range(start_port, end_port + 1):
    if port_scan(host, port):
        print(f"Port {port} is open")

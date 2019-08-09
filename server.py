import socket
import threading


host = '127.0.0.1'
port = 8080
directory = 'public'

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AddressFamily and TCP connections


def start():
    try:
        print("Starting server on " + str(host) + ":" + str(port))
        my_socket.bind((host, port))
        print("Started server on " + str(host) + ":" + str(port) + "\n")
        conn()

    except OSError:
        print("Host and/or port already in use")
        shutdown()


def shutdown():
    try:
        print("Server shutting down")
        my_socket.shutdown(socket.SHUT_RDWR)  # No reads or Writes
    except Exception:
        pass


def conn():
    my_socket.listen(5)  # number of invalid connections before termination
    while True:
        (client, address) = my_socket.accept()
        print("client - ", client)
        print("address - ", address)
        client.settimeout(60)  # seconds to wait for the same client
        threading.Thread(target=handle_request, args=(client,)).start()  # with threading
        # handle_request(client)  # without threading


def generate_headers(response_code, file_type):
    print("Requested File Type : " + file_type)

    header = ''
    if response_code == 200:
        header += 'HTTP/1.1 200 OK\n'
    elif response_code == 404:
        header += 'HTTP/1.1 404 Not Found\n'
    elif response_code == 400:
        header += 'HTTP/1.1 400 Bad Request\n'

    if file_type == 'jpg' or file_type == 'jpeg':
        header += 'Content-Type: image/jpeg\n'
    elif file_type == 'htm' or file_type == 'html':
        header += 'Content-Type: text/html\n'
    elif file_type == 'png':
        header += 'Content-Type: image/png\n'
    elif file_type == 'css':
        header += 'Content-Type: text/css\n'

    header += 'Connection: close\n\n'
    return header


def handle_request(client):
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
        except Exception as e:
            print("Request timed out" + str(e))
            break
        print(data)

        try:
            file_requested = data.split(' ')[1]

            # a = data.split(' ')
            # file_requested = a[1]

            file_requested = file_requested.split('?')[0]

            if file_requested == "/":
                file_requested = "/index.html"

            file_path = directory + file_requested

            file_type = file_requested.split('.')[1]

            f = open(file_path, 'rb')
            response_data = f.read()
            f.close()
            print("Requested File : " + file_path)
            response_header = generate_headers(200, file_type)

        except UnboundLocalError as e:  #
            print(e)
            response_header = generate_headers(400, '')
            response_data = b"Malformed request"
        except IndexError as e:  # no extension to split
            print("Requested ")
            response_header = generate_headers(400, '')
            response_data = b"Malformed request"
        except FileNotFoundError:
            response_header = generate_headers(404, file_type)
            # f = open('404.html', 'rb')
            # response_data = f.read()
            # f.close()

            response_data = b"<h1>Error 404 - File Not Found<h1>"

        response = response_header.encode()

        response += response_data
        # response = response + response_data

        client.send(response)
        client.close()
        break


start()

#!/usr/bin/env python3
import socketserver
import os
import json 


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""

content_type = {
    ".html": "text/html",
    ".css": "text/css",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/icon",
    ".txt": "text/plain",
}

class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    This class is responsible for handling a request. The whole class is
    handed over as a parameter to the server instance so that it is capable
    of processing request. The server will use the handle-method to do this.
    It is instantiated once for each request!
    Since it inherits from the StreamRequestHandler class, it has two very
    usefull attributes you can use:

    rfile - This is the whole content of the request, displayed as a python
    file-like object. This means we can do readline(), readlines() on it!
    -> used to read the incoming request from the client

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we do wfile.close(), the response is
    automatically sent.
    -> used to write the response to the client

    The class has three important methods:
    handle() - is called to handle each request.
    setup() - Does nothing by default, but can be used to do any initial
    tasks before handling a request. Is automatically called before handle().
    finish() - Does nothing by default, but is called after handle() to do any
    necessary clean up after a request is handled.
    """
    def handle(self):
        """
        This method is responsible for handling an http-request. You can, and should(!),
        make additional methods to organize the flow with which a request is handled by
        this method. But it all starts here!
        """

        # Request, parse, and process the requested link 
        request_line = self.rfile.readline().decode('utf-8').strip() # By using utf-8 encoding in decode(), you ensure that the bytes are properly decoded 
        requested_part = request_line.split()

        print(requested_part)

        # Check if the request is valid and force the HTTP method to be upper letters, and URI to be lower letters 
        if len(requested_part) >= 2:
            HTTP_method = requested_part[0].upper()
            URI = requested_part[1].lower()

        # Chek if the HTTP methode is Get, Post 
        if HTTP_method == "GET":
            # check that the file type is legal
            if URI.endswith('.py'):
                self.wfile.write(error_handling(403).encode())

            # get the index 
            elif URI == "/" or URI == "/index.html":
                self.get_request("index.html")

            # get the icon 
            elif URI == "/favicon.ico":
                self.get_request("favicon.ico")

            elif URI.startswith('/messages'):
                # Handle GET request for messages
                pass
            
            else:
                print("here2")
                self.wfile.write(error_handling(404).encode())
                

        elif HTTP_method == 'POST':
            if URI == "/test.txt":

                line = self.rfile.readline().decode().strip()
                while line:
                    header, value = line.split(":", 1)
                    if header == "Content-Length":
                        length = value
                    line = self.rfile.readline().decode().strip()
                line = self.rfile.read(int(length)).decode().strip()

                body = line[5:]     # % = lengden av text =

                # post_message = body[5:].encode()s
                self.wfile.write(b"HTTP/1.1 200 OK\r\n")
                self.wfile.write(f"Content-length: {length}\r\n".encode())
                self.wfile.write(b"Content-type: text/plain\r\n")
                self.wfile.write(b"\r\n")
                self.wfile.write(body.encode())

            
            # elif URI == '/messages':
            #     # Handle POST request to create a new message
            #     pass 
            else:
                self.wfile.write(error_handling(403).encode())

        elif HTTP_method == 'PUT':
            if URI.startswith('/messages'):
                # Handle PUT request to update a message
                pass 
            else:
                # Handle other PUT requests (404)
                pass

        elif HTTP_method == 'DELETE':
            if URI.startswith('/messages'):
                # Handle DELETE request to remove a message@
                pass
            else:
                # Handle other DELETE requests (404)
                pass

        else:
            self.wfile.write(error_handling(404).encode())
    
    def get_request(self, filename):
        # Open the file and store its content for writing later 
        with open(filename, 'rb') as f:
            content = f.read()
        
        # Find the content type 
        content_type = find_content_type(filename)

        # Create the response header 
        response_header = (
            b'HTTP/1.1 200 OK\r\n'+
            b'Content-Length: %d\r\n'%len(content) + 
            f'Content-Type: {content_type}\r\n\r\n'.encode()
        )

        # Write the response header and the content of the file
        self.wfile.write(response_header + content)

    def post_request(self, filename):
        pass
        # TODO: må finne en måte å ikke hardcode content lengden for at det skal virke. det jeg gjør i post virker ikke 
        # bruke json 
        # Open the file and store its content for writing later 

        # req = self.rfile.readline()
        # body = ""

        # for index, line in enumerate(req):
        #     print(line)
        #     if len(line) == 2:
        #         body = req[index + 1].decode().strip()
        #         break

        # post_message = body[5:].encode()
        # content_type = find_content_type(filename)
        
        # self.wfile.write(b"HTTP/1.1 200")

        # self.wfile.write(f'Content-Length: {len(post_message)} \r\n'.encode())
        # self.wfile.write(b"Content-type: text/plain\r\n")
        # self.wfile.write(b"\r\n")
        # self.wfile.write(post_message)

        # content_length = 0
        # for line in self.rfile:
        #     line = line.decode('utf-8').strip()
        #     if line.startswith("Content-Length"):
        #         print(content_length)
        #         content_length = int(line.split(":")[1])
        #         break
        # print(content_length)
        

        # # Find the content type and length 
        # content_type = find_content_type(filename)
        # # content_length = self.get_header_length()

        # data = self.rfile.read(content_length).decode()
        # print(data)
    

        # # Create the response header 
        # response_header = (
        #     b'HTTP/1.1 200 OK\r\n'+
        #     f'Content-Length: {content_length} \r\n'.encode() +
        #     f'Content-Type: {content_type}\r\n\r\n'.encode()
        # )

        # # Write the response header and the content of the file 
        # self.wfile.write(response_header)
        # # self.wfile.write(b"HTTP/1.1 200 OK\r\n")

        # self.wfile.write(b"nxuaios ")

        # # a - because it should append (or ab ?)

    def put_request(self):
        # oppdaterer noe du har fra før 
        pass 

    def delete_request(self):
        # slette det 
        pass

    def get_message(self, filename): 
        # Retrieve and return a list of messages
        content_length = self.get_header_length()
        content_type = find_content_type(filename)

        response_header = (
            b'HTTP/1.1 200 OK\r\n'+
            f'Content-Length: {content_length} \r\n'.encode() +
            f'Content-Type: {content_type}\r\n\r\n'.encode()
        )

        response = '{"message": []}'
        self.wfile.write(response_header + response.encode())

        pass 

    def create_message(self):
        pass

    def update_message(self, message_id, message_data):
        # Update an existing message and return it
        pass

    def delete_message(self, message_id):
        # Delete a message by ID
        pass

    def parse_headers(self):
        headers = {}
        while True:
            header_line = self.rfile.readline().decode('utf-8').strip()
            if not header_line:
                # Empty line, signaling the end of headers
                break
            if ':' not in header_line:
                # Invalid header field line, skip it
                continue
            key, value = header_line.split(":", 1)
            key = key.strip()
            value = value.strip()
            headers[key.lower()] = value
        return headers

    
    def get_header_length(self):
        header = self.parse_headers()
        length = int(header['Content-Length'])
        return length
        


# All definitions are found here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
def find_content_type(filename):
    extension = os.path.splitext(filename)[1]
    return content_type.get(extension)

# Emilie helpt me with the htlm code 
def generate_error_html_body(error_code, message):
    error_body = f"""
        <html>
        <body>
            <h1>{error_code} {message}</h1>
        </body>
        </html>
        """
    return error_body

def error_handling(error_code):
    if error_code == 404:
        message = "Not Found"
        content = "HTTP/1.1 404 Not Found \r\n"
    elif error_code == 403:
        message = "Forbidden"
        content = "HTTP/1.1 403 Forbidden \r\n"
    else:
        message = "Internal Server Error"
        content = "HTTP/1.1 500 Internal Server Error \r\n"

    # Create the error body
    error_body = generate_error_html_body(error_code, message)

    content += (
        "Content-Type: text/html \r\n" +
        "Content-Length: " + str(len(error_body)) +"\r\n\r\n"       # dont work if i do it like the others 
        + error_body)
        
    return content


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
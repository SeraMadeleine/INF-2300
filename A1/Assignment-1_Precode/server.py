#!/usr/bin/env python3
import socketserver
import os
import json 
import urllib.parse


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""


messages = []

content_type = {
    ".html": "text/html",
    ".css": "text/css",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/icon",
    ".txt": "text/plain",
    ".json": "application/json", 
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
            print(URI)
            # check that the file type is legal, .py and .md should not be leagle
            if URI.endswith('.py') or URI.endswith("md"):
                self.wfile.write(error_handling(403).encode())

            # get the index or the idex
            elif URI == "/" or URI == "/index.html" or URI == "/favicon.ico":
                # If the URI is "/" set it to be "/index.html"
                if  URI == "/":
                    URI = "/index.html"

                # Remove the / from the URI to get the filname 
                filename = URI[1:]
                self.get_request(filename, 'rb')

            elif URI == "/test.txt":
                filename = URI[1:]
                self.get_test(filename, 'r')

            elif URI.startswith('/message'):
                print("got message")
                # Handle GET request for messages
                filename = URI[1:]
                self.get_json(filename)
            
            else:
                print("ups error")
                self.wfile.write(error_handling(404).encode())
                

        elif HTTP_method == 'POST':
            if URI == "/test.txt":
                filename = URI[1:]
                self.post_request(filename)

            
            elif URI.startswith('/message'):
                # Handle POST request to create a new message
                filename = 'message.json'
                self.post_json(filename) 

            else:
                self.wfile.write(error_handling(403).encode())

        elif HTTP_method == 'PUT':
            if URI.startswith('/message'):
                filename = 'message.json'
                # Handle PUT request to update a message
                self.put_request(filename)
            else:
                # Handle other PUT requests (404)
                pass

        elif HTTP_method == 'DELETE':
            if URI.startswith('/message'):
                filename = 'message.json'

                self.delete_request(filename)
            else:
                # Handle other DELETE requests (404)
                pass

        else:
            self.wfile.write(error_handling(404).encode())
    
    def get_request(self, filename, mode):
        # Open the file and store its content for writing later 
        with open(filename, mode) as f: 
            content = f.read()
        
        # Find the content type and length 
        content_type = find_content_type(filename)
        content_lenght = len(content)

        # Create the response header 
        response_header = self.create_responseheader('200 OK', content_type, content_lenght)

        # Write the response header and the content of the file
        self.wfile.write(response_header + content)

    def get_test(self, filename, mode):
        if os.path.exists(filename):
            # __file__.replace(fila du er på (server.py), det dub vil replace med (test))
            with open(filename, mode) as f:     
                content = f.read()

                # TODO: regne ut lengden og fremdeles få den til å skrive ut alt 
                content_type = find_content_type(filename)
                response_header = (
                    b'HTTP/1.1 200 OK\r\n'+
                    f'Content-Type: {content_type}\r\n\r\n'.encode() 
                )
                self.wfile.write(response_header)

                for line in content: 
                    self.wfile.write(line.encode())     # encode() = bytes 
        else:
                    # create a response 404
                    self.wfile.write(error_handling(404).encode())                

    def get_json(self, filename):
        # Convert the 'message' list to a JSON-formatted string
        json_data = json.dumps(messages)

        # Calculate the content length
        content_length = len(json_data)

        # Determine the content type based on the filename
        content_type = find_content_type(filename)

        # Create the response header
        response_header = self.create_responseheader('200 OK', "application/json", content_length)

        # Write the response header and the JSON content to the client
        self.wfile.write(response_header + json_data.encode())


    def create_responseheader(self, response, content_type, content_lenght):
        # Create the response header 
        response_header = (
            f'HTTP/1.1 {response}\r\n'.encode()+
            f'Content-Length: {content_lenght}\r\n'.encode()+ 
            f'Content-Type: {content_type}\r\n\r\n'.encode()
        )

        return response_header

    def post_request(self, filename):
        # Determine the response status based on whether the file exists or is created.
        if os.path.exists(filename): 
            response_status = '200 OK'
            file_size = os.path.getsize(filename)
        else: 
            response_status = '201 Created'
            file_size = 0

        # Print the response status for debugging purposes
        print(response_status)

        # Read the request body with the specified Content-Length
        content_length = self.find_lenght()
        request_body = self.rfile.read(content_length).decode().strip()

        # Unquote the body to handle special characters (e.g., æ, ø, å) and update the size to include the new message 
        body = urllib.parse.unquote(request_body)[5:]  # Start at 5 to skip "text=" prefix
        file_size += len(body)

        # Append the body to the file
        with open(filename, 'ab') as f:
            f.write(body.encode() + b"\n")  # Append with a newline for better formatting

        # Read the entire content of the file
        with open(filename, "rb") as f:    
            content = f.readlines()

        # Determine the content type based on the file extension, create and write the HTTP response header
        content_type = find_content_type(filename)
        response_header = self.create_responseheader(response_status, content_type, file_size)
        self.wfile.write(response_header)

        # Write the file content to the client
        for line in content: 
            self.wfile.write(line)  # Write each line of content

    def find_lenght(self):
        # Read the HTTP request headers to extract the Content-Length
        while True:
            header_line = self.rfile.readline().decode().strip()
            if not header_line:
                # Empty line indicates the end of headers
                break
            if ':' not in header_line:
                # Skip invalid header field lines
                continue
            header_name, header_value = header_line.split(":", 1)
            if header_name == "Content-Length":
                content_length = int(header_value)

        return content_length
        
    def post_json(self, filename):
        # TODO: legg til at den skriver til en ny fil som lages hvis den ikke eksisterer 
        length = self.find_lenght()
        print("length \n", length)
        json_data = json.loads(self.rfile.read(length))       # må finne lengden av headern? og lese inn det
        new_ID = len(messages)+1
        new_message = {"ID": new_ID, "Text": json_data["text"]}

        content_length = str(len(new_message)+length)
        print("content length: \n", content_length)
        response_header = self.create_responseheader('200 OK', "application/json", content_length)

        messages.append(new_message)

        response = json.dumps(new_message)
        self.wfile.write(response_header + response.encode())
        

    def put_request(self, filename):
        """
        PUT is used to update an existing resource.

        """
        # find the lenght 
        content_lenght = 100        # TODO: må finne den faktiske lengden 
        text = self.rfile.read(content_lenght).decode()
        content_type = find_content_type(filename)

        with open(filename, "r") as f: 
            # read the file and create a list with dictionaries
            content = json.load(f)

        # Create a dictionary with the key and text 
        dictionary = json.loads(text)

        # Get the message for the corresponding ID
        for ID in content: 
            if ID['id'] == dictionary['id']:
                ID['message'] = dictionary['message']
                break
        
        with open(filename, "w") as f: 
            # write the updated list to the file
            f.write(json.dumps(content))

    def delete_request(self, filename):
        """"
        Delete the message and the related id
        """
        # find the lenght
        content_lenght = 100        # TODO: må finne den faktiske lengden
        text = self.rfile.read(content_lenght).decode()
        content_type = find_content_type(filename)

        with open(filename, "r") as f:
            # read the file and create a list with dictionaries
            content = json.load(f)
        
        dictionary = json.load(text)
        
        for ID in content:
            if ID['id'] == dictionary['id']:
                content.remove(ID)
                break
        with open(filename, 'w') as f:
            f.write(json.dumps(content))

        response_header = self.create_responseheader('200 OK', content_type, content_lenght)

        self.wfile.write(response_header)
        self.wfile.close()


# All definitions are found here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
def find_content_type(filename):
    """
    Determine the Content-Type for a given file based on its filename.
    
    Args: filename(str): The name of the file.
    
    Returns:The corresponding type if found, or None if the extension is not recognized.
    """
    # Extract the file extension from the filename (e.g., ".html").
    extension = os.path.splitext(filename)[1]

    # Lookup the type in the content_type dictionary based on the extension.
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
    elif error_code == 500:
        message = "Internal Server Error"
        content = "HTTP/1.1 500 Internal Server Error \r\n"
    else:
        print("In the error handling function, something went wrong.")

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
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

# Messages are stored in a list. The messages are represented as dictionaries, containing keys such as "ID" and "Text"
messages = []

# Dictionary that maps the file to the corresponding type
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
        request_line = self.rfile.readline().decode('utf-8').strip()    # Using utf-8 encoding in decode() ensures that bytes are correctly decoded. 
        requested_part = request_line.split()                           

        # Determine whether the request is legitimate and force the HTTP method to be uppercase and the URI to be lowercase. 
        if len(requested_part) >= 2:
            HTTP_method = requested_part[0].upper()
            URI = requested_part[1].lower()

        # Determine if the HTTP method is GET, POST, PUT, or DELETE and handle it accordingly.
        if HTTP_method == "GET":
            # Verify that the file type is legal;.py and.md should not be allowed.
            if URI.endswith('.py') or URI.endswith("md"):
                self.wfile.write(error_handling(403).encode())

            # Respond to requests for specified resources.
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
                # Handle GET request for messages
                filename = URI[1:]
                self.get_json(filename)
            
            else:
                # Return a 404 Not Found error
                self.wfile.write(error_handling(404).encode())
                

        elif HTTP_method == 'POST':
            # Handle POST request for creating a new text test.txt or message.json
            if URI == "/test.txt":
                filename = URI[1:]
                self.post_request(filename)

            
            elif URI.startswith('/message'):
                filename = 'message.json'
                self.post_json(filename) 

            else:
                # Return a 403 Forbidden error for other POST requests
                self.wfile.write(error_handling(403).encode())

        elif HTTP_method == 'PUT':
            if URI.startswith('/message'):
                # Handle PUT request to update a message
                filename = 'message.json'
                self.put_request()
            else:
                # Return a 404 Not Found error
                self.wfile.write(error_handling(404).encode())

        elif HTTP_method == 'DELETE':
            if URI.startswith('/message'):
                #  Handle DELETE request for deleting a message
                filename = 'message.json'

                self.delete_request(filename)
            else:
                # Return a 404 Not Found error
                self.wfile.write(error_handling(404).encode())

        else:
            # Return a 404 Not Found error for unsupported HTTP methods
            self.wfile.write(error_handling(404).encode())
    
    def get_request(self, filename, mode):
        """
        Handle a GET request for a specific file.

    Args:
        filename (str): The name of the file to retrieve.
        mode (str): The mode in which to open the file ('rb' for binary, 'r' for text).

    Returns:
        None
        """
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
        """
        Handle a GET request for a specific test file.

        Args:
            filename (str): The name of the file to retrieve.
            mode (str): The mode in which to open the file ('r' for text, 'rb' for binary).

        Returns:
            None
        """
        if os.path.exists(filename):
            # __file__.replace(fila du er på (server.py), det dub vil replace med (test))
            # If the file provided exists on the server
            with open(filename, mode) as f:     
                content = f.read()

                # TODO: regne ut lengden og fremdeles få den til å skrive ut alt 
                
                # Determine the content type of the file and construct an HTTP response header
                content_type = find_content_type(filename)
                response_header = (
                    b'HTTP/1.1 200 OK\r\n'+
                    f'Content-Type: {content_type}\r\n\r\n'.encode() 
                )

                # Send the response header to the client
                self.wfile.write(response_header)

                # Send the file content to the client line by line
                for line in content: 
                    self.wfile.write(line.encode())     # encode() = bytes 
        else:
            # Send a 404 Not Found response if the provided file does not exist.
            self.wfile.write(error_handling(404).encode())                

    def get_json(self, filename):
        """
        Handle a GET request for JSON data.

        Args:
            filename (str): The name of the JSON file to retrieve.

        Returns:
            None
        """
        # Convert the 'message' list to a JSON-formatted string
        json_data = json.dumps(messages)

        # Calculate the content length
        content_length = len(json_data)

        # Determine the content type based on the filename
        content_type = find_content_type(filename)

        # Make a response header and send the response header and JSON data to the client.
        response_header = self.create_responseheader('200 OK', "application/json", content_length)
        self.wfile.write(response_header + json_data.encode())


    def create_responseheader(self, response, content_type, content_lenght):
        """
        Create an HTTP response header.

        Args:
            response (str): The HTTP response status (e.g., '200 OK', '404 Not Found').
            content_type (str): The content type of the response (e.g., 'application/json').
            content_length (int): The length of the response content.

        Returns:
            bytes: The HTTP response header as bytes.
        """
        response_header = (
            f'HTTP/1.1 {response}\r\n'.encode()+
            f'Content-Length: {content_lenght}\r\n'.encode()+ 
            f'Content-Type: {content_type}\r\n\r\n'.encode()
        )

        return response_header

    def post_request(self, filename):
        """
        Handle a POST request for a specific file.

        Args:
            filename (str): The name of the file to which the data will be appended.

        Returns:
            None
        """

        # Determine the response status based on whether or not the file exists.
        if os.path.exists(filename): 
            response_status = '200 OK'
            file_size = os.path.getsize(filename)
        else: 
            response_status = '201 Created'
            file_size = 0

        # Read the request body with the specified Content-Length
        content_length = self.find_length()
        request_body = self.rfile.read(content_length).decode().strip()

        # Unquote the body to handle special characters (æ, ø, å) and update the size to incorporate the new message. 
        body = urllib.parse.unquote(request_body)[5:]  # Start at 5 to skip "text=" prefix
        file_size += len(body)

        # Append the body to the file
        with open(filename, 'ab') as f:
            f.write(body.encode() + b"\n")  # Append with a newline for better formatting

        # Read the entire content of the file
        with open(filename, "rb") as f:    
            content = f.readlines()

        # Determine the content type depending on the file extension, then construct and write the HTTP response header.
        content_type = find_content_type(filename)
        response_header = self.create_responseheader(response_status, content_type, file_size)
        self.wfile.write(response_header)

        # Write the file content to the client
        for line in content: 
            self.wfile.write(line)  # Write each line of content

    def find_length(self):
        """
        Extract the Content-Length from the HTTP request headers.

        Returns:
            int: The Content-Length value extracted from the headers.
        """
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
        """
        Handle a POST request to append JSON data to a file and respond with JSON data.

        Args:
            filename (str): The name of the file to append JSON data to.

        Returns:
            None
        """
        length = self.find_length()
        print("length \n", length)

        # Use the Content-Length header to get the length of the JSON data.
        json_data = json.loads(self.rfile.read(length))    

        # Generate a new message with a unique ID and the text from the JSON data.
        new_ID = len(messages) + 1
        new_message = {"ID": new_ID, "Text": json_data["text"]}

        # Calculate the content length of the response JSON data and retrieve the content length of the response JSON data
        response_content = json.dumps(new_message, indent=4)  # Format with proper indentation (to get them below eachoter) source: https://pynative.com/python-prettyprint-json-data/
        content_length = len(response_content)
        
        # Create an HTTP response header
        response_header = self.create_responseheader('200 OK', "application/json", content_length)

        # Append the new message to the 'messages' list
        messages.append(new_message)

        # Convert the new message to JSON and send it as the response
        response = json.dumps(new_message, indent=4)
        self.wfile.write(response_header)  # Write the response header

        # Write the formatted JSON content to the response
        self.wfile.write(response_content.encode())
        
    def put_request(self):
        """
        Handle a PUT request to update a message with new content.
        """
        # Parse the JSON request body
        content_length = self.find_length()
        json_data = json.loads(self.rfile.read(content_length).decode())

        # Find the ID in the request data
        message_id = json_data.get("ID")

        if message_id is None:
            # Return an error response if the ID is missing in the request
            response_header = self.create_responseheader('400 Bad Request', "application/json", 0)
            self.wfile.write(response_header)
            return

        # Search for the message with the given ID
        updated = False
        for message in messages:
            if message["ID"] == message_id:
                # Update the message's text with the new content
                message["Text"] = json_data["Text"]
                updated = True
                break

        if updated:
            # Respond with a success status code
            response_header = self.create_responseheader('200 OK', "application/json", 0)
            self.wfile.write(response_header)
        else:
            # If the message with the given ID doesn't exist, return a not found error
            response_header = self.create_responseheader('404 Not Found', "application/json", 0)
            self.wfile.write(response_header)

    def delete_request(self, filename):
        """
        Handle a DELETE request to remove a message with a specific ID.

        Args:
            filename (str): The name of the file (not used in this context).

        Returns:
        None
        """
        # Read the request body to get the ID of the message to be deleted
        content_length = self.find_length()
        json_data = json.loads(self.rfile.read(content_length).decode())

        # Find the ID in the request data
        message_id = json_data.get("ID")

        if message_id is None:
            # Return an error response if the ID is missing in the request
            response_header = self.create_responseheader('400 Bad Request', "application/json", 0)
            self.wfile.write(response_header)
            return

        # Search for the message with the given ID
        deleted = False
        for message in messages:
            if message["ID"] == message_id:
                # Delete the message and free its ID
                messages.remove(message)
                deleted = True
                break

        if deleted:
            # Respond with a success status code
            response_header = self.create_responseheader('200 OK', "application/json", 0)
            self.wfile.write(response_header)
        else:
            # If the message with the given ID doesn't exist, return a not found error
            response_header = self.create_responseheader('404 Not Found', "application/json", 0)
            self.wfile.write(response_header)



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

def generate_error_html_body(error_code, message):
    """
    Generate an HTML body for displaying an error message.

    Args:
        error_code (int): The HTTP error code.
        message (str): The error message.

    Returns:
        str: The HTML body as a string.
    """
    error_body = f"""
        <html>
        <body>
            <h1>{error_code} {message}</h1>
        </body>
        </html>
        """
    return error_body

def error_handling(error_code):
    """
    Generate an HTTP response for a given error code.

    Args:
        error_code (int): The HTTP error code.

    Returns:
        str: The complete HTTP response as a string, including headers and error message body.
    """
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
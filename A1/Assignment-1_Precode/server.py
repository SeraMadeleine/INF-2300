#!/usr/bin/env python3
import socketserver
import os
import json 
import urllib.parse
from error_handling import *
from HTTP_handler import HTTPHandler


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""


# Instans
handle_error = Error()

# Messages are stored in a list. The messages are represented as dictionaries, containing keys such as "ID" and "Text"
messages = []


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
        else:
            self.wfile.write(handle_error.error_handling(400).encode())
            return

        if URI.endswith('.py') or URI.endswith("md"):
            self.wfile.write(handle_error.error_handling(403).encode())
            return

        # Determine if the HTTP method is GET, POST, PUT, or DELETE and handle it accordingly.
        if HTTP_method == "GET":
            self.handle_GET(URI)
        elif HTTP_method == 'POST':
            self.handle_POST(URI)
        elif HTTP_method == 'PUT':
            self.handle_PUT(URI)
        elif HTTP_method == 'DELETE':
            self.handle_DELETE(URI)
        else:
            self.wfile.write(handle_error.error_handling(405).encode())     # Method Not Allowed
    
    def handle_GET(self, URI):
        if URI == "/" or URI == "/index.html" or URI == "/favicon.ico" or URI == "/test.txt":
                # If the URI is "/" set it to be "/index.html"
            if  URI == "/":
                URI = "/index.html"

            # Handle the GET request for the correct uri
            self.get_request(self.get_filname(URI), 'rb')

        elif URI.startswith('/message'):
            print("got message")
            # Handle GET request for messages
            URI = "/message.json"
            self.get_json(self.get_filname(URI))
        
        else:
            self.wfile.write(handle_error.error_handling(404).encode())

    def handle_POST(self, URI):
        if URI == "/test.txt":
            self.post_request(self.get_filname(URI))

        
        elif URI.startswith('/message'):
            URI = "/message.json"
            # Handle POST request to create a new message
            self.post_json(self.get_filname(URI)) 

        else:
            # Return a 403 Forbidden error for other POST requests
            self.wfile.write(handle_error.error_handling(403).encode())

    def handle_PUT(self, URI):
        if URI.startswith('/message'):
            URI = "/message.json"
            self.put_request(self.get_filname(URI))
        else:
            self.wfile.write(handle_error.error_handling(404).encode())

    def handle_DELETE(self, URI):
        if URI.startswith('/message'):
            #  Handle DELETE request for deleting a message
            URI = "/message.json"
            self.delete_request(self.get_filname(URI))
        else:
            # Return a 404 Not Found error
            self.wfile.write(handle_error.error_handling(404).encode())

    def get_request(self, filename, mode):
        """
        Handle a GET request for a specific file.

        Args:
            filename (str): The name of the file to retrieve.
            mode (str): The mode in which to open the file ('rb' for binary, 'r' for text).

        Returns:
            None
        """     

        if not os.path.exists(filename):
            self.wfile.write(handle_error.error_handling(404).encode())
            return

        # Open the file and store its content for writing later 
        with open(filename, mode) as f: 
            content = f.read()
        
        # Find the content type and length 
        content_type = HTTPHandler.find_content_type(filename)
        content_lenght = len(content)

        # Create the response header 
        response_header = HTTPHandler.create_response_header('200 OK', content_type, content_lenght)

        # Write the response header and the content of the file
        self.wfile.write(response_header + content)

    def get_json(self, filename):
        """
        Handle a GET request for JSON data.

        Args:
            filename (str): The name of the JSON file to retrieve.

        Returns:
            None
        """
        if not os.path.exists(filename):
            # Send a 404 Not Found response if the file does not exist
            self.wfile.write(handle_error.error_handling(404).encode())
            return

        # Convert the 'message' list to a JSON-formatted string
        json_data = json.dumps(messages, indent=4)

        # Calculate the content length
        content_length = len(json_data)

        # If there are no messages or only empty brackets in the JSON data, send a custom error response
        if content_length <= 2: 
            self.wfile.write(handle_error.error_handling(204).encode())
            return

        # Make a response header and send the response header and JSON data to the client.
        response_header = HTTPHandler.create_response_header('200 OK', "application/json", content_length)
        self.wfile.write(response_header + json_data.encode())

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

        # Determine the content type based on the file extension
        content_type = HTTPHandler.find_content_type(filename)
        response_header = HTTPHandler.create_response_header(response_status, content_type, file_size)
        self.wfile.write(response_header)

        # Write the file content to the client
        for line in content: 
            self.wfile.write(line)  # Write each line of content

        
    def post_json(self, filename):
        """
        Handle a POST request to append JSON data to a file and respond with JSON data.

        Args:
            filename (str): The name of the file to append JSON data to.

        Returns:
            None
        """

        # Determine the response status based on whether or not the file exists.
        response_status = '200 OK' if os.path.exists(filename) else '201 Created'


        content_length = self.find_length()

        # Use the Content-Length header to get the length of the JSON data.
        json_data = json.loads(self.rfile.read(content_length))    

        # Generate a new message with a unique ID and the text from the JSON data.
        
        # Check if there are available IDs; if so, reuse the smallest one
        new_ID = 1  # Start with ID 1

        # Find the smallest unused ID by iterating through existing messages
        while any(message["ID"] == new_ID for message in messages):
            new_ID += 1

        new_message = {"ID": new_ID, "Text": json_data["text"]}

        # Calculate the content length of the response JSON data and retrieve the content length of the response JSON data
        response_content = json.dumps(new_message, indent=4)  # Format with proper indentation (to get them below eachoter) source: https://pynative.com/python-prettyprint-json-data/
        content_length = len(response_content)
        
        # Create an HTTP response header
        response_header = HTTPHandler.create_response_header(response_status, "application/json", content_length)

        # Append the new message to the 'messages' list
        messages.append(new_message)

        # Write the response header and its content
        self.wfile.write(response_header + response_content.encode())  

        # Save the updated 'messages' list to the storage file
        self.save_messages_to_file(filename)
        
    def put_request(self, filename):
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
            self.send_error_response('404 Not Found', "application/json", 0)
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
            # Respond with a success status code and save the updated messages
            self.send_error_response('200 OK', "application/json", 0)
            self.save_messages_to_file("message.json")
        else:
            # If the message with the given ID doesn't exist, return a not found error
            self.send_error_response('404 Not Found', "application/json", 0)


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
            
            response_header = HTTPHandler.create_response_header('404 Not Found', "application/json", 0)
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
            response_header = HTTPHandler.create_response_header('200 OK', "application/json", 0)
            self.wfile.write(response_header)
        else:
            # If the message with the given ID doesn't exist, return a not found error
            print(f"Message with ID {message_id} not found.")
            response_header = HTTPHandler.create_response_header('404 Not Found', "application/json", 0)
            self.wfile.write(response_header)
        
        # Save the updated 'messages' list to the storage file
        self.save_messages_to_file(filename)

    def send_error_response(self, status_code, type, content_length):
        """
        Send an error response with the specified status code and error message.

        Args:
            status_code (int): The HTTP status code for the error response.
            content_length (int, optional): The length of the response body. If not provided, it will be calculated.

        Returns:
            None
        """
        response_header = HTTPHandler.create_response_header(status_code, type, content_length)
        self.wfile.write(response_header)
    
    def save_messages_to_file(self, filename):
        """
        Save messages from the 'messages' list into a storage file (e.g., message.json).
        """
        with open(filename, 'w') as storage_file:
            json.dump(messages, storage_file, indent=4)  
    
    def get_filname(self, URI):
        filename = URI[1:]
        return filename

    def find_length(self):  
        """
        Extract the Content-Length from the HTTP request headers.

        Returns:
            int: The Content-Length value extracted from the headers.
        """
        content_length = 0

        #  Read the HTTP request headers until an empty line is encountered 
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
                content_length = int(header_value.strip())

        return content_length


def load_messages_from_file():
    """
    Load messages from a storage file (e.g., message.json) into the 'messages' list.
    """
    global messages
    if os.path.exists("message.json"):
        with open("message.json", 'r') as storage_file:
            messages = json.load(storage_file)
    



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        load_messages_from_file()             # Added so that the message from the json file may be loaded and maintained even if the server goes down.
        server.serve_forever()
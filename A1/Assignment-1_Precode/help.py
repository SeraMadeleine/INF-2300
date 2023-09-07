#!/usr/bin/env python3

import socketserver
import os
import json



class MyHTTPHandler(socketserver.StreamRequestHandler):
    """
    The server will create a new instance of this class for every request.
    Since it inherits from the StreamRequestHandler class, it has two very
    useful attributes you can use:

    rfile - This is the whole content of the request as a python
    file-like object. This means we can do readline(), readlines() on it!
    See `https://docs.python.org/3/library/io.html#io.BufferedReader`

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we call wfile.close() the response is
    automatically sent to the client.
    See `https://docs.python.org/3/library/io.html#io.BufferedWriter`

    The class has three important methods:
    handle() - is called to handle each request.
    setup() - Does nothing by default, but can be used to do any initial
    tasks before handling a request. Is automatically called before handle().
    finish() - Does nothing by default, but is called after handle() to do any
    necessary clean up after a request is handled.
    """

    # GET is used to request data from a specified resource
    def GET(self, splitHeader):

        if splitHeader[1] == "/" or splitHeader[1] == "/index.html":
            path = "/index.html"

            # Opening file, and if not possible, returning an error code
            try:
                with open(path[1:], "r") as f: # removing "/"" with [1:]
                    self.data = f.read()

            except:
                response = "HTTP/1.1 404 Not Found\r\n"
                self.wfile.write(response.encode())

            self.contentType = "text/html"

        elif splitHeader[1] == "/messages":
            path = "/messages.json"
            self.contentType = "application/json"
            with open(path[1:], "r") as output:
                self.lists = json.load(output) # read file and create list
                self.data = json.dumps(self.lists, indent=4) # data tab=4

        # If server.py, error code so it wont reveal any data
        elif splitHeader[1].endswith("py") or splitHeader[1].endswith("md"): # .py og md filer
            response = "HTTP/1.1 403\r\n"
            self.wfile.write(response.encode()) # encode fra string til bytes

        #filesize = os.path.getsize(path[1:])
        response = "HTTP/1.1 200 OK\r\n"
        contentLength = f"Content-Length: {len(self.data)}\r\n"
        contentType = "Content-Type: {} \r\n\r\n".format(self.contentType)
        response = response + contentLength + contentType + self.data
        self.wfile.write(response.encode()) # encode fra string til bytes
        self.wfile.close()


    # POST is used to send data to a server to create/update a resource
    def POST(self, splitHeader, headerDict):
    # The response code line has the for <version> <responsecode> <responsestring>

        if splitHeader[1] == "/test.txt":

            length = int(headerDict["Content-Length"])
            text = self.rfile.read(length).decode()
            text = text[5:] + "\n"

            writeHeaderFile = open(splitHeader[1][1:], "a")
            writeHeaderFile.write(text)
            writeHeaderFile = open(splitHeader[1][1:], "r")
            response = "HTTP/1.1 200 OK\r\n"
            body = writeHeaderFile.read()
            filesize = len(body)
            contentLength = f"Content-Length: {filesize} \r\n"

        # The response should be 201 - Created and a body containing the newly created message object
        elif splitHeader[1] == "/messages": # messages is the body
            length = int(headerDict["Content-Length"])
            text = self.rfile.read(length).decode()
            path = "/messages.json"
            self.contentType = "application/json"

            try:
                with open(path[1:], "r") as output:
                    new_list = json.load(output) # read file and create list
                    dictionary = json.loads(text) # dictionary with a key and text
                    number = new_list[-1]["id"]+1 # getting the last one in the list (will not work with an empty list)
                    dictionary["id"] = number
                    new_list.append(dictionary)

                with open(path[1:], "w") as new_output: # delete all and write from beginning
                    json.dump(new_list, new_output)

                    body = json.dumps(dictionary)
                    filesize = len(body)
                    contentLength = f"Content-Length: {filesize} \r\n" # POST requests have no restrictions on data length ?
                    contentType = "Content-Type: application/json\r\n\r\n"

            # If the resource does not exist, create a new
            except:
                empty_list = []
                dictionary = json.loads(text)
                number = 0
                dictionary["id"] = number
                empty_list.append(dictionary)

                with open(path[1:], "w") as new_output: # delete all and write from beginning
                    json.dump(empty_list, new_output)

                    body = json.dumps(dictionary)
                    filesize = len(body)
                    contentLength = f"Content-Length: {filesize} \r\n" # POST requests have no restrictions on data length ?
                    contentType = "Content-Type: application/json\r\n\r\n"

            response = "HTTP/1.1 201 CREATED\r\n"

        response = response + contentLength + contentType + body
        self.wfile.write(response.encode()) # encode fra string til bytes
        self.wfile.close()

    # RESTful Web API supporting GET, POST, PUT and DELETE to /messages using JSON-formatted messages
    # PUT used to update existing resource
    def PUT(self, splitHeader, headerDict):

        if splitHeader[1] == "/messages":
            path = "/messages.json"

            length = int(headerDict["Content-Length"])
            text = self.rfile.read(length).decode()
            self.contentType = "application/json"

            with open(path[1:], "r") as output:
                new_list = json.load(output) # read file and create list with dictionaries

            dictionary = json.loads(text) # dictionary with a key and text

            # Find the message with the corresponding id and replace the text-field with the one from the request
            for similar_id in new_list:
                if dictionary["id"] == similar_id["id"]:
                    similar_id["text"] = dictionary["text"]

            with open(path[1:], "w") as new_output: # delete all and write from beginning
                new_output.write(json.dumps(new_list))


    def DELETE(self, splitHeader, headerDict):
        # the corresponding id and remove the message. Response should be 200 - Ok.

        if splitHeader[1] == "/messages":
            path = "/messages.json"

            length = int(headerDict["Content-Length"])
            text = self.rfile.read(length).decode()
            contentType = "application/json"
            response = "HTTP/1.1 200 OK\r\n"

            with open(path[1:], "r") as output:
                new_list = json.load(output) # read file and create list with dictionaries

            dictionary = json.loads(text) # dictionary with a key and text

            # Find the message with the corresponding id and remove the message
            for similar_id in new_list:
                if dictionary["id"] == similar_id["id"]:
                    new_list.remove(similar_id)

            with open(path[1:], "w") as new_output: # delete all and write from beginning
                new_output.write(json.dumps(new_list))

        response = response + contentType
        self.wfile.write(response.encode()) # encode fra string til bytes
        self.wfile.close()

    def handle(self):
        """ This method is responsible for handling an HTTP request """

        # Starts with an empty string
        headers = ""

        while True:
            header = self.rfile.readline().decode() # decode fra bytes til string
            if header == "\r\n": # When redline returns a \r\n its at the end
                break # Breaks when it reaches the body
            headers += header # Adding to every line

        headers = headers.split("\r\n")
        headers.remove("")

        firstLine = headers[0]

        # Create an empty dictionary
        headerDict = {}
        for line in headers:
            if line == firstLine:
                continue
            tmp = line.split(": ") # colons (:) on a path denotes a variable
            headerDict[tmp[0]] = tmp[1]

        splitHeader = headers[0].split(" ")

        if splitHeader[0] == "GET":
            self.GET(splitHeader)
        elif splitHeader[0] == "POST":
            self.POST(splitHeader, headerDict)
        elif splitHeader[0] == "PUT":
            self.PUT(splitHeader, headerDict)
        elif splitHeader[0] == "DELETE":
             self.DELETE(splitHeader, headerDict)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyHTTPHandler)
    try:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        server.shutdown()

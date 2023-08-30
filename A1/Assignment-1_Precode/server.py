#!/usr/bin/env python3
import socketserver


"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""

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

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we do wfile.close(), the response is
    automatically sent.

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
        # self.wfile.write(b"HTTP/1.1 200 OK \r\n")  # commented out to get the webpage up 

        # Request, parse, and process the requested link 
        request = self.rfile.readline().decode('utf-8').strip() # By using utf-8 encoding in decode(), you ensure that the bytes are properly decoded 
        print("Request received!", request)

        requested_part = request.split()

        """ 
        The function must return index.html in the response body if the method is GET.  This is true for the / and /index.html Uniform Resource Identifiers (URIs).
        If a resource does not exist, the get should return 404 - not found with an optional body. The same applies for a request to a forbidden resource,
        however, it should return 403 - forbidden.
        """
        # Check if the request line contains at least two parts (HTTP method and URI)
        if len(requested_part) >= 2: 
            HTTP_method = requested_part[0].upper()     # Force it to be upper for case insensitivity
            URI = requested_part[1].lower()

            if HTTP_method == "GET":
                if URI == "/" or URI == "/index.html": 
                    # Read the content of index.html as bytes
                    with open("index.html", "rb") as f:
                        content = f.read()
                    
                    # Calculate the content length 
                    contentLength = len(content)

                    # Create the responce header
                    response_headers = (
                    b'HTTP/1.1 200 OK\r\n'
                    b'Content-Type: text/html\r\n'
                    b'Content-Length: %d \r\n\r\n' %contentLength
                    )

                    # Write the responsheader and the content of the page 
                    self.wfile.write(response_headers)
                    self.wfile.write(content)

                else:
                    self.wfile.write(b'404 - Not Found \r\n')

            if URI == 'POST': 
                if URI == '/test.txt': 
                    pass 
                else: 
                    self.wfile.write(b'403 - Forbidden')

    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()

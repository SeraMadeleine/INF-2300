class Error:
    """
    Error class for generating HTTP error responses.

    This class provides methods to generate HTML error bodies and complete
    HTTP error responses for different HTTP error codes.

    Attributes:
        None

    Methods:
        generate_error_html_body(error_code, message):
            Generate an HTML body for displaying an error message.

        error_handling(error_code):
            Generate an HTTP response for a given error code, including headers and error message body.
    """
    def generate_error_html_body(self, error_code, message):
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

    
    def error_handling(self, error_code):
        """
        Generate an HTTP response for a given error code.

        Args:
            error_code (int): The HTTP error code.

        Returns:
            str: The complete HTTP response as a string, including headers and error message body.
        """
        
        if error_code == 204:
            message = "No Content"
            content = "HTTP/1.1 204 No Content \r\n"
        elif error_code == 400:
            message = "Bad Request"
            content = "HTTP/1.1 400 Bad Request \r\n"
        elif error_code == 403:
            message = "Forbidden"
            content = "HTTP/1.1 403 Forbidden \r\n"
        elif error_code == 404:
            message = "Not Found"
            content = "HTTP/1.1 404 Not Found \r\n"
        elif error_code == 405:
            message = "Method Not Allowed"
            content = "HTTP/1.1 405 Method Not Allowed \r\n"
        elif error_code == 500:
            message = "Internal Server Error"
            content = "HTTP/1.1 500 Internal Server Error \r\n"
        else:
            print("In the error handling function, something went wrong.")

        # Create the error body
        error_body = self.generate_error_html_body(error_code, message)

        content += (
            "Content-Type: text/html \r\n" +
            "Content-Length: " + str(len(error_body)) +"\r\n\r\n"       # dont work if i do it like the others 
            + error_body)
            
        return content

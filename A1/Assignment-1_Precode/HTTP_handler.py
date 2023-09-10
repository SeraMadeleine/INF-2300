import os

class HTTPHandler:
    """
    A utility class for handling HTTP-related tasks such as creating response headers
    and determining content types based on file extensions.
    """

    CONTENT_TYPE = {
        ".html": "text/html",
        ".css": "text/css",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".ico": "image/icon",
        ".txt": "text/plain",
        ".json": "application/json",
    }

    @staticmethod
    def create_response_header(response, content_type, content_length):
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
            f'HTTP/1.1 {response}\r\n'.encode() +
            f'Content-Length: {content_length}\r\n'.encode() +
            f'Content-Type: {content_type}\r\n\r\n'.encode()
        )

        return response_header

    @staticmethod
    def find_content_type(filename):
        """
        Determine the Content-Type for a given file based on its filename.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The corresponding type if found, or None if the extension is not recognized.
        """
        # Extract the file extension from the filename (e.g., ".html").
        extension = os.path.splitext(filename)[1]

        # Lookup the type in the CONTENT_TYPE dictionary based on the extension.
        return HTTPHandler.CONTENT_TYPE.get(extension)

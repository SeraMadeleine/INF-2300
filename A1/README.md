
## Running the Program


1. Open a terminal and navigate to the project directory.

2. Start the server by running the following command:
    ```
    python3 server.py
    ```

   This command will start the server, and you can now open a webbrowser with the following IPaddress `http://localhost:8080`.

   NB: for my mac, the Post for text only works in firefox

## Running Tests

To test the server, you can use the provided `test_client.py` script. Follow these steps:

1. Make sure the server is running 
2. Open a new terminal and navigate to the project directory. 
3. To run the tests, execute the following command:

    ```
    python3 test_client.py
    ```

## Interacting with the Server

You can interact with the server using HTTP methods (GET, POST, PUT, DELETE) to manage messages. When testing the program HTTPIE was used, so there are no guaranti that it will work for enything else. 

### Deleting a Message

To delete a message with a specific ID, you can use the `http DELETE` command as follows:

    
    http DELETE http://localhost:8080/message <<< '{"ID": 1}'
    

Replace `1` with the ID of the message you want to delete.

### Getting Messages

To retrieve a list of messages, you can use the `http GET` command:

    
    http GET http://localhost:8080/message
    

This will retrieve all messages in JSON format.

### Posting a Message

To create a new message, you can use the `http POST` command:

    
    http POST http://localhost:8080/message text="Your message text here"
    

Replace `"Your message text here"` with the text of the message you want to post.

### Updating a Message

To update the text of an existing message, you can use the `http PUT` command as follows:

    
    http PUT http://localhost:8080/message.json <<< '{"ID": 1, "Text": "New text for the message"}'
    

Replace `1` with the ID of the message you want to update and `"New text for the message"` with the new text.


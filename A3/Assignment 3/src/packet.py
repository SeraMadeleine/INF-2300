class Packet:
    """Represent a packet of data.
    Note - DO NOT REMOVE or CHANGE the data attribute!
    The simulation assumes this is present!"""

    def __init__(self, binary_data):
        # Add which ever attributes you think you might need
        # to have a functional packet.
        self.data = binary_data
        self.checksum = 0 
        self.ack = False            # True when sending response to Alice 
        self.seqnr = None           # Set when packet is sendt 
        self.retry_count = 0        # Number of times a packet has been retransmitted or resent
        self.payload_type = "data"  # Payload type: "data" or "ack"
        self.status = "created"     # Status attribute to track packet status


    
    # Extend me!
    def mark_packet(self, mark):
        """
        Identify whether a packet is a data packet or an ACK packet based on the 'mark' parameter.

        Args:
            mark (str): The mark to set the packet type. Use "ack" for acknowledgment packets or "data" for data packets.
        """
        if mark == "ack":
            self.ack = True
            self.payload_type = "ack"
        elif mark == "data":
            self.ack = False
            self.payload_type = "data"

    def increment_retry_count(self):
        """Increment the retry count to track the number of retransmissions."""
        self.retry_count += 1

    def set_status(self, status):
        """Track the current state or status of a packet within the network protocol.

        Args:
            status (str): The status to set for the packet (e.g., "created," "sent," "received," "acknowledged").
        """
        self.status = status
    
    def __repr__(self):
        return  f"Number: {self.seqnr} - Data: {self.data} "
    
    # TIPS: Add a __str__ method to print a packet-object nicely! :)
    def __str__(self) -> str:
        return f"Number: {self.seqnr} - Data: {self.data} - ACK: {self.ack}"



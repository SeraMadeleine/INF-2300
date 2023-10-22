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
        self.seqnr = 0              # Set when packet is sendt 
        self.retry_count = 0        # Number of times a packet has been retransmitted or resent
        self.sendt = False     # Status attribute to track packet status
        self.ack = False


    
    # Extend me!

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



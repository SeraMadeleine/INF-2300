from collections import deque

from copy import copy
from threading import Timer

from packet import Packet
from config import *
import time



class TransportLayer:
    """
    The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """

    def __init__(self):
        # Initialize instance variables
        self.timer          = None
        self.timeout        = 0.4           # Seconds
        self.window_size = WINDOW_SIZE      # Window size, value sat in config 
        self.packets_window = []            # Buffer for sending packets
        self.window_start   = 0             # Start positions within the list of packets
        self.window_end     = 0             # End positions within the list of packets
        self.seqnr          = 0             # Sequence number, increm for all pacets 
        self.expected_seqnr = 0             # The expected data sequence number
        self.expected_ack   = 0             # The last acknowledged sequence number
        self.debug          = False          # Set to false if you do not want debug prints       


    def calculate_checksum(self, data):
        """
        Calculate a simple XOR-based checksum for the data.

        Args:
            data (bytes): The data for which the checksum is calculated.

        Returns:
            int: The calculated checksum.
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def debugger(self, message):
        """
        A helper method to print debugging messages if debugging is enabled.

        Args:
            message (str): The message to print.
        """
        if self.debug == True:
            self.logger.debug(message)

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer


    # Alice 
    def from_app(self, binary_data):
        """ 
        Sending data from the application layer to the network layer.

        Args:
            binary_data (bytes): The data to send.
        """

        if binary_data is None: 
            self.debugger(f"Binary data is {binary_data}, something is wrong")
            return

        if not self.packets_window or self.packets_window[-1].seqnr != self.seqnr:
            # Wait until there is space in the window
            while len(self.packets_window) >= self.window_size:
                self.debugger("Window is full, waiting for space")
                time.sleep(1)

            # Create a packet with the binary data, sequence number, and checksum.
            packet = Packet(binary_data)
            packet.seqnr = self.seqnr
            self.seqnr += 1

            # Calculate the data's checksum. This is done to determine whether or not the data is corrupted. 
            packet.checksum = self.calculate_checksum(binary_data)  

            # Append the packet to the window
            self.debugger(f"append packet nr {self.seqnr} \n")
            self.packets_window.append(packet)
            self.window_end = self.seqnr
            self.debugger(f"window: {self.packets_window} \n")

            self.network_layer.send(packet)
            self.reset_timer(self.handle_timeout)


    def from_network(self, packet):
        """ 
        Receiving data from the network layer.

        Args:
            packet (Packet): The received packet.
        """
        
        self.debugger(self.packets_window)
        
        if packet.ack:
            # Handling acknowledgment packets
            self.handle_ack_packet(packet)
        else:
            # Handling data packets.
            self.handle_data_packet(packet)


    # BOB 
    def handle_data_packet(self, packet):
        """
        Receiving data from the network layer.

        Args:
            packet (Packet): The received packet.
        """
    
        # Calculate the checksum of the received data
        received_checksum = packet.checksum

        if packet.seqnr <= self.expected_seqnr:     
            self.debugger(f"Recived data packet with seqnr: {packet.seqnr}, expected:  {self.expected_seqnr} \n")

            # Calculate the checksum of the received data
            calculated_checksum = self.calculate_checksum(packet.data)

            # Check if the received checksum is equal to the calculated checksum
            if received_checksum == calculated_checksum:
                self.debugger(f"checksums {received_checksum} == {calculated_checksum}")

                # Send ACK for the received packet using self.network_layer.send.
                packet.ack = True
                self.debugger("Sending ack")
                self.network_layer.send(packet)
                self.expected_ack = packet.seqnr + 1           

                if packet.seqnr == self.expected_seqnr:
                    self.expected_seqnr += 1
                    self.application_layer.receive_from_transport(packet.data)
            else: 
                # Checksums do not match; data is corrupt
                self.debugger("Received corrupt data ({received_checksum} != {calculated_checksum}). Dropping the packet, not sending ACK.\n")

        elif packet.seqnr > self.expected_ack:
            # Sett starten på vinduet til der det elementet er i lista 
            self.debugger(f"Received future data packet: expected: {self.expected_ack}\n")


    # ALICE 
    def handle_ack_packet(self, packet):
        """
        Handling received Ack packets.

        Args:
            ACK (ack): The received ack.
        """
    
        # mindre eller expecte 
        if packet.seqnr >= self.expected_seqnr:    
            self.debugger(f"Alice recived ACK.  ack seqnr:{packet.seqnr} = exp seqnr: {self.expected_ack} \n")
            self.expected_ack = packet.seqnr
            
            # Slide the window to the right
            while self.packets_window and self.packets_window[0].seqnr <= packet.seqnr: 
                self.packets_window.pop(0)
                self.debugger(f"Pop packet nr {packet.seqnr}")
                self.window_start = self.expected_ack +1 
                self.expected_ack += 1
        else:
            self.debugger(f"Ignoring out-of-order ACK packet with seqnr: {packet.seqnr}, expected: {self.expected_seqnr}")

        # Reset timer 
        if self.packets_window:
            self.reset_timer(self.handle_timeout)
            self.debugger("Resetting timer \n")


    def handle_timeout(self):
        """
        Handle the timeout event by retransmitting unacknowledged packets.
        """
        self.debugger("Timeout occurred. Retransmitting unacknowledged packets\n")

        # Retransmit all unacknowledged packets
        for packet in self.packets_window:
            self.network_layer.send(packet)
        
        # Reset timer
        self.reset_timer(self.handle_timeout)
        

    def reset_timer(self, callback, *args):
        # This is a safety-wrapper around the Timer-objects, which are
        # separate threads. If we have a timer-object already,
        # stop it before making a new one so we don't flood
        # the system with threads!
        if self.timer:
            if self.timer.is_alive():
                self.timer.cancel()
        # callback(a function) is called with *args as arguments
        # after self.timeout seconds.

        # Only reset the timer if there are unacknowledged packets in the window
        if self.packets_window:
            self.timer = Timer(self.timeout, callback, *args)
            self.timer.start()


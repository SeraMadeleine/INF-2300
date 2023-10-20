from copy import copy
from threading import Timer

from packet import Packet
from config import *


class TransportLayer:
    """
    The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """


    def __init__(self):
        self.timer = None
        self.timeout = 0.4              # Seconds
        self.window_size = WINDOW_SIZE  # Number of packets that can be in flight simultaneously
        self.packets_window = []        # Buffer for sending packets
        self.window_start = 0           # Start positions within the list of packets
        self.window_end = 0             # End positions within the list of packets
        self.seqnr = 0                  # Sequence number, increm for all pacets 
        self.expected_seqnr = 0         # The expected data sequence number
        self.expected_ack = 0           # The last acknowledged sequence number
        self.debug = True               # Set to false if you do not want debug prints 

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


    def from_app(self, binary_data):
        """ 
        Sending data from the application layer to the network layer.

        Args:
            binary_data (bytes): The data to send.
        """

        # self.debugger(f"window: {self.packets_window}")

        if len(self.packets_window) <= self.window_size and self.seqnr <= PACKET_NUM:
            packet = Packet(binary_data)
            # Create a packet with the binary data and assign a sequence number.

            # Set seqnr for packet and self
            packet.seqnr = self.seqnr
            self.seqnr += 1

            # Append the packet to the window 
            self.packets_window.append(packet)
            self.debugger(f"window: {self.packets_window}")

            # self.network_layer.send(packet)
            # if self.window_start == packet.seqnr:
                # self.reset_timer(self.retransmit_packets)
        
            self.network_layer.send(packet)


    def from_network(self, packet):
        """ 
        Receiving data from the network layer.
        """
        self.application_layer.receive_from_transport(packet.data)
        self.debugger(self.packets_window)
        
        if packet.payload_type == "ack":
            # Handling acknowledgment packets
            self.handle_ack_packet(packet)
        elif packet.payload_type == "data" and packet.seqnr <= PACKET_NUM:
            # Handling data packets.
            self.handle_data_packet(packet)
        


    def handle_data_packet(self, packet):
        """
        Receiving data from the network layer.

        Args:
            packet (Packet): The received packet.
        """
        self.debugger("Recived data packet \n")
        self.debugger(f"expected_seqnr: {self.expected_seqnr} \n")
        self.debugger(f"packet.seqnr: {packet.seqnr} \n")
        if packet.seqnr == self.expected_seqnr:
            # Slide the window to the right if possible but not beyond PACKET_NUM.
            while self.packets_window and self.packets_window[0].seqnr < self.window_start and self.window_start <= PACKET_NUM:
                self.packets_window.pop(0)
                print(self.packets_window)
                # self.window_start += 1

            # Send ACK for the received packet using self.network_layer.send.
            ack_packet = Packet(packet.data)
            ack_packet.mark_packet("ack")
            ack_packet.seqnr = packet.seqnr  # Use the seqnr of the received packet
            self.expected_seqnr += 1
            self.network_layer.send(ack_packet)
            # self.reset_timer()  # Reset the timer when an ACK is received.
        elif packet.seqnr < self.expected_ack:
            self.debugger(f"Acknowledging older packet, expected ack: {self.expected_ack} \n")
        else:
            self.debugger(f"Received future data packet: expected: {self.expected_ack}\n")


    def handle_ack_packet(self, ack):
        """
        Handling received data packets.

        Args:
            ACK (ack): The received ack.
        """
        ack_seqnr = ack.seqnr

        if ack_seqnr == self.window_start:
            self.debugger(f"Received ACK for packet {ack_seqnr}. \n")
            self.window_start += 1
            while self.packets_window and self.packets_window[0].seqnr < self.window_start:
                self.packets_window.pop(0)
            # if self.window_start < self.seqnr:
            #     self.reset_timer(self.retransmit_packets)
        elif ack.payload_type == "data":
            if ack.seqnr == self.expected_ack:
                ack_packet = Packet(ack.data)
                ack_packet.seqnr = ack.seqnr
                ack_packet.mark_packet("ack")
                self.network_layer.send(ack_packet)
                self.expected_ack += 1
            elif ack.seqnr < self.expected_ack:
                self.debugger("Acknowledging older packet \n")
            else:
                self.debugger(f"Received future data packet: {ack.seqnr} \n")

    




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
        self.timer = Timer(self.timeout, callback, *args)
        self.timer.start()


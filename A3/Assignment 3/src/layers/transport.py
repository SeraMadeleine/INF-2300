from copy import copy
from threading import Timer
from config import * 

from packet import Packet


class TransportLayer:
    """
    The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """


    def __init__(self):
        self.timer = None
        self.timeout = 0.4              # Timeout for retransmission in seconds
        self.window_size = WINDOW_SIZE  # Number of packets that can be in flight simultaneously
        self.packets_window = []        # Buffer for sending packets
        self.window_start = 0           # Start positions within the list of packets
        self.window_end = 0             # End positions within the list of packets
        self.seqnr = 0                  # Sequence number, increm for all pacets 
        self.expected_ack = 0           # The expected acknowledgment sequence number
        self.expected_seqnr = 0         # Start with sequence number 0 for the first packet
        self.buffered_packets = {}  # Buffer for unacknowledged packets
        self.base = 0  # The base sequence number for the current window



    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer


    # Sending packets 
    def from_app(self, binary_data):
        if len(self.packets_window) <= self.window_size and self.seqnr <= PACKET_NUM: 
            # Create a packet with the binary data and assign a sequence number.
            packet = Packet(binary_data)

            # Set seqnr for packet and self
            packet.seqnr = self.seqnr 
            self.seqnr += 1

            # Append the packet to the window 
            self.packets_window.append(packet)
            self.logger.debug(self.packets_window)

            self.network_layer.send(packet)

            # Start the timer if it is not already running
            
            if self.base == packet.seqnr:
                self.reset_timer(self.retransmit_packets)
        else: 
            self.logger.debug("Window is full. Waiting for ACKs.")
            pass

    # Reciving acknowledgments
    def from_network(self, packet):
        # self.logger.debug(f"")
        self.logger.debug(self.packets_window)
        self.application_layer.receive_from_transport(packet.data)
        # Implement me!

        
        # Check if the received packet is an acknowledgment (ACK). Then Alice is the one reading 
        if packet.payload_type == "ack":
            ack_seqnr = packet.seqnr 

            if ack_seqnr >= self.base and ack_seqnr <= PACKET_NUM: 
                self.logger.debug(f"Received ACK for packet {ack_seqnr}.")
                self.packets_window = self.packets_window[ack_seqnr - self.base + 1:]
                self.base = ack_seqnr + 1
                # Reset the timer if there are more unacknowledged packets
                if self.base < self.seqnr:
                    self.reset_timer(self.retransmit_packets)
                
                # # Remove all acknowledges packets from the window and update 
                # while self.window_end < len(self.packets_window): 
                #     self.packets_window = self.packets_window[ack_seqnr - self.base + 1:]
                #     self.base = ack_seqnr + 1
                #     self.network_layer.send(self.packets_window[self.window_end])
                #     self.window_end += 1
                
        # Handle out-of-order acknowledgments and potential future ACKs

        # Check if the received packet is a data packet, if it is a packet bob is the nes to do something. 
        elif packet.payload_type == "data": 
            if packet.seqnr == self.expected_seqnr:
                # Handle data packets (e.g., check for corruption, order, and send ACK)
                # Add code here to check for packet integrity and order and send ACKs.
                ack_packet = Packet(packet.data)
                ack_packet.seqnr = packet.seqnr
                ack_packet.mark_packet("ack")
                self.network_layer.send(ack_packet)
                self.expected_seqnr += 1
                self.expected_ack += 1

            elif packet.seqnr < self.expected_seqnr:
                print("\nAcknowledging older packet\n")

            else:
                print(f"\n  else data, expected: {self.expected_seqnr} packet: {packet.seqnr}\n ")
                # This is a future packet; you may choose to handle it accordingly, e.g., buffering, requesting retransmission, etc.
            

    def retransmit_packets(self):
        for packet in self.packets_window:
            self.logger.debug(f"Retransmitting packet {packet.seqnr}.")
            self.network_layer.send(packet)
        self.reset_timer(self.retransmit_packets)

    # def retransmit_packets(self, packet):
    #     for packet in self.packets_window: 
    #         self.logger.debug(f"Retransmitting packet {packet.seqnr}.")
    #         self.network_layer.send(packet)
    #         packet.increment_retry_count()
    #         self.reset_timer(self.retransmit_packets)
    #     pass 


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



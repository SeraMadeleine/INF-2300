from copy import copy
from threading import Timer

from packet import Packet


class TransportLayer:
    """
    The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """


    def __init__(self):
        self.timer = None
        self.timeout = 0.4              # Seconds
        self.window_size = 4            # Number of packets that can be in flight simultaneously
        self.packets_window = []        # Buffer for sending packets
        self.window_start = 0           # Start positions within the list of packets
        self.window_end = 0             # End positions within the list of packets
        self.seqnr = 0                  # Sequence number, increm for all pacets 


    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer


    def from_app(self, binary_data):
        # Create a packet with the binary data and assign a sequence number.
        packet = Packet(binary_data)

        # sette seqnr 
        packet.seqnr = self.seqnr 
        self.seqnr += 1


        # Implement me!
        self.packets_window.append(packet)
        # self.logger.debug(self.packets_window)

        # self.reset_timer()

        # sette sequensnum 
        # sette checksum (ikke viktig i førsteomgang)
        # legg inn i window (buffer)
        # start timer 


        self.network_layer.send(packet)

    def from_network(self, packet):
        # self.logger.debug(f"")
        self.logger.debug(self.packets_window)
        self.application_layer.receive_from_transport(packet.data)
        # Implement me!
        # størst 

        # har packeten en AKK - da har bob sendt pacet til alice 

        # Må sjekke alle punktene, ikke korrupt etc 
        # Bob har egen transport layer, så annet seq num 

        # self.logger.debug(f"")



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



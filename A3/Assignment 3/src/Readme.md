# Simulation Program Readme

This readme provides instructions on how to run the Reliable Transport Protocol simulation for INF-2300 Assignment 3, located in the `src` folder. In this simulation, a reliable data transfer protocol is implemented in the transport layer of the OSI stack. The program allows you to simulate a system with drop, corrupt, and delay channels.

## Running the Program

To run the simulation program, follow these steps:

1. **Locate the `simulation.py` File**: First, navigate to the `src` folder of this project.

2. **Run the Program**: Open your terminal and run the following command:

   ```shell
   python3 simulation.py
   ```

The simulation will execute, and you will observe the reliable data transfer process


## Default Settings

By default, the program has the following settings:

- **Drop, Corrupt, and Delay Channels**: The chance of a packet being dropped, corrupted, or delayed is set to 0.7. This means that there is a 70% chance of any of these events happening. These values can be modified in the config.py file if needed.

- **Debug Mode**:  Debug mode is set to False by default. This means that minimal printing will occur during the simulation to avoid excessive output. If you want to enable debug mode for more detailed information, you can modify this setting in the transport.py file.





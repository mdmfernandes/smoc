#!/usr/bin/python

import sys
import socket
import os
import os.path
import time

# debug (prints a lot of stuff)
debug = True

# read from Cadence
data = sys.stdin.readline()	# Connection stabilished
data = data.replace('\n', '') # remove the \n

# send data back to Cadence to check that is connected
sys.stderr.write(data)
sys.stderr.flush()# flush

# Open UNIX socktet to talk to the client
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    os.remove("/tmp/pythcad_socket")
except OSError:
    pass

# Start to listen
s.bind("/tmp/pythcad_socket")
s.listen(1)

if debug == True:
    time.sleep(1)
    sys.stderr.write('Server started to listening...')
    sys.stderr.flush()# flush

# Waits for client connection
conn, addr = s.accept()

if debug == True:
    sys.stderr.write('Client is connected!')
    sys.stderr.flush()# flush
    #time.sleep(2)


while True:
    # waits for datagram from python client
    dataClient = conn.recv(1024)

    if dataClient.upper() == "DONE":  # end connection
        break
    
    # sends the datagram to Cadence
    sys.stdout.write(dataClient)
    sys.stdout.flush()  # flush

    # waits for response from Cadence
    dataCadence = sys.stdin.readline()
    dataCadence = dataCadence.replace('\n', '') # remove the \n

    if debug == True: # sends confirmation to cadence
        #time.sleep(2)
        sys.stderr.write('Data sent to client: %s' % dataCadence)  # stdout for Cadence Virtuoso
        sys.stderr.flush()  # flush
        
    # sends Cadence response to the client
    conn.sendall(dataCadence)

# send error to SKILL (just because)
# sys.stderr.write('error cenas %s' % data)
# sys.stderr.flush()# flush
# sys.stderr.close()# close stdout

s.close()  # close connection with python client
os.remove("/tmp/pythcad_socket")

# Send feedback to Cadence
sys.stderr.write("Connection with client ended!")
sys.stderr.flush()  # flush
sys.stdout.close()  # close stdout
sys.stderr.close()  # close stderr
sys.exit(255) # close connection to cadence (code up to 255)


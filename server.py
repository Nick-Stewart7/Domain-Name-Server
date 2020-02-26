#! /usr/bin/env python3
# Nicholas Stewart
# ID: 31512469
# Section: 008
import sys
import socket
import struct

# Read server IP address and port from command-line arguments
serverIP = sys.argv[1]    # own IP
serverPort = int(sys.argv[2])    # own port

# Create a UDP socket. Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Assign server IP address and port number to socket
serverSocket.bind((serverIP, serverPort))

print("The server is ready to receive on port:  " + str(serverPort) + "\n")

# open file and add information to a map
dnsMaster = open("dns-master.txt", "r")
dnsList = dnsMaster.readlines()
dnsList = dnsList[5:]

dns = {}
for aRecord in dnsList:
    aRecord = str(aRecord)
    aRecord = aRecord.strip('\n')
    temp = aRecord.split(" A IN ")
    hostName = temp[0] + " A IN"
    dns[hostName] = aRecord

# loop forever listening for incoming UDP messages
while True:
    # Receive and print the client data from "data" socket
    # 1024 is max data length
    data, address = serverSocket.recvfrom(1024)
    print("Message received")
    # unpack the packet
    size = struct.calcsize("!HHIHH")
    preUnpack = struct.unpack("!HHIHH", data[:size])
    Qlength = preUnpack[3]
    info = struct.unpack("!HHIHH%ds" % Qlength, data)
    msgID = info[2]
    name = info[5].decode('utf-8')

    if name in dns:
        # Return answer
        ans = dns[name]

        name = bytes(name, "utf-8")
        ans = bytes(ans, "utf-8")
        Alength = len(ans)
        print("Responded to question with an A Record")
        data = struct.pack("!HHIHH%ds%ds" % (Qlength, Alength), 2, 0, msgID, Qlength, Alength, name, ans)
        serverSocket.sendto(data, address)
    else:
        # repack w/ error
        name = bytes(name, "utf-8")
        ans = bytes('', 'utf-8')
        Alength = len(ans)
        print("Host Name not found. Responding with an error")
        data = struct.pack("!HHIHH%ds%ds" % (Qlength, Alength), 2, 1, msgID, Qlength, Alength, name, ans)
        serverSocket.sendto(data, address)
    # Echo back to client

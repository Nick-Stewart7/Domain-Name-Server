#! /usr/bin/env python3
# Nicholas Stewart
# ID: 31512469
# Section: 008
import sys
import socket
import struct
import random

# Get the server hostname, port and data length as command line arguments
host = sys.argv[1] # dest IP
port = int(sys.argv[2]) # dest port
hostName = sys.argv[3]

# Create UDP client socket. Note the use of SOCK_DGRAM
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set timeout
clientSocket.settimeout(1)

# Set counters
timeoutCount = 0
packetSent = 0
messageCount = 1

# Set RTT list
allRTT = []

# Set data values
question = hostName + " A IN"
question = bytes(question, 'utf-8')
Qlength = len(question)

# Ping
while timeoutCount < 3:
    messageCount = random.randrange(1, 101)
    data = struct.pack("!HHIHH%ds" % Qlength, 1, 0, messageCount, Qlength, 0, question)

    try:
        # Send data to server
        print("Sending Request to " + host + ", " + str(port) + ": ")
        print("Message ID: " + str(messageCount))
        print("Question Length: " + str(Qlength) + " bytes")
        print("Answer Length: 0 bytes")
        print("Question: " + question.decode("utf-8"))
        print("")

        clientSocket.sendto(data, (host, port))
        packetSent += 1

        # Receive the server response
        dataEcho, address = clientSocket.recvfrom(1024)

        size = struct.calcsize("!HHIHH%ds" % Qlength)
        preUnpack = struct.unpack("!HHIHH%ds" % Qlength, dataEcho[:size])
        Alength = preUnpack[4]
        info = struct.unpack("!HHIHH%ds%ds" % (Qlength, Alength), dataEcho)

        ans = info[6].decode('utf-8')
        if info[1] == 0:
            retCode = "0 (No errors)"
        else:
            retCode = "1 (Name does not exist)"

        print("Received Response from " + host + ", " + str(port) + ": ")
        print("Return Code: " + retCode)
        print("Message ID: " + str(info[2]))
        print("Question Length: " + str(info[3]) + " bytes")
        print("Answer Length: " + str(Alength) + " bytes")
        print("Question: " + question.decode("utf-8"))
        print("Answer: " + ans)

        break
    except socket.timeout as timeoutERR:
        print(str(timeoutERR))
        timeoutCount += 1
        continue

if timeoutCount == 3:
    print("Cannot reach host at: " + host + ", " + str(port))

# Close the client socket
clientSocket.close()

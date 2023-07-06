from email.mime import message
from http import server
from msilib import sequence
import socket
import pickle
import sys
import random

class Packet():

    def __init__(self,sequence_number,valid,ack_or_nak,length,message):
        self.sequence_number = sequence_number
        self.message = message
        self.valid = valid
        self.ack_or_nak = ack_or_nak
        self.length = length

    def get_message(self):
        return self.message

    def get_valid(self):
        return self.valid

    def get_length(self):
        return self.length

    def get_ack_or_nak(self):
        return self.ack_or_nak

def main():
    port = int(sys.argv[1])
    host = socket.gethostname()
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host,port))

    max_seg = int(sys.argv[2])
    corrupt_prob = float(sys.argv[3])

    line = input("Enter Input: ")

    for i in range(0, len(line), max_seg):
        if random.random() >= corrupt_prob:
            clientSocket.send(pickle.dumps(Packet(i,True,2,max_seg,line[i:i+max_seg])))
        else:
            clientSocket.send(pickle.dumps(Packet(i,False,2,max_seg,line[i:i+max_seg])))
        ack = False
        while not ack:
            try:
                ob = pickle.loads(clientSocket.recv(1024))
                if ob.get_valid() is False:
                    clientSocket.send(pickle.dumps(Packet(i,True,2,max_seg,line[i:i+max_seg])))
                elif ob.get_valid() is True:
                    ack = True    
            except socket.timeout:
                    print("Timeout")

    messagecomp = ""

    while True:
        data = clientSocket.recv(1024)
        ob = pickle.loads(data)
        if ob.get_valid() is True:
            messagecomp += str(ob.get_message())
            clientSocket.send(pickle.dumps(Packet(0,True,1,0,"")))
        elif ob.get_valid() is False:
            clientSocket.send(pickle.dumps(Packet(0,False,0,0,"")))
        
        if "." in ob.get_message():
            break
        if "?" in ob.get_message():
            break
        if "!" in ob.get_message():
            break

    print(messagecomp)
            
if __name__ == "__main__":
    main()


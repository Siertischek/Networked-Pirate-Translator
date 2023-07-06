from http import server
from msilib import sequence
import socket
import pickle
from string import punctuation
import sys
import csv
import string
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
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host,port))

    max_seg = int(sys.argv[2])
    corrupt_prob = float(sys.argv[3])

    print("Server is listening")

    serverSocket.listen(1)

    messagecomp = ""
    punc = ""
    connection,addr = serverSocket.accept()

    while True:
        data = connection.recv(1024)
        ob = pickle.loads(data)
        if ob.get_valid() is True:
            messagecomp += str(ob.get_message())
            connection.send(pickle.dumps(Packet(0,True,1,0,"")))
        elif ob.get_valid() is False:
            connection.send(pickle.dumps(Packet(0,False,0,0,"")))
        
        if "." in ob.get_message():
            punc = "."
            break
        if "?" in ob.get_message():
            punc = "?"
            break
        if "!" in ob.get_message():
            punc = "!"
            break

    messagecomp = messagecomp.strip(string.punctuation)
    messagecomp += " "
    with open('pirate.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            messagecomp = messagecomp.replace(row[0],row[1])
            line_count+=1

    messagecomp += punc

    for i in range(0, len(messagecomp), max_seg):
        if random.random() >= corrupt_prob:
            connection.send(pickle.dumps(Packet(i,True,2,max_seg,messagecomp[i:i+max_seg])))
        else:
            connection.send(pickle.dumps(Packet(i,False,2,max_seg,messagecomp[i:i+max_seg])))
        ack = False
        while not ack:
            try:
                ob = pickle.loads(connection.recv(1024))
                if ob.get_valid() is False:
                    connection.send(pickle.dumps(Packet(i,True,2,max_seg,messagecomp[i:i+max_seg])))
                elif ob.get_valid() is True:
                    ack = True    
            except socket.timeout:
                    print("Timeout")

if __name__ == "__main__":
    main()
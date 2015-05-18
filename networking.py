import sys, getopt
import socket
import threading
import queue
import select
import json
import time

class Receive_Connection(threading.Thread):
  def __init__(self, gameManager):
    threading.Thread.__init__(self)
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.gameManager = gameManager
  
  def run(self):
    self.socket.bind((self.gameManager.localHost, self.gameManager.localPort))
    self.socket.listen(10)
    
    while True:
      connection, address = self.socket.accept()
      buf = connection.recv(1026)
      response = json.loads(buf.decode("UTF-8"))
      print("R2" + str(response))
      if response["type"] == "connection_request":
        print ("Received connection request")
        for other_peer in response["peers"]: # connect to everyone he is already connected to
          s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s1.connect((other_peer[0],other_peer[1]))
          s1.send(bytes(json.dumps({"type": "connection_finish", "peers" : [], "me" : (self.gameManager.localHost,self.gameManager.localPort)}), 'UTF-8'))
          buf = s1.recv(1024)
          self.gameManager.connected_peers.append(s1)
        connection.sendall(bytes(json.dumps({"type": "connection_response", "peers" : self.gameManager.connection_ports}), 'UTF-8'))
        self.gameManager.connected_peers.append(connection)
        self.gameManager.connection_ports.extend(response["peers"])
        self.gameManager.connection_ports.append(response["me"])
      elif response["type"] == "connection_finish":
        print ("Received connection finish")
        for other_peer in response["peers"]: # connect to everyone he is already connected to
          s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s1.connect((other_peer[0],other_peer[1]))
          s1.send(bytes(json.dumps({"type": "connection_request", "peers" : [], "me" : (self.gameManager.localHost,self.gameManager.localPort)}), 'UTF-8'))
          buf = s1.recv(1024)
          self.gameManager.connected_peers.append(s1)
        connection.sendall(bytes(json.dumps({"type": "connection_response", "peers" : connection_ports}), 'UTF-8'))
        self.gameManager.connected_peers.append(connection)
        self.gameManager.connection_ports.extend(response["peers"])
        self.gameManager.connection_ports.append(response["me"])
      else:
        print("Receive Connection Error.  Received invalid request to port listening for requests")
        print(response)
      
class GameManager():
  def __init__(self):
    self.localPort = 8000
    self.localHost = "localhost" # change to "" to run over outside network
    self.connected_peers = []
    self.connection_ports = []

  def main(self, c):
    
    t2 = Receive_Connection(self)
    t2.start()
    
    t3 = threading.Thread(target=self.receive_message,args=(c,))
    t3.start()
    
    t2.join()
    t3.join()
    
    
  #sends broadcast to all connected peers.  Assumes input can be converted into json (like a dict)
  def broadcast(self, message):
    m = bytes(json.dumps(message), 'UTF-8')
    
    for peer in self.connected_peers:
      peer.send(m)
      
  def receive_message(self, handler):
    while True:
      if (not any(self.connected_peers)):
        time.sleep(1)
        continue
      try: 
        inputready, outputready, exceptready = select.select(self.connected_peers, [], [], 1)
      except select.error as err:
        print("SELECT error: {0}".format(err))
        break
      except socket.error as err:
        print("SELECT error: {0}".format(err))
        break
      for s in inputready:
        try:
          buf = s.recv(1024)
          s = buf.decode("UTF-8")
          #this hack exists because we could get multiple json objects at the same time and need to parse them all separately.  We really should use some kind of message bundler and if this needs to happen use a regex to parse it faster (though at least this still operates in linear time)
          l = []
          c = 0
          s1 = ""
          for i in s:
            s1 += i
            if i == "{" or i == "(":
              c += 1
            elif i == "}" or i == ")":
              c -= 1
              if c == 0:
                l.append(s1)
                s1 = ""
                
          for s in l:
            m = json.loads(s)
            threading.Thread(target=handler.dispatch,args=(m,)).start()
        except:
          print("Unexpected error")
        
    print("Receiver Stopped")
    
  def parseArgs(self, argv):
    try:
      opts, args = getopt.getopt(argv,"p:",["port="])
    except getopt.GetoptError:
      print ('test.py -p <port>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py -p <port>')
         sys.exit()
      elif opt in ("-p", "--port"):
        try:
          self.localPort = int(arg)
        except ValueError:
          print ("Port must be an integer")
          sys.exit()

  def send_connection_request(self):
    opponent_port = input("opponent port: ")
    opponent_ip = input("opponent ip: ")
    try: 
      opponent_port = int(opponent_port)
    except:
      print("Opponent port must be an integer")
      return self.send_connection_request()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((opponent_ip, opponent_port))
    s.send(bytes(json.dumps({"type": "connection_request", "peers" : self.connection_ports, "me" : (self.localHost,self.localPort)}), 'UTF-8'))
    buf = s.recv(1024)
    response = json.loads(buf.decode("UTF-8"))
    print("R1" + str(response))
    if response["type"] == "connection_response":
      for other_peer in response["peers"]:
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((other_peer[0],other_peer[1]))
        s1.send(bytes(json.dumps({"type": "connection_finish", "peers" : connection_ports, "me" : (localHost,localPort)}), 'UTF-8'))
        buf = s1.recv(1024)
        self.connected_peers.append(s1)
        #ignore the response of the others (we don't really care what they have to say)
      self.connected_peers.append(s)
      self.connection_ports.append((opponent_ip,opponent_port))
      self.connection_ports.extend(response["peers"])
    else:
      print("Send Connection Error")
      print(response)
     
     
    
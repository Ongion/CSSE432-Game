import sys, getopt
import socket
import threading
import queue
import select
import json
import time

localPort = 8000
connected_peers = []
connection_ports = []

#sends broadcast to all connected peers.  Assumes input can be converted into json (like a dict)
def broadcast(message):
  m = bytes(json.dumps(message), 'UTF-8')
  for peer in connected_peers:
    peer.send(m)
    
def receive_message():
  while True:
    if (not any(connected_peers)):
      time.sleep(1)
      continue
    try: 
      inputready, outputready, exceptready = select.select(connected_peers, [], [], 1)
    except select.error as err:
      print("SELECT error: {0}".format(err))
      break
    except socket.error as err:
      print("SELECT error: {0}".format(err))
      break
    
    for s in inputready:
      d = s.recv(1024)
      print(d)
  print("Receiver Stopped")
  
def parseArgs(argv):
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
        global localPort
        localPort = int(arg)
      except ValueError:
        print ("Port must be an integer")
        sys.exit()
  print (localPort)

def send_connection_request():
  opponent_port = input("opponent port: ")
  opponent_ip = input("opponent ip: ")
  try: 
    opponent_port = int(opponent_port)
  except:
    print("Opponent port must be an integer")
    return send_connection_request()
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((opponent_ip, opponent_port))
  s.send(bytes(json.dumps({"type": "connection_request", "peers" : connection_ports, "me" : (localHost,localPort)}), 'UTF-8'))
  buf = s.recv(1024)
  response = json.loads(buf.decode("UTF-8"))
  print("R1" + str(response))
  if response["type"] == "connection_response":
    for other_peer in response["peers"]:
      s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s1.connect((other_peer[0],other_peer[1]))
      s1.send(bytes(json.dumps({"type": "connection_finish", "peers" : connection_ports, "me" : (localHost,localPort)}), 'UTF-8'))
      buf = s1.recv(1024)
      connected_peers.append(s1)
      #ignore the response of the others (we don't really care what they have to say)
    connected_peers.append(s)
    connection_ports.append((opponent_ip,opponent_port))
    connection_ports.extend(response["peers"])
  else:
    print("Send Connection Error")
    print(response)
      
class Keyboard_Monitor(threading.Thread):
  def run(self):
    while True:
      print_menu()
      i = input("")
      print("Got command ", i)
      if (i == "1"):
        send_connection_request()
      elif (i == "2"):
        broadcast({"type": "play"})
      else:
        print("Unknown Request")
    
class Receive_Connection(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
  def run(self):
    self.socket.bind(("", localPort))
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
          s1.send(bytes(json.dumps({"type": "connection_finish", "peers" : [], "me" : (localHost,localPort)}), 'UTF-8'))
          buf = s1.recv(1024)
          connected_peers.append(s1)
        connection.sendall(bytes(json.dumps({"type": "connection_response", "peers" : connection_ports}), 'UTF-8'))
        connected_peers.append(connection)
        connection_ports.extend(response["peers"])
        connection_ports.append(response["me"])
      elif response["type"] == "connection_finish":
        print ("Received connection finish")
        for other_peer in response["peers"]: # connect to everyone he is already connected to
          s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s1.connect((other_peer[0],other_peer[1]))
          s1.send(bytes(json.dumps({"type": "connection_request", "peers" : [], "me" : (localHost,localPort)}), 'UTF-8'))
          buf = s1.recv(1024)
          connected_peers.append(s1)
        connection.sendall(bytes(json.dumps({"type": "connection_response", "peers" : connection_ports}), 'UTF-8'))
        connected_peers.append(connection)
        connection_ports.extend(response["peers"])
        connection_ports.append(response["me"])
      else:
        print("Receive Connection Error.  Received invalid request to port listening for requests")
        print(response)
      
def print_menu():
  global connected_peers
  print("You are presently connected to " + str(connection_ports) + " peers")
  print("Press...")
  print("1....Send connection request")
  print("2....Play")
    
if __name__ == "__main__":
  parseArgs(sys.argv[1:])
  
  t1 = Keyboard_Monitor()
  t1.start()
  
  t2 = Receive_Connection()
  t2.start()
  
  t3 = threading.Thread(target=receive_message)
  t3.start()
  
  t1.join()
  t2.join()
  t3.join()
  
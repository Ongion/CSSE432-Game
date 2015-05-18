import math, pygame,sys,pygame.locals
import networking
import threading
import multiprocessing
import time

WIDTH = 900
HEIGHT = 900
FRAME_PERIOD = 1000/60
A_SHIP = 3
V_SHIPTURN = 10
V_LASER = 10
LASER_LENGTH = 10
SHIP_LENGTH = 20
START_CIRCLE_RADIUS = 30
SHIP_ANGLE = math.pi/3
WHITE = (255,255,255)
BLACK = (0,0,0)
GLOBAL_FRAME_RATE = 15


class Keyboard_Monitor(threading.Thread):
  def __init__(self, gameState):
    threading.Thread.__init__(self)
    self.gameState = gameState

  def run(self):
    while True:
      self.gameState.print_menu()
      i = input("")
      print("Got command ", i)
      if (i == "1"):
        self.gameState.gameManager.send_connection_request()
      elif (i == "2"):
        self.gameState.my_time = time.time()
        self.gameState.playRequests.append(self.gameState.my_time)
        time.sleep(0.01)
        self.gameState.gameManager.broadcast({"type": "play","time": self.gameState.my_time})
      else:
        print("Unknown Request")
    

class GameState:

  def __init__(self):
    self.width = WIDTH
    self.height = HEIGHT
    self.ships = []
    self.spriteShips = pygame.sprite.Group()
    self.spriteLasers = pygame.sprite.Group()
    self.playRequests = []
    #we won't know our number until a play transaction has transpired
    self.id = None
    
    #set up the game manager that does all of the threads for sending and receiving messages
    self.gameManager = networking.GameManager()
    self.gameManager.parseArgs(sys.argv[1:])
    t = threading.Thread(target=self.gameManager.main,args=(self,))
    t.start()
    
    #set up the keyboard monitor that listens for requests
    self.keyboardM = Keyboard_Monitor(self)
    self.keyboardM.start()
    
    self.update_count = 0
    print("Here")
    
  def print_menu(self):
    print("You are presently connected to " + str(self.gameManager.connection_ports) + " peers")
    print("Press...")
    print("1....Send connection request")
    print("2....Play")
    
  def run(self):
    centerX = self.width/2
    centerY = self.height/2
    numPlayers = len(self.playRequests)
    for i in range(numPlayers):
      # Start all the players out in a circle around the center, facing outwards
      offsetY = START_CIRCLE_RADIUS * math.cos(2 * math.pi * i / numPlayers)
      offsetX = START_CIRCLE_RADIUS * math.sin(2 * math.pi * i / numPlayers)
      self.ships.append(Spaceship(self, self.width/2 + offsetX, centerY + offsetY, 2 * math.pi * i / numPlayers, i))
      self.spriteShips.add(self.ships[i])
    self.lasers = []
  
    pygame.init()
    pygame.key.set_repeat(60,60)
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    screen.fill(BLACK)
    clock= pygame.time.Clock()

    self.spriteShips.draw(screen)
    pygame.display.flip()


    while True:
      for event in pygame.event.get():#30
        if event.type==pygame.locals.QUIT:#31
          pygame.quit()#32
          sys.exit()#33
        if event.type == pygame.KEYDOWN:
          self.calculateMove(event)
      self.update()
      screen.fill(BLACK)
      self.spriteShips.draw(screen)
      self.spriteLasers.draw(screen)
      pygame.display.flip()
      clock.tick(60)
    
  def dispatch(self, m):
    if "type" in m:
      if m["type"] == "play":
        self.playCommand(m)
      elif m["type"] == "shipLocation":
        self.ships[m["id"]].x = m["x"]
        self.ships[m["id"]].y = m["y"]
        self.ships[m["id"]].vX = m["vX"]
        self.ships[m["id"]].vY = m["vY"]
        self.ships[m["id"]].angle = m["angle"]
      elif m["type"] == "laserCreation":
        laser = Laser(self,m["x"],m["y"],m["angle"],m["playerNum"])
        self.spriteLasers.add(laser)
        self.lasers.append(laser)
      else:
        print("Message Type Unsupported " + str(m["type"]))
    else:
      print("Invalid message: no given type "+ str(m))
    
  def playCommand(self, m):
    if self.playRequests:
      self.playRequests.append(m["time"])
    else:
      self.my_time = time.time()
      self.playRequests.append(m["time"])
      self.playRequests.append(self.my_time)
      self.gameManager.broadcast({"type": "play","time": self.my_time})
      
    print(self.playRequests)
    
    #we should have a play request from everyone and one from ourselves
    if len(self.playRequests) == len(self.gameManager.connection_ports) + 1:
      #theoretically, they would be ordered, but we have no guarantees...unless we sort it
      self.playRequests.sort()
      self.id = self.playRequests.index(self.my_time)
      #we are no longer listening for commands from our keyboard for setting up connections/sending requests
      time_to_wait = 3 - (time.time() - self.playRequests[-1])
      print(time_to_wait)
      time.sleep(time_to_wait)
      self.run()
      
  def update(self):
    for ship in self.ships:
      ship.update()
    for laser in self.lasers:
      laser.update()
    self.collision()
    # Now, remove the lasers that are offscreen!
    self.lasers = [laser for laser in self.lasers if not laser.isOffScreen()]
    
    #only send updates to your friends every GLOBAL_FRAME_RATE times
    self.update_count += 1
    if self.update_count >= GLOBAL_FRAME_RATE:
      self.update_count = 0
      #print("broadcasting location")
      self.gameManager.broadcast({"type": "shipLocation","id":self.id,"x":self.ships[self.id].x,"y":self.ships[self.id].y,"angle":self.ships[self.id].angle,"vX":self.ships[self.id].vX,"vY":self.ships[self.id].vY})
      time.sleep(0.1)
    
  def calculateMove(self,event):
    rotate = accel = 0
    if event.key == 276: #LEFT
      rotate = -.01
    elif event.key == 275: #RIGHT
      rotate = .01
    elif event.key == 273: #UP
      accel = .01
    elif event.key == 274:#DOWN
      accel = -.01
    elif event.key == 32:
      laser = Laser(self,game.ships[self.id].rect.centerx,game.ships[self.id].rect.centery,game.ships[self.id].angle,game.ships[self.id].playerNum)
      self.spriteLasers.add(laser)
      self.lasers.append(laser)

    self.ships[self.id].applyInput([rotate,accel])  
    
  def collision(self):
    for laser in self.spriteLasers:

      # See if it hit a block
      hit_list = pygame.sprite.spritecollide(laser, self.spriteShips, False)

      # For each block hit, remove the bullet and add to the score
      for ship in hit_list:
        if(ship.playerNum != laser.playerNum):
          print(ship)
          self.spriteShips.remove(ship)
          

      # Remove the bullet if it flies up off the screen
      if laser.isOffScreen():
        self.spriteLasers.remove(laser)

    
    
class Spaceship(pygame.sprite.Sprite):

  def __init__(self, game, startX, startY, startAngle, playerNum):
    self.game = game
    self.x = startX
    self.y = startY
    self.playerNum = playerNum
    self.angle = startAngle
    self.vX = 0
    self.vY = 0
    
    super().__init__()
    self.original = pygame.Surface((SHIP_LENGTH,SHIP_LENGTH))
    self.rect = self.original.get_rect()
    self.original.set_colorkey(BLACK)
    self.rect.x = self.x
    self.rect.y = self.y
    pygame.draw.polygon(self.original,WHITE,self.points(),0)
    self.image = pygame.transform.rotate(self.original,-self.angle*180/math.pi)

    
  def points(self):
    return ((SHIP_LENGTH/2+math.sqrt(3)/3*SHIP_LENGTH,SHIP_LENGTH/2),
      (SHIP_LENGTH/2+math.sqrt(3)/3*SHIP_LENGTH*math.cos(math.pi-SHIP_ANGLE),SHIP_LENGTH/2+math.sqrt(3)/3*SHIP_LENGTH*math.sin(math.pi-SHIP_ANGLE)),
      (SHIP_LENGTH/2+math.sqrt(3)/3*SHIP_LENGTH*math.cos(math.pi+SHIP_ANGLE),SHIP_LENGTH/2+math.sqrt(3)/3*SHIP_LENGTH*math.sin(math.pi+SHIP_ANGLE)))  
      
      
  def applyInput(self, input):
    self.rotationInput(input[0])
    self.velocityInput(input[1])

  def rotationInput(self, inputX):
    self.angle += inputX * V_SHIPTURN

  def velocityInput(self, inputY):
    self.vX += A_SHIP * inputY * math.cos(self.angle)
    self.vY += A_SHIP * inputY * math.sin(self.angle)

  def update(self):
    self.x += self.vX * FRAME_PERIOD
    self.y += self.vY * FRAME_PERIOD
    self.doScreenWraps()
    self.rect.x = self.x
    self.rect.y = self.y
    self.image = pygame.transform.rotate(self.original,-self.angle*180/math.pi)

  def doScreenWraps(self):
    if self.x < -SHIP_LENGTH:
      self.x += self.game.width + 2 * SHIP_LENGTH
    elif self.x > self.game.width + SHIP_LENGTH:
      self.x -= self.game.width + 2* SHIP_LENGTH 
    if self.y < -SHIP_LENGTH:
      self.y += self.game.height + 2 * SHIP_LENGTH
    elif self.y > self.game.height + SHIP_LENGTH:
      self.y -= self.game.height + 2 * SHIP_LENGTH

class Laser(pygame.sprite.Sprite):
  
  def __init__(self, game, startX, startY, angle, playerNum):
    self.game = game
    self.x = startX
    self.y = startY
    self.angle = angle
    self.playerNum = playerNum
    
    super().__init__()
    self.image = pygame.Surface((LASER_LENGTH,LASER_LENGTH))
    self.rect = self.image.get_rect()
    self.image.set_colorkey(BLACK)
    self.rect.x = self.x
    self.rect.y = self.y
    pygame.draw.line(self.image,WHITE,self.points1(),self.points2(),1)
    
    #if we are the on shooting, we need to tell everybody
    if playerNum == self.game.id:
      self.game.gameManager.broadcast({"type": "laserCreation", "x": self.x, "y": self.y, "angle": self.angle, "playerNum": self.playerNum})
  
  def points1(self):
    return (LASER_LENGTH/2 - LASER_LENGTH/2*math.cos(self.angle),LASER_LENGTH/2-LASER_LENGTH/2*math.sin(self.angle))
  
  def points2(self):
    return (LASER_LENGTH/2 + LASER_LENGTH/2*math.cos(self.angle),LASER_LENGTH/2+LASER_LENGTH/2*math.sin(self.angle))

  def update(self):
    self.x += V_LASER * math.cos(self.angle)
    self.y += V_LASER * math.sin(self.angle)
    self.rect.x = self.x
    self.rect.y = self.y

  def isOffScreen(self):
    xLen = LASER_LENGTH * math.cos(self.angle)
    yLen = LASER_LENGTH * math.sin(self.angle)
    return self.x < -xLen or self.x > game.width + xLen or self.y < -yLen or self.y > game.height + yLen


#Main game
if __name__ == "__main__":
  print(sys.getcheckinterval())
  sys.setcheckinterval(1)
  game = GameState()


import math, pygame,sys,pygame.locals

WIDTH = 900
HEIGHT = 900
FRAME_PERIOD = 1000/60
A_SHIP = 10
V_SHIPTURN = 5
V_LASER = 10
LASER_LENGTH = 10
SHIP_LENGTH = 20
START_CIRCLE_RADIUS = 30
SHIP_ANGLE = math.pi/3
WHITE = (255,255,255)
BLACK = (0,0,0)


class GameState:

	def __init__(self, numPlayers):
		self.numPlayers = numPlayers
		self.width = WIDTH
		self.height = HEIGHT
		self.ships = []
		self.lives = [3 for x in range(numPlayers)]
		self.spriteShips = pygame.sprite.Group()
		centerX = self.width/2
		centerY = self.height/2
		for i in range(numPlayers):
			# Start all the players out in a circle around the center, facing outwards
			offsetY = START_CIRCLE_RADIUS * math.cos(2 * math.pi * i / numPlayers)
			offsetX = START_CIRCLE_RADIUS * math.sin(2 * math.pi * i / numPlayers)
			self.ships.append(Spaceship(self, centerX + offsetX, centerY + offsetY, 2 * math.pi * i / numPlayers, i))
			self.spriteShips.add(self.ships[i])
		self.lasers = []

	def update(self):
		for ship in self.ships:
			ship.update()
		for laser in self.lasers:
			laser.update()
		# APPLY COLLISION DETECTION HERE
		# Now, remove the lasers that are offscreen!
		#self.lasers = [laser for laser in lasers if not laser.isOffScreen()]


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
		self.image = pygame.transform.rotate(self.original,self.angle*180/math.pi)

		
		


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
		self.image = pygame.transform.rotate(self.original,self.angle*180/math.pi)

	def doScreenWraps(self):
		if self.x < -SHIP_LENGTH:
			self.x += self.game.width + 2 * SHIP_LENGTH
		elif self.x > self.game.width + SHIP_LENGTH:
			self.x -= self.game.width + 2* SHIP_LENGTH 
		if self.y < -SHIP_LENGTH:
			self.y += self.game.height + 2 * SHIP_LENGTH
		elif self.y > self.game.height + SHIP_LENGTH:
			self.y -= self.game.height + 2 * SHIP_LENGTH

class Laser:
	
	def __init__(self, game, startX, startY, angle, playerNum):
		self.game = game
		self.x = startX
		self.y = startY
		self.angle = angle
		self.playerNum = playerNum

	def update(self):
		self.x += V_LASER * math.cos(self.angle)
		self.y += V_LASER * math.sin(self.angle)

	def isOffScreen(self):
		xLen = LASER_LENGTH * math.cos(self.angle)
		yLen = LASER_LENGTH * math.sin(self.angle)
		return self.x < -xLen or self.x > game.width + xLen or self.y < -yLen or self.y > game.height + yLen

def calculateMove(event,game):
	rotate = accel = 0
	if event.key == 276: #LEFT
		rotate = .01
	elif event.key == 275: #RIGHT
		rotate = -.01
	elif event.key == 273: #UP
		accel = .01
	elif event.key == 274:#DOWN
		accel = -.01
		
	game.ships[0].applyInput([rotate,accel])	
	
		
#Main game

pygame.init()
pygame.key.set_repeat(60,60)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
screen.fill(BLACK)
game = GameState(3)
clock= pygame.time.Clock()

game.spriteShips.draw(screen)
pygame.display.flip()


while True:
	for event in pygame.event.get():#30
		if event.type==pygame.locals.QUIT:#31
			pygame.quit()#32
			sys.exit()#33
		if event.type == pygame.KEYDOWN:
			calculateMove(event,game)
	game.update()
	screen.fill(BLACK)
	game.spriteShips.draw(screen)
	pygame.display.flip()
	clock.tick(60)
	
	
		









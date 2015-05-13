import math

WIDTH = 900
HEIGHT = 900
FRAME_PERIOD = 1000/60
A_SHIP = 10
V_SHIPTURN = 5
V_LASER = 10
LASER_LENGTH = 10
SHIP_LENGTH = 20
START_CIRCLE_RADIUS = 30

class GameState:

	def __init__(self, numPlayers):
		self.numPlayers = numPlayers
		self.width = WIDTH
		self.height = HEIGHT
		self.ships = []
		self.lives = [3 for x in range(numPlayers)]
		centerX = self.width/2
		centerY = self.height/2
		for i in range(numPlayers):
			# Start all the players out in a circle around the center, facing outwards
			offsetY = START_CIRCLE_RADIUS * math.cos(2 * math.pi * i / numPlayers)
			offsetX = START_CIRCLE_RADIUS * math.sin(2 * math.pi * i / numPlayers)
			self.ships[i] = Spaceship(self, centerX + offsetX, centerY + offsetY, 2 * math.pi * i / numPlayers, i)
		self.lasers = []

	def update(self):
		for ship in self.ships:
			ship.update()
		for laser in self.lasers:
			laser.update()
		# APPLY COLLISION DETECTION HERE
		# Now, remove the lasers that are offscreen!
		self.lasers = [laser for laser in lasers if not laser.isOffScreen()]


class Spaceship:

	def __init__(self, game, startX, startY, startAngle, playerNum):
		self.game = game
		self.x = startX
		self.y = startY
		self.playerNum = playerNum
		self.angle = startAngle
		self.vX = 0
		self.vY = 0

	def applyInput(self, input):
		self.rotationInput(input.x)
		self.velocityInput(input.y)

	def rotationInput(self, inputX):
		self.angle += inputX * V_SHIPTURN

	def velocityInput(self, inputY):
		self.vX += A_SHIP * inputY * math.cos(self.angle)
		self.vY += A_SHIP * inputY * math.sin(self.angle)

	def update(self):
		self.x += self.vX * FRAME_PERIOD
		self.y += self.vY * FRAME_PERIOD
		self.doScreenWraps()

	def doScreenWraps(self):
		if self.x < -SHIP_LENGTH:
			self.x += self.game.width + 2 * SHIP_LENGTH
		elif self.x > self.game.width + SHIP_LENGTH:
			self.x -= self.game.width + 2* SHIP_LENGTH 
		if self.y < -SHIP_LENGTH:
			self.y += self.game.height + 2 * SHIP_LENGTH
		elif self.y > self.game.height + SHIP_LENGTH
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


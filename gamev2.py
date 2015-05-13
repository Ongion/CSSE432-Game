FRAME_PERIOD = 1000/60
A_SHIP = 10
V_SHIPTURN = 5
V_LASER = 10
LASER_LENGTH = 10


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


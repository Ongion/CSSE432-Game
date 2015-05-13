'''
Created on May 9, 2015

@author: schackma
'''
import math
from tkinter import Tk, Canvas, Frame, BOTH

WIDTH = 1000
HEIGHT = 1000
DELAY = 10
SPEED = 10
ASPEED = math.pi/30
LSPEED = 10

class Board(Canvas):
  
    def __init__(self, parent):
        Canvas.__init__(self, width=WIDTH, height=HEIGHT, 
            background="black", highlightthickness=0)
         
        self.parent = parent 
        self.ship = Spaceship(50,50,self.create_line(0,0,0,0))
        self.initUI()
        self.lasers = []
        self.ships = [self.ship,Spaceship(100,50,self.create_line(0,0,0,0))]
        

        self.bind_all("<Key>",self.onKeyPressed)
        self.after(DELAY, self.onTimer)
        self.pack()        
    
    def initUI(self):
        points = [self.ship.x,self.ship.y,
                  self.ship.x-self.ship.length*math.cos(self.ship.angle+self.ship.innerAngle),self.ship.y+self.ship.length*math.sin(self.ship.angle+self.ship.innerAngle),
                  self.ship.x-self.ship.length*math.cos(self.ship.angle-self.ship.innerAngle),self.ship.y+self.ship.length*math.sin(self.ship.angle-self.ship.innerAngle)]
        self.ship.triangle = self.create_polygon(points,outline = 'white',tag='ship')
    
    def moveShip(self):
        oldShips = self.find_withtag("ship");
        z = 0
        while z<len(self.ships):
            if self.ships[z].x <0:
                self.ships[z].x = WIDTH
            
            if self.ships[z].x > WIDTH:
                self.ships[z].x = 0
            
            if self.ships[z].y < 0:
                self.ships[z].y = HEIGHT
            
            if self.ships[z].y > HEIGHT:
                self.ships[z].y = 0
            
            points = [self.ships[z].x,self.ships[z].y,
                  self.ships[z].x-self.ships[z].length*math.cos(self.ships[z].angle+self.ships[z].innerAngle),self.ships[z].y+self.ships[z].length*math.sin(self.ships[z].angle+self.ship.innerAngle),
                  self.ships[z].x-self.ships[z].length*math.cos(self.ships[z].angle-self.ships[z].innerAngle),self.ships[z].y+self.ships[z].length*math.sin(self.ships[z].angle-self.ship.innerAngle)]
    
            self.ships[z].triangle =  self.create_polygon(points,outline = 'white',tag='ship')
            z+=1
        
        for s in oldShips:
            self.delete(s)
            
    
    def onKeyPressed(self, e): 
    
        key = e.keysym

        if key == "Left": 
            self.ship.angle += ASPEED
        

        if key == "Right":
            self.ship.angle += -ASPEED
        

        if key == "Up":
            self.ship.vx += SPEED*math.cos(self.ship.angle)
            self.ship.vy += -SPEED*math.sin(self.ship.angle)
        

        if key == "Down":
            self.ship.vx += -SPEED*math.cos(self.ship.angle)
            self.ship.vy += SPEED*math.sin(self.ship.angle)
        
        if key == "a":
            self.ship.fire = True
    
           
    def createLaser(self,ship):
        Lwidth = 25
        Lhieght = 10
        x = self.create_line(ship.x,ship.y,
                              ship.x+Lhieght*math.cos(ship.angle)+Lwidth*math.cos(ship.angle),ship.y-Lwidth*math.sin(ship.angle)-Lhieght*math.sin(ship.angle),
                              fill = 'white',tag='laser')
        las = Laser(ship.angle,x)
        self.lasers.append(las)
        
        
    def moveLasers(self):
        x = 0
        while x< len(self.lasers):
            self.move(self.lasers[x].drawing,LSPEED*math.cos(self.lasers[x].angle),-LSPEED*math.sin(self.lasers[x].angle))
            
            x = x+1
    
    def checkCollisions(self):
        for l in self.find_withtag("ship"):
            Lc = self.coords(l)
            overlap = self.find_overlapping(Lc[0],Lc[1],Lc[2],Lc[3])
            for over in overlap:
                if self.gettags(over)[0]=='laser':
                    for ship in self.ships:
                        if l == ship.triangle:
                            self.ships.remove(ship)
                            break
                        self.delete(over)
                
                  
        
        
    def onTimer(self):
        self.ship.move()
        self.moveShip()
        self.moveLasers()
        self.checkCollisions()
        
        if self.ship.fire:
            self.ship.fire = False
            self.createLaser(self.ship)
            
        self.after(DELAY, self.onTimer)
        

class Spaceship:
    length = 50
    innerAngle = math.pi/6
    
    def __init__(self,startX,startY,tri):
        self.x = startX
        self.y = startY
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.fire = False
        self.timestep = DELAY/1000
        self.triangle = tri
    
    def addVel(self,x):
        self.vx = self.vx + x*math.cos(self.angle)
        self.vy = self.vy +x*math.sin(self.angle)
    
    def move(self):
        self.x = self.x+self.vx*self.timestep
        self.y = self.y+self.vy*self.timestep
        
    def turn(self,x):
        self.angle = self.angle+x

class Laser:
    
    def __init__(self,angle,draw):
        self.angle = angle
        self.drawing = draw


class game(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
                
        parent.title('Space Wars')
        self.board = Board(parent)
        self.pack()  
        
def main():
  
    root = Tk()
    ex = game(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
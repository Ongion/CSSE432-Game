'''
Created on May 9, 2015

@author: schackma
'''
import math
from tkinter import Tk, Canvas, Frame, BOTH

WIDTH = 1000
HEIGHT = 1000
DELAY = 17
SPEED = 10
ASPEED = math.pi/10
LSPEED = 10

class Board(Canvas):
  
    def __init__(self, parent):
        Canvas.__init__(self, width=WIDTH, height=HEIGHT, 
            background="black", highlightthickness=0)
         
        self.parent = parent 
        self.ship = Spaceship(50,50)
        self.lasers = []
        self.ships = [self.ship,Spaceship(100,50)]
        
        self.bind_all("<Key>",self.onKeyPressed)
        self.after(DELAY, self.onTimer)
        self.pack()        
    
    def updateUI(self):
      self.updateShipUI()
      updateLaserUI(self)
    
    def updateShipUI(self):
        #delete previous ships from the UI
        oldShips = self.find_withtag("ship");
        for s in oldShips:
            self.delete(s)
            
        for s in self.ships:
            self.create_polygon(s.points(),outline = 'white',tag='ship')
    
    def updateLaserUI(self):
        for l in self.lasers:
            self.move(self.lasers[x].drawing,LSPEED*math.cos(self.lasers[x].angle),-LSPEED*math.sin(self.lasers[x].angle))
            
            x = x+1
    
    
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
                              ship.x-Lhieght*math.cos(ship.angle)+Lwidth*math.cos(ship.angle),ship.y-Lwidth*math.sin(ship.angle)-Lhieght*math.sin(ship.angle),
                              fill = 'white',tag='laser')
        las = Laser(ship.angle,x)
        self.lasers.append(las)
        
        
    def checkCollisions(self):
        for l in self.find_withtag("ship"):
            Lc = self.coords(l)
            overlap = self.find_overlapping(Lc[0],Lc[1],Lc[2],Lc[3])
            for over in overlap:
                print(self.gettags(over))
                if self.gettags(over) ==('laser'):
                    print("true")
                    c = self.coords(over)
                    for ship in self.ships:
                        if c[0] == ship.x:
                            self.ships.remove(ship)
                            break
                        self.delete(over)
                
                  
        
        
    def onTimer(self):
        self.ship.move()
        self.updateUI()
        self.moveLasers()
        self.checkCollisions()
        
        if self.ship.fire:
            self.ship.fire = False
            self.createLaser(self.ship)
            
        self.after(DELAY, self.onTimer)
        
class Spaceship:
    length = 50
    innerAngle = math.pi/6
    
    def __init__(self,startX,startY):
        self.x = startX
        self.y = startY
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.fire = False
        self.timestep = DELAY/1000
    
    def addVel(self,x):
        self.vx = self.vx + x*math.cos(self.angle)
        self.vy = self.vy +x*math.sin(self.angle)
    
    def move(self):
        self.x = self.x+self.vx*self.timestep
        self.y = self.y+self.vy*self.timestep
        if self.x <0:
            self.x = WIDTH
        
        if self.x > WIDTH:
            self.x = 0
        
        if self.y < 0:
            self.y = HEIGHT
        
        if self.y > HEIGHT:
            self.y = 0
            
    def points(self):
      return [self.x,self.y,
                  self.x-self.length*math.cos(self.angle+self.innerAngle),self.y+self.length*math.sin(self.angle+self.innerAngle),
                  self.x-self.length*math.cos(self.angle-self.innerAngle),self.y+self.length*math.sin(self.angle-self.innerAngle)]
        
        
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
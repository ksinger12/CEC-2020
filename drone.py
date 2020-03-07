import math

#Drone class
#Needs the grid object passed into on initialization for environment reference
class Drone:    
    def __init__(self, grid, pos):
        self.grid = grid
        
        if (pos != None):
            self.pos = [pos[0], pos[1]]
        else:
            self.pos = [0, 0]
            
        self.time = 0
        
        self.hopper = []
        self.hopperSize = (int)(math.floor(pow(pow(self.grid.getSize(), 3), 0.5)/2))
        self.lastColour = ""
        
        self.memory = []
        #Initializing drone's memory of environment to zero
        for i in range(self.grid.getSize()):
            toAddi = []
            for j in range(self.grid.getSize()):
                toAddj = []
                for k in range(self.grid.getSize()):
                    toAddj.append(None)
                toAddi.append(toAddj)
            self.memory.append(toAddi)
        
    #Moves the drone in a given direction, updates the time taken
    def move(self, direction): #0 is up, 1 is right, 2 is down, 3 is left
        self.time += 1
        if (direction == 0):
            self.pos[1] += 1
        elif (direction == 1):
            self.pos[0] += 1
        elif (direction == 2):
            self.pos[1] += -1
        elif (direction == 3):
            self.pos[0] += -1
        else:
            self.time += -1
    
    #Picks up a block in the environment at the current position, updates time
    def pickUp(self):
        toAdd = self.grid.takeBlock(self.pos[0], self.pos[1]) #(colour, z)
        if (toAdd == None): #if there is an error exit
            return
        if (len(self.hopper) < self.hopperSize): #if there is room in the hopper, pick up block
            self.hopper.append(toAdd[0]) #add to hopper
            
            #Update time
            newColour = toAdd[0]
            if (newColour == self.lastColour):
                self.time += 2
            else:
                self.time += 3
            
            self.lastColour = newColour
            self.memory[self.pos[0]][self.pos[1]][toAdd[1]] = None
    
    #Drops off a block in the environment at the current position at a given z value
    def dropOff(self, colour, z):
        toRemove = None
        inHopper = False
        for i in self.hopper: #block needs to be in hopper to drop off
            if (i == colour):
                toRemove = i
                inHopper = True
                break
        if (inHopper == False): #If the block is not in the hopper
            return
        self.hopper.remove(toRemove) #Remove block from hopper
        
        #Add block to grid and memory
        test = self.grid.addBlock(self.pos[0], self.pos[1], toRemove)
        if (test != None):
            #Update time
            if (colour == self.lastColour):
                self.time += 2
            else:
                self.time += 3
                
            self.lastColour = colour
            self.memory[self.pos[0]][self.pos[1]][z] = toRemove[0]
            
    def scan(self):
        block = self.grid.blockAt(self.pos[0], self.pos[1])
        self.memory[self.pos[0]][self.pos[1]][block[1]] = block[0]
        return block
    
    
                
            
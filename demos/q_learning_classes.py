import pygame as pg
import random

#mouse Crosshair
def mouse(gameDisplay,myfont,disP,active= False):
    if active:
        x,y = pg.mouse.get_pos()
        textsurface = myfont.render('x: '+str(x-30)+' y: '+str(y-30),False,(255,255,255))
        gameDisplay.blit(textsurface,(0,0))
        pg.draw.lines(gameDisplay, (255,255,255), False, ((0,y-10),(disP[0],y-10)))
        pg.draw.lines(gameDisplay, (255,255,255), False, ((x-10,0),(x-10,disP[1])))


#Cells that are to be dead, cannot be moved into returned as False
def layingOutDead(Dimensions,DeadCell):
    for n in DeadCell:
        yield (n[1]-1)*Dimensions[0] + n[0]-1

#EndGameCells PointsGiven : CartesianLocation
def layingOutEnds(Dimensions,EndGame):
    for m,n in EndGame.items():
        if type(n) == list:
            for o in n:
                yield [m,(o[1]-1)*Dimensions[0] + o[0]-1]
        else:
            yield [m,(n[1]-1)*Dimensions[0] + n[0]-1]

def layingOutField(Dimensions,Dead,Ends,defaultReward):

    d = [0] * (Dimensions[0]*Dimensions[1])
    for n in range(len(d)):
        d[n] = [0.00,0.00,0.00,0.00]

    e = [defaultReward] * Dimensions[0]*Dimensions[1]

    for n in Dead:
        d[n] = []
        e[n] = False

    for m,n in Ends:
        d[n] = [0.00]
        e[n] = m

    return d,e

def maxMin(max,min,test):
    if max >= test and min <= test:
        return max,min
    elif max < test:
        return test,min
    else:
        return max,test

def AveOrMax(lst,Average = False):
    if Average:
        return sum(lst) / len(lst)
    else:
        return max(lst)

class Player:
    def __init__(self,gameDisplay,place,grid,count,reward,BlockSize = 70,noise = 0,alpha=0.5,gamma=1):
        self.gameDisplay = gameDisplay
        self.xGrid = grid[0]
        self.yGrid = grid[1]
        self.xPlace = place[0]
        self.yPlace = place[1]
        self.BlockSize = BlockSize
        self.lengthOfGrid = grid[0] * grid[1]
        self.noise = noise
        self.count = count
        self.reward = reward
        self.placed = place
        self.alpha = alpha
        self.gamma = gamma #
        self.prevRew = 0




    def rewFunc(self,Qcurrent,alpha,reward,gamma,Qnext):
        return Qcurrent + alpha*(reward+gamma*Qnext-Qcurrent)

    def rewardCheck(self,rew,historic):
        if rew > historic:
            return rew
        else:
            return historic

    def move(self,dir,maX,miN,hist):
        x,y = self.placed
        hest = self.noise/2
        true = 100-self.noise
        var = ['up','right','down','left','up','right']
        movement = dir
        randCheck = random.randint(0,100)

        def placedVal(x,y):
            return x-1+self.xGrid*(y-1)

        rew = self.reward[placedVal(x,y)]
        lastPos = placedVal(x,y)

        if len(self.count[placedVal(x,y)]) == 1:

            self.count[lastPos][0] = self.rewFunc(self.count[lastPos][0],self.alpha,rew,self.gamma,0)
            maX,miN = maxMin(maX,miN,self.count[lastPos][0])

        elif dir == 'right':
            #0
            if self.placed[0] == self.xGrid or self.reward[placedVal(x,y)+1] == False:
                self.count[lastPos][0] = self.rewFunc(self.count[lastPos][0],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y)]))
            else:
                self.count[lastPos][0] = self.rewFunc(self.count[lastPos][0],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x+1,y)]))
            maX,miN = maxMin(maX,miN,self.count[lastPos][0])

        elif dir == 'left':
            #2
            if self.placed[0] == 1 or self.reward[placedVal(x,y)-1] == False:
                self.count[lastPos][2] = self.rewFunc(self.count[lastPos][2],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y)]))
            else:
                self.count[lastPos][2] = self.rewFunc(self.count[lastPos][2],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x-1,y)]))
            maX,miN = maxMin(maX,miN,self.count[lastPos][2])

        elif dir == 'up':
            #3
            if self.placed[1] == 1 or self.reward[placedVal(x,y)-self.xGrid] == False:
                self.count[lastPos][3] = self.rewFunc(self.count[lastPos][3],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y)]))
            else:
                self.count[lastPos][3] = self.rewFunc(self.count[lastPos][3],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y-1)]))
            maX,miN = maxMin(maX,miN,self.count[lastPos][3])

        elif dir == 'down':
            #1
            if  self.placed[1] == self.yGrid or self.reward[placedVal(x,y)+self.xGrid] == False:
                self.count[lastPos][1] = self.rewFunc(self.count[lastPos][1],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y)]))
            else:
                self.count[lastPos][1] = self.rewFunc(self.count[lastPos][1],self.alpha,rew,self.gamma,AveOrMax(self.count[placedVal(x,y+1)]))
            maX,miN = maxMin(maX,miN,self.count[lastPos][1])



        #this places the randomness in movement
        for n in range(1,len(var)-1):
            if dir == var[n]:
                if hest == 0:
                    movement = dir
                elif randCheck <= true + hest and randCheck > true:
                    movement = var[n-1]
                elif randCheck > true + hest:
                    movement = var[n+1]



        #CONTROLS THE MOVEMENT OF THE PLAYER
        if len(self.count[placedVal(x,y)]) == 1:
            self.placed = self.xPlace, self.yPlace
            self.prevRew = self.reward[placedVal(x,y)]

        elif movement == 'right' and self.placed[0] != self.xGrid and self.reward[placedVal(x,y)+1] != False:
            self.placed = x+1,y

        elif movement == 'left' and self.placed[0] != 1 and self.reward[placedVal(x,y)-1] != False:
            self.placed = x-1,y

        elif movement == 'up' and self.placed[1] != 1 and self.reward[placedVal(x,y)-self.xGrid] != False:
            self.placed = x,y-1

        elif movement == 'down' and self.placed[1] != self.yGrid and self.reward[placedVal(x,y)+self.xGrid] != False:
            self.placed = x,y+1

        hist = self.rewardCheck(self.reward[placedVal(x,y)],hist)

        return maX,miN,hist,self.prevRew



    def painted(self,color):
        bl = self.BlockSize
        pg.draw.circle(self.gameDisplay,color,(20+int(bl/2)+bl*(self.placed[0]-1),20+int(bl/2)+bl*(self.placed[1]-1)),(int(bl/4)-2))

    def brain(self,maX,miN,prevRew,histRew,revRandomness = False):
        def placedVal(x,y):
            return x-1+self.xGrid*(y-1)

        x,y = self.placed
        b = self.count[placedVal(x,y)]
        a = max(b)
        valChoose = []
        for n in range(len(b)):
            if b[n] == a:
                valChoose += [n]

        direction = ['right','down','left','up']

        j = 1 if histRew == 0 else prevRew/histRew*100

        if random.randint(0,100) > j and revRandomness:
            f = direction[random.randint(0,3)]
        else:
            direction = ['right','down','left','up']
            randDir = random.randint(0,len(valChoose)-1)
            f = direction[valChoose[randDir]]

        maX,miN,histRew,prevRew = self.move(f,maX,miN,histRew)

        return  maX,miN,histRew,prevRew





#HERE THE GRID CLASS BEGINS

class Grid:
    def __init__(self,gameDisplay,grid,count,BlockSize = 70):
        self.gameDisplay = gameDisplay
        self.xGrid = grid[0]
        self.yGrid = grid[1]
        self.BlockSize = BlockSize
        self.lengthOfGrid = grid[0] * grid[1]
        self.count = count

    def colorMovement(self,miN,maX,pos,countPos):
        if self.count[countPos][pos] < 0:
            r,g = 1,0
        elif self.count[countPos][pos] > 0:
            r,g = 0,1
        else:
            r,g = 0,0

        if maX != 0 and g == 1:
            return r,g,self.count[countPos][pos]/maX
        elif miN != 0 and r == 1:
            return r,g,self.count[countPos][pos]/miN
        else:
            return r,g,0


    #this will control the values in each cell and type of cell
    def updateGrid(self,maX,miN):
        scoreFont = pg.font.SysFont('Comic Sans Ms',int(self.BlockSize/7.5))
        #this determins with the use of valAndType array
        r,g,s = 0,0,0
        halfB = self.BlockSize/2
        for j in range(self.yGrid):
            for i in range(self.xGrid):
                regCell = len(self.count[i+j*self.xGrid]) == 4
                x,y = 20+self.BlockSize*i,20+self.BlockSize*j
                pg.draw.rect(self.gameDisplay,(255,255,255),(x,y,self.BlockSize+1,self.BlockSize+1),1)
                if regCell:
                    pg.draw.rect(self.gameDisplay,(255,255,255),(x+2+self.BlockSize/4,y+2+self.BlockSize/4,halfB-3,halfB-3),1)
                    pg.draw.polygon(self.gameDisplay,(255,255,255),[(x+halfB,y+3),(x+self.BlockSize-3,y+halfB),(x+halfB,y+self.BlockSize-3),(x+3,y+halfB)],1)


                    #top 3
                    r,g,s = self.colorMovement(miN,maX,3,i+j*self.xGrid)

                    textsurface = scoreFont.render("%.2f" % self.count[i+j*self.xGrid][3],False,(255,255,255))
                    surface1 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface1.set_colorkey((0,0,0))
                    surface1.set_alpha(255*s)
                    pg.draw.polygon(surface1,(255*r,255*g,0),[(4+self.BlockSize/4,1+self.BlockSize/4),(halfB,4),(-3+3*self.BlockSize/4,1+self.BlockSize/4)])

                    self.gameDisplay.blit(surface1, (x,y))
                    self.gameDisplay.blit(textsurface,(x+int(self.BlockSize/2.38),y+int((self.BlockSize)/5.77)))
                    #left 2
                    r,g,s = self.colorMovement(miN,maX,2,i+j*self.xGrid)

                    textsurface = scoreFont.render("%.2f" % self.count[i+j*self.xGrid][2],False,(255,255,255))
                    surface2 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface2.set_colorkey((0,0,0))
                    surface2.set_alpha(255*s)
                    pg.draw.polygon(surface2,(255*r,255*g,0),[(4,self.BlockSize/2),(1+self.BlockSize/4,3+self.BlockSize/4+1),(2+self.BlockSize/4,3*self.BlockSize/4-2)])

                    self.gameDisplay.blit(surface2, (x,y))
                    self.gameDisplay.blit(textsurface,(x+int(self.BlockSize/12.5),y+int((self.BlockSize)/2.17)))
                    #down 1
                    r,g,s = self.colorMovement(miN,maX,1,i+j*self.xGrid)

                    textsurface = scoreFont.render("%.2f" % self.count[i+j*self.xGrid][1],False,(255,255,255))
                    surface3 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface3.set_colorkey((0,0,0))
                    surface3.set_alpha(255*s)
                    pg.draw.polygon(surface3,(255*r,255*g,0,),[(3+self.BlockSize/4,3*self.BlockSize/4-1),(self.BlockSize/2,self.BlockSize-4),(3*self.BlockSize/4-2,3*self.BlockSize/4-1)])

                    self.gameDisplay.blit(surface3, (x,y))
                    self.gameDisplay.blit(textsurface,(x+int(self.BlockSize/2.38),y+int((self.BlockSize)/1.316)))
                    #right 0
                    r,g,s = self.colorMovement(miN,maX,0,i+j*self.xGrid)

                    textsurface = scoreFont.render("%.2f" % self.count[i+j*self.xGrid][0],False,(255,255,255))
                    surface4 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface4.set_colorkey((0,0,0))
                    surface4.set_alpha(255*s)
                    pg.draw.polygon(surface4,(255*r,255*g,0),[(3*self.BlockSize/4-1,3*self.BlockSize/4-2),(self.BlockSize-4,self.BlockSize/2),(3*self.BlockSize/4-1,3+self.BlockSize/4)])

                    self.gameDisplay.blit(surface4, (x,y))
                    self.gameDisplay.blit(textsurface,(x+int(self.BlockSize/1.315),y+int((self.BlockSize)/2.17)))

                elif self.count[i+j*self.xGrid] == []:
                    surface6 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface6.set_colorkey((0,0,0))
                    surface6.set_alpha(100)
                    pg.draw.rect(self.gameDisplay,(255,255,255),(x+5,y+5,self.BlockSize-9,self.BlockSize-9))

                else:
                    r,g,s = self.colorMovement(miN,maX,0,i+j*self.xGrid)

                    textsurface = scoreFont.render("%.2f" % self.count[i+j*self.xGrid][0],False,(255,255,255))
                    surface5 = pg.Surface((self.BlockSize,self.BlockSize))
                    surface5.set_colorkey((0,0,0))
                    surface5.set_alpha(255*s)
                    pg.draw.rect(surface5,(255*r,255*g,0),(1,1,self.BlockSize-1,self.BlockSize-1))

                    self.gameDisplay.blit(surface5, (x,y))
                    pg.draw.rect(self.gameDisplay,(255,255,255),(x+10,y+10,self.BlockSize-19,self.BlockSize-19),1)
                    self.gameDisplay.blit(textsurface,(x+int(self.BlockSize/2.38),y+int((self.BlockSize)/2.17)))

import pygame as pg
import q_learning_classes as box

#values to manipulate
blocks = (8,5)
Start = (1,1)
Dead = []
Ends = {1: (8,5),-1:[(2,2)]}
defaultReward = -0.04

blockSize = 140 #default value is 70
x,y = 0,0
mouse = False
noise = 0 # % VALUE
alpha=0.5
gamma=1



disP = (40+blocks[0]*blockSize,40+blocks[1]*blockSize)



#sets up pygame for us
gameDisplay = pg.display.set_mode((0, 0), pg.FULLSCREEN)
pg.display.set_caption("Reinforcement Learning Game")
clock = pg.time.Clock()
#text setup
pg.font.init()
myfont = pg.font.SysFont('Comic Sans Ms',20)

crashed = False

E = box.layingOutEnds(blocks,Ends)
D = box.layingOutDead(blocks,Dead)
C,R = box.layingOutField(blocks,D,E,defaultReward)

grid = box.Grid(gameDisplay,blocks,C,blockSize)
#player takes the following parameters (gameDisplay to be drawn on),(placement),(the dimensions of the grid),(score of each direction),(reward for state)
#(the Block Size)
player = box.Player(gameDisplay,Start,blocks,C,R,blockSize,noise,alpha,gamma)

maX,miN = 0,0
Comp = False
PlayerColor = (0,0,255)
i = 0
speed = 30
hist = 0
prevRew = 0

while not crashed:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            crashed = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                crashed = True
            if event.key == pg.K_RIGHT:
                if Comp == False:
                    maX,miN,hist,prevRew = player.move('right',maX,miN,hist)
            if event.key == pg.K_LEFT:
                if Comp == False:
                    maX,miN,hist,prevRew = player.move('left',maX,miN,hist)
            if event.key == pg.K_UP:
                if Comp == True:
                    speed -= 1
                else:
                    maX,miN,hist,prevRew = player.move('up',maX,miN,hist)
            if event.key == pg.K_DOWN:
                if Comp == True:
                    speed += 1
                else:
                    maX,miN,hist,prevRew = player.move('down',maX,miN,hist)
            if event.key == pg.K_p:
                if not Comp:
                    Comp = True
                    PlayerColor = (255,0,255)
                else:
                    Comp = False
                    PlayerColor = (0,0,255)
    #and i%speed == 0
    if Comp:
        maX,miN,hist,prevRew = player.brain(maX,miN,prevRew,hist,True)


    gameDisplay.fill((0,0,0))


    grid.updateGrid(maX,miN)
    player.painted(PlayerColor)

    box.mouse(gameDisplay,myfont,disP,mouse)

    pg.display.update()
    i += 1
    clock.tick(30)

pg.quit()

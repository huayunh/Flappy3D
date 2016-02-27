# The original idea of Flappy Bird is from Dong Nguyen's mobile phone game 
# released on May 24, 2013. This is just a fan-made copy by Huayun Huang at
# Carnegie Mellon University for 15-112's term project, and has no intention of
# copyright infringement.

# The codes below, unless cited otherwise, are written entirely by Huayun Huang.
# huayunh, section A, Spring 2015

import eventBasedAnimation,random,math,os
from Tkinter import *
# eventBasedAnimation written by David Kosbie
# http://www.cs.cmu.edu/~112/notes/eventBasedAnimation.py

def get3DRatio(VanishPoint45,distanceToScreen):
    # receiving the vanishing point of an angle at 45 and the distance to screen
    return float(VanishPoint45)/(VanishPoint45+distanceToScreen)

def rgbString(red, green, blue):
    # from course note
    # www.cs.cmu.edu/~112
    return "#%02x%02x%02x" % (red, green, blue)

def drawCircle(canvas,cx,cy,r,color):
    # a quick access to draw circles
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r,width=0,fill=color)

def colorAdjust(ratio,rgb):
    # adjust the RGB value of the color with the ratio
    if ratio<0:ratio=0
    r,g,b=rgb
    maxColor=255
    if (int(r*ratio)>maxColor or 
        int(g*ratio)>maxColor or 
        int(b*ratio)>maxColor):
        return "white"
    else: return rgbString(int(r*ratio),int(g*ratio),int(b*ratio))

def readFile(filename, mode="rt"):
    # from course note: 
    # www.cs.cmu.edu/~112/notes/notes-functions-redux-and-web-and-file-io.html
    with open(filename, mode) as fin:
        return fin.read()

def writeFile(filename, contents, mode="wt"):
    # from course note: 
    # www.cs.cmu.edu/~112/notes/notes-functions-redux-and-web-and-file-io.html
    with open(filename, mode) as fout:
        fout.write(contents)

class Pipe():
    # In my game, the "pipes" are replaced by openings on the wall.
    def __init__(self,w3D,d3D,gap,l3D=600,gapStart=-300,forwardSpeed=25):
        # w3D is half of the actual width since it is systematic to the 
        # vanishing point
        # d3D is the distance to the camera
        # l3D is the thickness of the wall
        self.gapStart=gapStart
        self.w3D=w3D
        self.gap=gap
        self.d3D=d3D
        self.l3D=l3D
        self.gapToNext=3000
        self.downSpeed=-10
        self.forwardSpeed=forwardSpeed

    def get2DPosition(self,VanishPoint45):
        # the coordinate system's origin is at the vanishing point at the center

        # the face at the front
        r=get3DRatio(VanishPoint45,self.d3D)
        w1=r*self.w3D
        h11=r*self.gapStart # front up
        h21=r*(self.gapStart+self.gap) # front down

        # the face at the back
        r=get3DRatio(VanishPoint45,self.d3D+self.l3D)
        w2=r*self.w3D
        h12=r*self.gapStart # back up
        h22=r*(self.gapStart+self.gap) # back down

        return w1,h11,h21,w2,h12,h22

    def drawSideFace(self,canvas,UI):
        # draw all the face at the side 
        x,y=UI.w/2,UI.vp
        w1,h11,h21,w2,h12,h22=self.get2DPosition(UI.VanishPoint45)

        darken=0.8*(1-float(self.d3D)/(self.gapToNext*UI.pipeNum-self.l3D))
        color=colorAdjust(darken,UI.rgb)
        canvas.create_polygon(x-w1,y+h11,x-w1,y+h21,
                              x-w2,y+h22,x-w2,y+h12,
                              fill=color,width=0) # left
        canvas.create_polygon(x+w1,y+h11,x+w1,y+h21,
                              x+w2,y+h22,x+w2,y+h12,
                              fill=color,width=0) # right

        darken=0.7*(1-float(self.d3D)/(self.gapToNext*UI.pipeNum-self.l3D))
        color=colorAdjust(darken,UI.rgb)
        canvas.create_polygon(x-w1,y+h11,x+w1,y+h11,
                              x+w2,y+h12,x-w2,y+h12,
                              fill=color,width=0) # top

        darken=0.9*(1-float(self.d3D)/(self.gapToNext*UI.pipeNum-self.l3D))
        color=colorAdjust(darken,UI.rgb)
        canvas.create_polygon(x-w1,y+h21,x+w1,y+h21,
                              x+w2,y+h22,x-w2,y+h22,
                              fill=color,width=0) # bottom

    def drawWallFace(self,canvas,UI):
        # draw the face that surround the side faces
        x,y=UI.w/2,UI.vp
        w1,h11,h21,w2,h12,h22=self.get2DPosition(UI.VanishPoint45)
        darken=(1-float(self.d3D)/(self.gapToNext*UI.pipeNum-self.l3D))
        color=colorAdjust(darken,UI.rgb)
        canvas.create_rectangle(x-w1-1,0,x+w1+1,y+h11,fill=color,width=0)
        canvas.create_rectangle(x-w1-1,y+h21,x+w1+1,UI.h,fill=color,width=0)
        canvas.create_rectangle(0,0,x-w1,UI.h,fill=color,width=0)
        canvas.create_rectangle(x+w1,0,UI.w,UI.h,fill=color,width=0)

    def draw(self,canvas,UI):
        self.drawSideFace(canvas,UI)
        self.drawWallFace(canvas,UI)

    def draw2D(self,canvas,UI,ratio):
        # draw the pipes in the 2D mode
        x=self.d3D*ratio+UI.offset2Dx
        w=self.l3D*ratio
        gapStart=self.gapStart*ratio+UI.h/2
        gap=self.gap*ratio
        darken=0.7
        color=colorAdjust(darken,UI.rgb)
        canvas.create_rectangle(x,0,x+w,gapStart,fill=color,width=0)
        canvas.create_rectangle(x,gapStart+gap,x+w,UI.h,fill=color,width=0)

    def isCollide(self,bird):
        # check if it collide with this pipe
        if ((self.d3D<=bird.d3D<=self.d3D+self.l3D) and 
            (bird.y3D-bird.r<=self.gapStart or 
             bird.y3D+bird.r>=self.gap+self.gapStart)):
                return True
        else: return False

    def moveForward(self):
        self.d3D-=self.forwardSpeed

class Bird():

    def __init__(self,lightFrame,darkFrame):
        # y3D is the relative position to the vanishing point
        # d3D is the distance to the vamera
        self.r=30
        self.lightFrame=lightFrame
        self.darkFrame=darkFrame
        self.d3D=150
        self.y3D=0

    def draw(self,canvas,UI):
        ratio=get3DRatio(UI.VanishPoint45,self.d3D)
        x,y=UI.w/2,UI.h/2+ratio*self.y3D
        step=int(UI.step/2)

        if UI.isInShadow: 
            period=len(self.lightFrame)
            # when the bird is in the opening with shadow cast on it
            if UI.down: # the bird glides
                image=self.darkFrame[1]
            else: # the bird glides
                period=len(self.darkFrame)
                image=self.darkFrame[step%period]

        else: 
            # when there is no shadow
            period=len(self.lightFrame)
            if UI.down:  # the bird glides
                image=self.lightFrame[1]
            else:
                image=self.lightFrame[step%period]

        canvas.create_image(x,y,image=image)
        
    def draw2D(self,canvas,UI,ratio):
        # draw the bird in the 2D mode
        x=self.d3D*ratio+UI.offset2Dx
        y=UI.vp+(self.y3D)*ratio
        frame=UI.step/5%2
        if frame==0:
            canvas.create_image(x,y,image=UI.images["2Dup"])
        else:
            canvas.create_image(x,y,image=UI.images["2Ddown"])

class Missile():
    # the missile on phase 4 used for hitting targets
    def __init__(self,speedX,speedY,speedD):
        # location and size of the missile
        self.r3D=20
        self.d3D=0
        self.x3D=0
        self.y3D=0
        # the speed vector component in 3D space
        self.speedX=speedX
        self.speedD=speedD
        self.speedY=speedY

    def draw(self,canvas,UI):
        maxColor=255
        greyR,greyG,greyB=(maxColor/2,maxColor/2,maxColor/2)
        r,g,b=UI.rgb
        # distance where the color is grey
        distance=float(UI.pipes[0].gapToNext*UI.pipeNum) 
        clrRatio=self.d3D/distance
        (r,g,b)=((r-greyR)*clrRatio+greyR,
                 (g-greyG)*clrRatio+greyG,
                 (b-greyB)*clrRatio+greyB)
        color=colorAdjust(0.4,(r,g,b))
        ratio=get3DRatio(UI.VanishPoint45,self.d3D)
        cr=self.r3D*ratio
        cx=self.x3D*ratio+UI.w/2
        cy=self.y3D*ratio+UI.vp
        canvas.create_oval(cx-cr,cy-cr,cx+cr,cy+cr,fill=color,width=0)

    def move(self):
        # free fall movement
        self.x3D+=self.speedX
        self.d3D+=self.speedD
        acceleration=0.4
        self.speedY+=acceleration
        self.y3D+=self.speedY

class Target():
    # the target at Phase 3 which player 2 need to shoot at.
    def __init__(self,pipe):
        self.r3D=pipe.gap/6
        # x3D,y3D is cx, cy here
        self.x3D=random.randint(-pipe.w3D+self.r3D,pipe.w3D-self.r3D)
        # relative position to the gapStart of the "pipe"
        self.y3D=self.r3D*1.5 + pipe.gap + pipe.gapStart
        self.downSpeed=10
        self.hitted=False

    def draw(self,canvas,UI):
        # draw the target if it is not hitted yet
        if not self.hitted: 
            nearPipe=UI.pipes[0]
            ratio=get3DRatio(UI.VanishPoint45,nearPipe.d3D)
            cx=self.x3D*ratio+UI.w/2
            cy=self.y3D*ratio+UI.vp
            r1=self.r3D*ratio # outer circle
            lineWidth=r1/3       
            darken=0.8*(1-float(nearPipe.d3D)/
                        (nearPipe.gapToNext*UI.pipeNum-nearPipe.l3D))
            color=colorAdjust(darken,UI.rgb)
            canvas.create_oval(cx-r1,cy-r1,cx+r1,cy+r1,outline=color,
                               width=lineWidth)
            r2=r1/3 #inner circle
            drawCircle(canvas,cx,cy,r2,color)

    def hitInside(self,x,y):
        # x,y is the x3D,y3D and d3D of the missile
        # check when missile hit the "pipe"
        mercyRadius=1.7
        if ((self.x3D-x)**2+(self.y3D-y)**2)**0.5<=self.r3D*mercyRadius:
            self.hitted=True
            return True
        else: return False

class Challenger():
    # challenger birds at phase 6 - reversed mode
    def __init__(self,x,y,rgb,ratio=1):
        self.x=x
        self.y=y
        self.color=colorAdjust(0.7,rgb)
        self.forwardSpeed=3+3*ratio*random.random()
        self.downSpeed=-4
        self.maxDownSpeed=-self.downSpeed
        self.r=20
        self.acceleration=self.maxDownSpeed/10.0

    def draw(self,canvas,up,down,step):
        frame=step/5%2
        if frame==0:
            canvas.create_image(self.x,self.y,image=up)
        else: canvas.create_image(self.x,self.y,image=down)

    def isKilled(self,pipe):
        # check if the bird get squeezed by Executioner...
        if (pipe.left<self.x+self.r and  self.x-self.r<pipe.right and 
            pipe.top>=self.y-self.r and self.y+self.r>=pipe.bottom):
            return True
        # not squeezing, then push the bird up or down unless it dies
        elif pipe.left<self.x<pipe.right and pipe.top>=self.y-self.r:
            self.y=pipe.top+self.r 
        elif pipe.left<self.x<pipe.right and self.y+self.r>=pipe.bottom:
            self.y=pipe.bottom-self.r
        return False

class Executioner():
    # the pipe that squeeze the bird at phase 6
    def __init__(self,width,height):
        w=20
        self.left=width/2-w
        self.right=width/2+w
        self.maxH=100
        self.top=height/2-self.maxH
        self.bottom=height/2+self.maxH
        self.color="light grey"
        self.speed=0
    def draw(self,canvas,height):
        # upper part
        canvas.create_rectangle(self.left,0,self.right,self.top,
                                width=0,fill=self.color)
        # lower part
        canvas.create_rectangle(self.left,self.bottom,self.right,height,
                                width=0,fill=self.color)

class GUI(eventBasedAnimation.Animation):

    class Button():
        # buttons that change current phase
        def __init__(self,x,y,UI,target,image,existPhase):
            self.x=x
            self.y=y
            self.image=image
            self.w=image.width()
            self.h=image.height()
            self.target=target
            self.existPhase=existPhase # phase of which the button exists
            self.getBackImage()

        def getBackImage(self):
            self.backGround=PhotoImage(file="splash!.gif")

        def goTo(self,UI):
            UI.phase=self.target

        def clickInside(self,x,y):
            return (self.x-self.w/2<=x<=self.x+self.w/2 and 
                    self.y-self.h/2<=y<=self.y+self.h/2)

        def draw(self,canvas):
            canvas.create_image(self.x,self.y,image=self.backGround)
            canvas.create_image(self.x,self.y,image=self.image)

    class PauseButton(Button):
        def __init__(self,UI):
            self.size=min(UI.w,UI.h)/30
            margin=10
            self.x=UI.w-self.size-margin
            self.y=margin
            lighten=1.2
            self.color=colorAdjust(lighten,UI.rgb)
            self.existPhase=range(3,7)

        def draw(self,canvas):
            # draw two strips at the upper right
            x,y=self.x,self.y
            stripWidth=self.size/3.0
            canvas.create_rectangle(x,y,x+stripWidth,y+self.size,
                                    width=0,fill=self.color)
            canvas.create_rectangle(x+stripWidth*2,y,x+self.size,y+self.size,
                                    width=0,fill=self.color)

        def clickInside(self,x,y):
            margin=15 # increase the detectable range
            return (self.x-margin<=x<=self.x+self.size+margin and 
                    self.y-margin<=y<=self.y+self.size+margin)

        def goTo(self,UI):
            UI.pause=True

    class ModeButton(Button):
        # Buttons appearing on the mode selection screen (phase2)
        def getBackImage(self):
            # change the background picture
            self.backGround=PhotoImage(file="ModeSelect.gif")

################################################################################
################################ init functions ################################
################################################################################

    def onInit(self):
        self.importImages()
        self.initVariable()

    def initVariable(self):
        # game constants
        self.w, self.h = self.width, self.height
        self.rgb = r,g,b = self.randomColorSelect()
        self.BGColor = rgbString(r,g,b)
        self.vp, self.VanishPoint45 = self.h*0.5, 2*self.w # vanishing point
        self.offset2Dx = self.w/10
        self.windowTitle = "Flappy3D"
        self.sides = random.randint(3,5)

        # game states variables
        self.phase=0
        self.isOver=False
        self.score=0
        self.pause=True
        self.drawInfo=False # decide to draw instructions or not
        self.downSpeed=3
        self.down=True
        self.speedUpStart=None

        # initializing functions
        self.initPipe()
        self.initBird()
        self.initButtons()
        self.init2PlayerMode()
        self.initHighScore()

    def initHighScore(self):
        # initialize the high score by extracting the log from the local file
        self.scoreWritten=False
        self.mode=None
        # get the local high score log. Create one if the file does not exist.
        try:
            scores=readFile("highScore.txt")
        except:
            self.createHighScore()
            scores=readFile("highScore.txt")
        scores=scores.splitlines()
        self.highScore={}
        for line in scores:
            # store the highest score
            self.highScore[int(line[0])]=int(line[2:])

    def createHighScore(self):
        # create an empty log of the highest score
        content="""\
3 0
4 0
5 0
6 0"""
        writeFile("highScore.txt",content)

    def init2PlayerMode(self):
        # initialize the 2 player mode
        self.lifeBar=500
        self.maxLife=float(self.lifeBar)
        cooldownRatio=0.5
        self.totalCooldownTime=(self.pipes[0].gapToNext/
                                self.pipes[0].forwardSpeed)*cooldownRatio
        self.mouseX,self.mouseY=-10,-10
        self.miss=6 # allow the shooter to miss several targets
        self.missile=None
        self.target=Target(self.pipes[0])
        self.cooldown=0

    def initBird(self):
        # initialize bird and challengers
        lightFrame=([self.images["light0"],
                     self.images["light1"],
                     self.images["light2"],
                     self.images["light3"],
                     self.images["light4"],
                     self.images["light5"],
                     self.images["light6"]])
        darkFrame=([self.images["dark0"],
                    self.images["dark1"],
                    self.images["dark2"],
                    self.images["dark3"],
                    self.images["dark4"],
                    self.images["dark5"],
                    self.images["dark6"]])
        self.bird=Bird(lightFrame,darkFrame)
        # check if the bird is "in" an opening
        self.isInShadow=False
        self.challengers=[Challenger(self.w/10,self.h/2,self.rgb)]

    def initPipe(self):
        # initialize all the Pipe and Executioner objects
        initWidth=self.w/2
        initHeight=self.h
        self.pipeNum=3
        self.pipes=[Pipe(initWidth,3000,initHeight)]
        self.executioner=Executioner(self.w,self.h)

    def importAnimation(self):
        # import the instruction animation
        for i in xrange(10): 
            storeName="instr"+str(i)
            fileName="instr"+str(i)+".gif"
            self.images[storeName]=PhotoImage(file=fileName)

        # import the bird animation for 3D mode
        for i in xrange(7):
            storeName="light"+str(i)
            fileName="Light"+str(i)+".gif"
            self.images[storeName]=PhotoImage(file=fileName)
            storeName="dark"+str(i)
            fileName="Dark"+str(i)+".gif"
            self.images[storeName]=PhotoImage(file=fileName)

        # import the animation for 2D modes (phase 5 and phase 6)
        self.images["2Dup"]=PhotoImage(file="2Dup.gif")
        self.images["2Ddown"]=PhotoImage(file="2Ddown.gif")

    def initButtons(self):
        # initialize all the buttons in game
        btnHeight=self.h*6/7
        self.buttons=({"pause":self.PauseButton(self),
                       "start":self.Button(self.w/7*6,btnHeight,self,
                        2,self.images["start"],[0,1]),
                       "help":self.Button(self.w/7*4,btnHeight,self,
                        1,self.images["help"],[0,2]),
                       "back":self.Button(self.w/7,btnHeight,self,
                        0,self.images["back"],[1,2]),
                       "classicMode":self.ModeButton(self.w*0.2,self.h*0.2,self,
                        5,self.images["classicMode"],[2]),
                       "normalMode":self.ModeButton(self.w*0.4,self.h*0.4,self,
                        3,self.images["normalMode"],[2]),
                       "duoMode":self.ModeButton(self.w*0.6,self.h*0.6,self,
                        4,self.images["duoMode"],[2]),
                       "reversedMode":self.ModeButton(self.w*0.8,self.h*0.8,
                        self,6,self.images["reversedMode"],[2])
                       })
        self.inGameBackBtn=self.Button(self.w/7,btnHeight,self,2,
                                       self.images["back"],[3,4,5,7])

    def importImages(self):
        # import static pictures
        self.images={}
        self.images["title"]=PhotoImage(file="title.gif")
        self.images["start"]=PhotoImage(file="StartBtn.gif")
        self.images["help"]=PhotoImage(file="HelpBtn.gif")
        self.images["moji"]=PhotoImage(file="moji.gif")
        self.images["sign"]=PhotoImage(file="Sign.gif")
        self.images["back"]=PhotoImage(file="BackBtn.gif")
        self.importAnimation()
        self.images["classicMode"]=PhotoImage(file="Mode-Classic.gif")
        self.images["normalMode"]=PhotoImage(file="Mode-Normal.gif")
        self.images["duoMode"]=PhotoImage(file="Mode-Duo.gif")
        self.images["reversedMode"]=PhotoImage(file="Mode-Reversed.gif")
        self.images["lose"]=PhotoImage(file="lose.gif")
        self.images["modeSelectBG"]=PhotoImage(file="ModeSelectBackground.gif")

    def randomColorSelect(self):
        # randomly select a new color and return the r,g,b value for self.rgb
        (r,g,b)=(random.randint(100,200),
                 random.randint(100,200),
                 random.randint(100,200))
        minDelta=20
        while (abs(r-g)<minDelta or abs(g-b)<minDelta or abs(b-r)<minDelta):
            (r,g,b)=(random.randint(100,200),
                     random.randint(100,200),
                     random.randint(100,200))
        return r,g,b

    def initMissile(self,x,y):
        speedD=(10**-2)*self.pipes[0].gapToNext
        xAdjust,yAdjust=5,1
        speedX=float(x-self.w/2)/self.VanishPoint45*speedD*xAdjust
        speedY=float(y-self.vp)/self.h*speedD*yAdjust
        self.missile=Missile(speedX,speedY,speedD)

################################################################################
################################ draw functions ################################
################################################################################
    def onDraw(self,canvas):
        if self.phase==0: self.drawPhase0(canvas)
        elif self.phase==1: self.drawPhase1(canvas)
        elif self.phase==2: 
            self.drawPhase2(canvas)
            if self.drawInfo!=False:
                self.drawModeInfo(canvas)
        elif self.phase==3: self.drawPhase3(canvas)
        elif self.phase==4: self.drawPhase4(canvas)
        elif self.phase==5: self.drawPhase5(canvas)
        elif self.phase==6: self.drawPhase6(canvas)
        elif self.phase==7: self.drawPhase7(canvas)

    def drawPhase0(self,canvas):
        # title screen
        canvas.create_rectangle(0,0,self.w,self.h,fill=self.BGColor,width=0)
        color=colorAdjust(0.9,self.rgb)
        drawCircle(canvas,self.w/2,self.h/5*2,self.w/5,color)
        color=colorAdjust(0.6,self.rgb)
        canvas.create_image(self.w/2,self.h/5*2,image=self.images["title"])
        size=str(int(self.h/20))
        cx,cy,r=self.w/8,self.h*3/5,int(size)*1.2
        self.drawInkAnimation(canvas,cx,cy,r)
        canvas.create_text(cx,cy,text="3D",fill=color,font="coda "+size)

        self.buttons["start"].draw(canvas)
        self.buttons["help"].draw(canvas)

    def drawPhase1(self,canvas):
        # helpPage
        canvas.create_rectangle(0,0,self.w,self.h,fill=self.BGColor,width=0)
        signImg=self.images["sign"]
        canvas.create_image(0,signImg.height()/2+20,image=signImg,anchor="w")
        self.drawHelp(canvas)
        self.buttons["back"].draw(canvas)
        self.buttons["start"].draw(canvas)
        self.drawPhase1Animation(canvas)
        size=str(self.h/30)
        color=colorAdjust(0.8,self.rgb)
        canvas.create_text(self.w/2,self.h*0.9,text="press the space bar!",
                           anchor="n",font="coda "+size,fill=color)

    def drawPhase2(self,canvas):
        # mode selection!
        canvas.create_rectangle(0,0,self.w,self.h,fill=self.BGColor,width=0)
        canvas.create_image(self.w,0,image=self.images["modeSelectBG"])
        self.buttons["back"].draw(canvas)
        self.buttons["classicMode"].draw(canvas)
        self.buttons["normalMode"].draw(canvas)
        self.buttons["duoMode"].draw(canvas)
        self.buttons["reversedMode"].draw(canvas)

    def drawPhase3(self,canvas):
        # 1P3D screen! "normal mode"
        self.draw3DBackGround(canvas)
        self.bird.draw(canvas,self)
        self.drawPause(canvas)

    def drawPhase4(self,canvas):
        # 2P3D screen! "duo mode"
        self.draw3DBackGround(canvas)
        if self.target!=None:
            self.target.draw(canvas,self)
        self.bird.draw(canvas,self)
        self.drawLifeBar(canvas)
        self.drawCooldownCircle(canvas)
        if self.missile!=None: 
            self.missile.draw(canvas,self)
        self.drawPause(canvas)

    def drawPhase5(self,canvas):
        # 1P2Dscreen! "classic mode"
        canvas.create_rectangle(0,0,self.w,self.h,fill=self.BGColor,width=0)
        darken=0.7
        color=colorAdjust(darken,self.rgb)
        canvas.create_rectangle(0,0,self.w,self.h/10,fill=color,width=0)
        canvas.create_rectangle(0,self.h*9/10,self.w,self.h,fill=color,width=0)
        self.draw2DModeBackgroundAnimation(canvas)

        ratio=self.w/float(self.pipes[0].gapToNext*len(self.pipes))*2
        for pipe in self.pipes:
            pipe.draw2D(canvas,self,ratio)
        self.drawIntroInGame(canvas)
        self.bird.draw2D(canvas,self,ratio)

        self.drawScore2D(canvas)
        self.drawPause(canvas)

    def drawPhase6(self,canvas):
        # "reversed mode"
        canvas.create_rectangle(0,0,self.w,self.h,fill=self.BGColor,width=0)
        self.drawScoreReversed(canvas)
        self.executioner.draw(canvas,self.h)
        for bird in self.challengers:
            bird.draw(canvas,self.images["2Dup"],self.images["2Ddown"],
                      self.step)
        self.drawPause(canvas)
        
    def drawPhase7(self,canvas):
        # losing screen
        w,h=self.w,self.h
        color=colorAdjust(0.6,self.rgb)
        canvas.create_rectangle(0,0,w,h,fill=color,width=0)
        color=colorAdjust(0.8,self.rgb)
        drawCircle(canvas,w/2,h*0.8,min(w,h)*0.8,color)
        size=str(h/8)
        canvas.create_text(w/2,h/4,text="Your score is",font="coda "+size,
                           fill=self.BGColor)
        size=str(h/5)
        color=colorAdjust(0.5,self.rgb)
        canvas.create_text(w/2,h/2,text=str(self.score),font="coda "+size,
                           fill=color)
        canvas.create_image(w/2,h/4*3,image=self.images["lose"])
        text="History highest: "+str(self.highScore[self.mode])
        size=str(h/20)
        color=colorAdjust(0.7,self.rgb)
        canvas.create_text(w/2,h/7,text=text,fill=color,font="coda "+size)
        self.inGameBackBtn.draw(canvas)

    def drawHelp(self,canvas):
        # draw the help text in phase 1
        font,margin,color="coda "+str(20),55,colorAdjust(0.5,self.rgb)
        left="""\
These birds love flying, \n however they will be 
knocked out once they \n bumped into the wall. 
Your job is to prevent \n this tragedy by hitting
the space bar. Be \n merciful to your \nkeyboard..."""
        right="""\
In the duo mode, you or \n your parter should use 
mouse to shoot at the \n targets to power up the
bird.\nIn the reversed mode, \n press spacebar to prevent 
the bird from passing the\n pipe!"""
        canvas.create_text(margin,margin,text=left,font=font,fill=color,
                           anchor="nw")
        canvas.create_text(self.w-margin,margin,text=right,font=font,fill=color,
                           anchor="ne")

    def drawPause(self,canvas):
        # draw pause button and pause screen
        if not self.pause: self.buttons["pause"].draw(canvas)
        else: self.drawPauseScreen(canvas)

    def drawPhase1Animation(self,canvas):
        # draw the animation at the help page
        period=self.timerDelay*2.0
        frame=self.step%period
        totalFrames=10
        x,y=self.w/2,self.h/2
        subF=float(period)/totalFrames
        for i in xrange(10):
            if frame<subF*(i+1):
                imageName="instr"+str(i)
                canvas.create_image(x,y,image=self.images[imageName])
                return

    def draw2DModeBackgroundAnimation(self,canvas):
        cx=self.w/2
        cy=self.h/2
        r=self.h/4
        duration=100.0
        period=self.timerDelay*duration
        CIRCLE=math.pi*2
        distance=self.step%period
        angle=(distance)/period*CIRCLE

        # zoom in and zoom out of the squares
        zoomFreq=8
        smallPeriod=period/zoomFreq
        smallDistance=distance%smallPeriod
        zoomAdjust=1.1
        zoomSpeed=6
        if smallDistance<smallPeriod/zoomSpeed:
            r*=smallDistance/(smallPeriod/zoomSpeed)*zoomAdjust
        elif smallDistance>smallPeriod/zoomSpeed*(zoomSpeed-1):
            r*=(1.0-(smallDistance-smallPeriod/zoomSpeed*(zoomSpeed-1))/
                (smallPeriod/zoomSpeed))*zoomAdjust

        self.recursiveDrawSquare(canvas,cx,cy,r,angle,2)

    def recursiveDrawSquare(self,canvas,cx,cy,r,angle,depth):
        if depth==0:
            color=colorAdjust(1.1,self.rgb)
            canvas.create_rectangle(cx-r,cy-r,cx+r,cy+r,fill=color,width=0)
        else:
            sides=self.sides
            for add in xrange(sides):
                addAngle=math.pi*2/sides*add
                self.recursiveDrawSquare(canvas,
                                         cx+r*math.cos(angle+addAngle),
                                         cy+r*math.sin(angle+addAngle),
                                         r/4,angle,depth-1)

    def draw3DBackGround(self,canvas):
        # shared by phase3 and phase4
        darken=0.02
        color=colorAdjust(darken,self.rgb)
        canvas.create_rectangle(0,0,self.w,self.h,fill=color,width=0)
        for pipe in reversed(self.pipes):
                    pipe.draw(canvas,self)
        self.drawIntroInGame(canvas)
        self.drawScore(canvas)

    def drawInkAnimation(self,canvas,cx,cy,r):
        # animation on the phase 0
        if self.step>self.timerDelay*5.0:
            # small animation of ink being dripped over the text "3D"
            canvas.create_image(cx,cy+10,image=self.images["moji"])
            if self.step>self.timerDelay*7.0:
                offSetX,offSetY,r=100,80,5
                canvas.create_oval(cx+offSetX-r,cy+offSetY-r,
                                   cx+offSetX+r,cy+offSetY+r,
                                   width=0,fill="black")
                if self.step>self.timerDelay*7.5:
                    offSetX,offSetY,r=180,95,8
                    canvas.create_oval(cx+offSetX-r,cy+offSetY-r,
                                       cx+offSetX+r,cy+offSetY+r,
                                       width=0,fill="black")

    def drawLifeBar(self,canvas):
        # draw the rectangle / life bar at the bottom of phase 4
        margin=10
        barH=20
        barW=self.lifeBar
        w,h=self.w,self.h
        color=colorAdjust(1.2,self.rgb)
        canvas.create_rectangle((w-self.maxLife)/2,h-margin-barH,
                                (w+self.maxLife)/2,h-margin,
                                outline=self.BGColor,width=1)
        canvas.create_rectangle((w-barW)/2,h-margin-barH,(w+barW)/2,h-margin,
                                fill=color,width=0)

    def drawCooldownCircle(self,canvas):
        # cool down circle around the mouse pointer in phase 4
        cx,cy=self.mouseX,self.mouseY
        r=20
        DEGREE_OF_CIRCLE=360
        degree=float(self.cooldown)*DEGREE_OF_CIRCLE
        # print degree
        circleWidth=6
        canvas.create_arc(cx-r,cy-r,cx+r,cy+r,start=90,extent=degree,
                          outline="grey",width=circleWidth,style="arc")

    def drawPauseScreenText(self,canvas,margin):
        # draw the information appear on the pause screen
        size=str(self.h/35)
        color=colorAdjust(0.8,self.rgb)
        text="History Highest: "+ str(self.highScore[self.phase])
        canvas.create_text(self.w/2,self.h*2/3-5,text=text,
                           font="coda "+size,fill=color,anchor="s")

        size=str(self.h/15)
        color=colorAdjust(1.1,self.rgb)
        canvas.create_text(self.w/2,self.h/3,text="Your current score:",
                           font="coda "+size,fill=color)
        size=str(self.h/6)
        canvas.create_text(self.w/2,self.h/2,text=str(self.score),fill="white",
                           font="coda "+size)
        period=self.timerDelay*10.0
        if self.step%period>period*0.5:
            color=colorAdjust(1.2,self.rgb)
            canvas.create_text(self.w/2,self.h-margin-5,
                               text="- Press spacebar to continue -",anchor="s",
                               font="coda "+str(self.h/18),fill=color)

    def drawPauseScreen(self,canvas):
        # pause screen appears when inGame() and self.pause
        margin=min(self.h,self.w)/6
        color=colorAdjust(0.6,self.rgb)
        canvas.create_rectangle(margin,margin,self.w-margin,self.h-margin,
                                fill=color,width=0)
        margin*=1.5
        color=colorAdjust(0.8,self.rgb)
        canvas.create_rectangle(margin,margin,self.w-margin,self.h-margin,
                                outline=color)
        self.drawPauseScreenText(canvas,margin)        
        self.inGameBackBtn.draw(canvas)

    def drawScore(self,canvas):
        # drawScore in 3D mode
        nearPipe=self.pipes[0]
        ratio=get3DRatio(self.VanishPoint45,nearPipe.d3D)
        y=self.vp+ratio*(nearPipe.gapStart)
        size=str(int(nearPipe.gap/4*ratio))
        color=colorAdjust(1.2,self.rgb)
        canvas.create_text(self.w/2,y,text=str(self.score+1),fill=color,
                           anchor="s",font="coda "+size)

    def drawScore2D(self,canvas):
        # drawScore in phase 5
        size=str(self.h/8)
        canvas.create_text(self.w/2,self.h/5*4,text=str(self.score),
                           fill="white",anchor="n",font="coda "+size)

    def drawScoreReversed(self,canvas):
        # drawScore in phase 6
        size=str(self.h/6)
        color=colorAdjust(1.1,self.rgb)
        canvas.create_text(self.w/2,self.h/2,text=str(self.score),
                           fill=color,font="coda "+size)

    def drawIntroInGame(self,canvas):
        # remind the player to press space bar
        if self.score==0:
            freq=self.timerDelay*3
            if self.step%freq<freq/2:
                if 3<=self.phase<=4:
                    # 3D mode
                    nearPipe=self.pipes[0]
                    size3D=nearPipe.gap/6.0
                    ratio=get3DRatio(self.VanishPoint45,nearPipe.d3D)
                    size=str(int(size3D*ratio))
                    y=self.vp+(nearPipe.gapStart+nearPipe.gap)*ratio
                    canvas.create_text(self.w/2,y,text="SPACEBAR", fill="grey",
                                       font="coda "+size,anchor="s")
                else: # 2D mode
                    size=str(self.h/11)
                    canvas.create_text(self.w/2,self.h*5/7,text="SPACEBAR",
                                       fill="white",font="coda "+size)

    def drawModeInfo(self,canvas):
        # the instruction appears when mouse on the mode selecting buttons
        x,y=self.w*0.95,self.h/10
        if self.drawInfo==self.buttons["classicMode"]:
            instr="""The "classical" Flappy Bird.
History highest: """+str(self.highScore[5])
        elif self.drawInfo==self.buttons["normalMode"]:
            instr="""Play Flappy Bird in 3D!
History highest: """+str(self.highScore[3])
        elif self.drawInfo==self.buttons["duoMode"]:
            instr="""Power up each other by 
shooting at target!
(Solo if you want to)
History highest: """+str(self.highScore[4])
        elif self.drawInfo==self.buttons["reversedMode"]:
            instr="""See how many birds you 
can capture!
History highest: """+str(self.highScore[6])
        canvas.create_text(x,y,text=instr,anchor="ne",font="coda "+
                           str(self.h/25),fill="white")

################################################################################
################################ ctrl functions ################################
################################################################################
    def inGame(self):
        # check if the player is currently in the game screen
        return 3<=self.phase<=6

    def onKey(self,event):
        if self.inGame():
            # if the user press space in game
            if ((not self.isOver) and event.keysym == "space"):
                if self.phase==6:
                    self.executioner.speed=40
                self.pause=False
                self.down=False
                self.downSpeed=20

    def onKeyRelease(self,event):
        self.executioner.speed=-15
        self.down=True

    def addPipe(self):
        # add a pipe and set its attributes according to the former pipe
        prevPipe=self.pipes[len(self.pipes)-1]

        neww3D=prevPipe.w3D
        newd3D=prevPipe.d3D+prevPipe.gapToNext
        newl3D=random.randint(200,1000)
        newGap=random.randint(self.h*2/3,self.h*5/4)

        # determine the gapStart to make sure the game is still playable
        angleAdjust=1.3
        angleRatio=float(prevPipe.gap)/prevPipe.gapToNext*angleAdjust
        shift=int((prevPipe.gapToNext-prevPipe.l3D)*angleRatio)
        newGapStart=prevPipe.gapStart+random.randint(-shift,shift)

        # make the game faster and faster
        acceleration=0.3
        newSpeed=prevPipe.forwardSpeed+acceleration
        if newSpeed>=35:
            newSpeed=35

        newPipe=Pipe(neww3D,newd3D,newGap,newl3D,newGapStart,newSpeed)
        self.pipes.append(newPipe)

    def addChallenger(self):
        # randomly decide whether or not we should add a new one
        # guadually increase its speed range by the log based ratio
        if self.speedUpStart!=None:
            incrBase=15
            ratio=math.log(self.step-self.speedUpStart+incrBase,incrBase)
        else: ratio=1
        avgAddTime=0.8 # second per new bird
        ONE_SEC=1024.0
        avgStep=avgAddTime*ONE_SEC/self.timerDelay
        if ((len(self.challengers)<1 or random.random()<1/avgStep) and 
            (len(self.challengers)<3)):
            # randomize the starting location
            startX=self.w/random.randint(8,11)
            startY=self.h/2+self.h/12*(random.random()*2-1)
            self.challengers.append(Challenger(startX,startY,self.rgb,ratio))

    def upDatePhase4(self):
        if self.cooldown<=0: self.cooldown=0
        else: self.cooldown-=1.0/self.totalCooldownTime
        self.lifeBar-=self.maxLife/self.totalCooldownTime/self.miss
        if self.lifeBar<0: self.isOver=True
        if self.missile!=None:
            self.missile.y3D+=self.downSpeed
            if (self.missile.d3D>self.pipes[0].d3D):
                if self.target.hitInside(self.missile.x3D,self.missile.y3D):
                    self.lifeBar=self.maxLife
                self.missile=None
            elif (self.missile.y3D>self.h*2):
                self.missile=None                    
            else: self.missile.move()
        self.target.y3D+=self.downSpeed

    def updatePhase6Bird(self):
        for bird in self.challengers:
            if bird.downSpeed>=bird.maxDownSpeed:
                bird.downSpeed=-bird.maxDownSpeed
            bird.downSpeed+=bird.acceleration
            bird.y+=bird.downSpeed
            bird.x+=bird.forwardSpeed
            if bird.isKilled(self.executioner):
                self.challengers.remove(bird)
                self.score+=1
                if self.score==1:
                    # start to speed up
                    self.speedUpStart=self.step
            elif bird.x>=self.w:
                self.isOver=True

    def updatePhase6(self):
        pipe=self.executioner
        gap=pipe.bottom-pipe.top

        # clamp the pipe according to its current location
        backSpeed=-20
        completelyClosed=-20
        if gap<-completelyClosed: 
            pipe.speed=backSpeed
        elif gap>pipe.maxH*2: 
            pipe.speed=0
            center=self.h/2
            pipe.top=center-pipe.maxH
            pipe.bottom=center+pipe.maxH
        pipe.top+=self.executioner.speed
        pipe.bottom-=pipe.speed

        self.addChallenger()
        self.updatePhase6Bird()

    def updatePipes(self):
        # update pipes in phase3, 4, and 5
        if self.pipes[0].isCollide(self.bird):
            self.isOver=True
            return
        for pipe in self.pipes:
            pipe.moveForward()
            pipe.gapStart+=self.downSpeed
            if pipe.d3D<=-pipe.l3D:
                # when the bird fully passes a pipe
                self.pipes=self.pipes[1:]
                self.score+=1
                self.target=Target(self.pipes[0])
        while len(self.pipes)<self.pipeNum: 
            self.addPipe()

    def onStep(self):
        if self.isOver: 
            self.phase=7
            if not self.scoreWritten:
                self.writeHighScore()
                self.scoreWritten=True
        elif self.inGame() and (not self.pause):
            if self.phase==6: self.updatePhase6() 
            else:
                acceleration=1 
                self.downSpeed-=acceleration
                if self.pipes[0].d3D<self.bird.d3D: self.isInShadow=True
                else: self.isInShadow=False
                if self.phase==4: self.upDatePhase4() 
                self.updatePipes()
            self.updateHighestScore(self.phase,self.score)

    def onMouse(self,event):
        x,y=event.x,event.y

        # check if it is a click on any button
        for button in self.buttons:
            if (self.phase in self.buttons[button].existPhase and 
                self.buttons[button].clickInside(x,y)):
                self.buttons[button].goTo(self)
                if not isinstance(self.buttons[button],self.PauseButton):
                    self.mode=self.buttons[button].target
                return

        # if the user want to return to main menu
        if (self.inGame() and self.pause) or (self.phase==7):
            if self.inGameBackBtn.clickInside(x,y):
                self.initVariable()
                self.phase=2
                return

        # if the user intend to launch a missile
        if (self.phase==4 and (not self.pause) and (not self.isOver) 
            and self.cooldown==0):
            self.initMissile(x,y)
            self.cooldown=1.0
            return

    def onMouseMove(self,event):
        if self.phase==2:
            modeButton=([self.buttons["classicMode"],
                         self.buttons["normalMode"],
                         self.buttons["duoMode"],
                         self.buttons["reversedMode"]])
            for button in modeButton:
                if button.clickInside(event.x,event.y):
                    self.drawInfo=button
                    return
            self.drawInfo=False
        elif self.phase==4:
            self.mouseX,self.mouseY=event.x,event.y

    def updateHighestScore(self,phase,score):
        self.highScore[phase]=max(self.highScore[phase],score)

    def writeHighScore(self):
        # write the current highest score into local log after every game ends
        fileName="highScore.txt"
        content=""
        for phase in xrange(3,7):
            if len(content)>0:
                content+="\n"
            content+=str(phase)+" "+str(self.highScore[phase])
        writeFile(fileName,content)

GUI(width=1000,height=600,timerDelay=8).run()

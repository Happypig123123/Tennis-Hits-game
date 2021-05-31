from matplotlib.pyplot import title
import pygame
import os 
import objects
import random
#setup
size = (960,720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tennis Hits")
pygame.init()
#clock setup
clock = pygame.time.Clock()

gameFinished = False
#set background
bg = pygame.image.load(os.path.join("img","background.png"))

#menu object list:
menuObects = pygame.sprite.Group()

#start title screen sequence:
titleSequence = objects.titleScreen()
menuObects.add(titleSequence)
gameStarted = False #True when title/help sequence over.

#tennis ball (main ball) object (red/green Ball):
ballObjects = pygame.sprite.Group()
mainBall = objects.ballMain()
ballObjects.add(mainBall)

#player (racket) object:
playerObjects = pygame.sprite.Group()
player = objects.player()
playerObjects.add(player)

#specialty ball objects:
activeSpecialBalls = {"DEATH":0,"TIME":0,"BONUS":0}

hitWhenNotReady = False #changes when player hits ball when not ready; and prevents more than 1 point from being lost.

##prevV = 0 #FOR DATA ANALYSIS OF THE Z VELOCITY OF MAINBALL
NextSpawnTime = 9999999999 #The next time a ball spawns
while gameFinished == False: #main loop; change gameFinished when game is exited to True
    ##if mainBall.vz != prevV:#FOR DATA ANALYSIS OF THE Z VELOCITY OF MAINBALL
    ##    print(pygame.time.get_ticks(),mainBall.vz,NextSpawnTime)#FOR DATA ANALYSIS OF THE Z VELOCITY OF MAINBALL
    ##    prevV = mainBall.vz#FOR DATA ANALYSIS OF THE Z VELOCITY OF MAINBALL
    
    
    #=============== main event loop:
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.QUIT:
            gameFinished = True
        if event.type == pygame.MOUSEBUTTONDOWN: #when key pressed:
            if event.button == 1 and not gameStarted: #left click:
                gameStarted = titleSequence.nextImage()
                if gameStarted:
                    NextSpawnTime = 3000
                print("TitleScreen.next")

        if True: #Change to false when not debuging the specialty balls
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    deathBall = objects.deathBall()
                    activeSpecialBalls["DEATH"] = True
                    ballObjects.add(deathBall)
                if event.key == pygame.K_b:
                    bonusBall = objects.bonusBall()
                    activeSpecialBalls["BONUS"] = True
                    ballObjects.add(bonusBall)
                if event.key == pygame.K_t:
                    timeBall = objects.timeBall()
                    activeSpecialBalls["TIME"] = True
                    ballObjects.add(timeBall)
        
            

    

    #====== drawing code:
    screen.blit(bg, (0, 0)) #background
    menuObects.draw(screen)

    if gameStarted: # === code to run when game is started; and not on a start menu screen.
        ballObjects.draw(screen) #draw the main ball
        playerObjects.draw(screen) #draw the player racket.
        #======= movement of ball objects [handles physics]
        if activeSpecialBalls["DEATH"]:
            deathBall.move()
            if deathBall not in ballObjects:
                activeSpecialBalls["DEATH"] = False
        if activeSpecialBalls["BONUS"]:
            bonusBall.move()
            if bonusBall not in ballObjects:
                activeSpecialBalls["BONUS"] = False
        if activeSpecialBalls["TIME"]:
            timeBall.move()
            if timeBall not in ballObjects:
                activeSpecialBalls["TIME"] = False

        mainBall.move() #handles physics for main ball

        #====== movemnt of player object
        player.move() #handels players racket staying in position with mouse cursor.
        
        #====== Colision Detection
        #  check for collision between balls and racket:
        collisions = pygame.sprite.spritecollide(player, ballObjects, False)
        if collisions:
            if mainBall in collisions: #main ball collision handeler:
                if mainBall.ready: #ensure ball hit with correct timing; or take a point.
                    hitWhenNotReady = False
                    mainBall.impact()
                    mainBall.impactEnabled = False
                    mainBall.ready=False
                    player.points += 1
                else:
                    if not hitWhenNotReady and mainBall.vz > 0: #only takes 1 point; and only if ball heading towards player
                        hitWhenNotReady = True
                        player.points -= 1
            
            #now check active speciality ballObjects collisions
            #we require the activeSpecialBalls dictionary to stop 'undefined' errors when these balls are not currenty active/exist.
            #the code after the and statement will not run unless the first condition is true; therefore this prevents undefinded errors in the collision check.
            if activeSpecialBalls["DEATH"] and deathBall in collisions:
                gameFinished = "DEATH_BALL" #end game
            if activeSpecialBalls["BONUS"] and bonusBall in collisions:
                player.points += 5
                bonusBall.z = 2 #causes the ball to 'die' as ball will kill its self when z > 1
            if activeSpecialBalls["TIME"] and timeBall in collisions:
                mainBall.vz *= .75 #reduce the main ball's velocity to 75% of its current value
                timeBall.z = 2 #causes the ball to 'die' as ball will kill its self when z > 1

                
        

        #check if  game over due to mainball traveling past z=1
        if mainBall.gameOver:
            gameFinished = "BALL_PAST_PLAYER"
        
        
        #display score:
        text = str(player.points)
        LargeText = pygame.font.Font('freesansbold.ttf',90)
        TextSurf, TextRect = objects.text_object(text, LargeText)
        TextRect.center = ((objects.screenWidth/2),50)
        screen.blit(TextSurf, TextRect)

        #====== random spawn of specialty balls:
        
        if NextSpawnTime < pygame.time.get_ticks():
            NextSpawnTime = pygame.time.get_ticks() + random.randint(3000,8000) #spawn every 1 to 5 seconds
            toSpawn = random.randint(1,3) #which ball to spawn (random choice)

            #DEBUG
            #print("SPAWNING:",toSpawn,"CURRENT TIME:",pygame.time.get_ticks(),"NEXT SPAWN:",NextSpawnTime)


            #MAIN
            #need to also ensure that other ball of same type does not already exist on screen
            if toSpawn == 1 and activeSpecialBalls["DEATH"] == False:
                deathBall = objects.deathBall()
                activeSpecialBalls["DEATH"] = True
                ballObjects.add(deathBall)
            if toSpawn == 2 and activeSpecialBalls["BONUS"] == False:
                bonusBall = objects.bonusBall()
                activeSpecialBalls["BONUS"] = True
                ballObjects.add(bonusBall)
            if toSpawn == 3 and activeSpecialBalls["TIME"] == False:
                timeBall = objects.timeBall()
                activeSpecialBalls["TIME"] = True
                ballObjects.add(timeBall)

        

        

            

    #update screen:
    pygame.display.flip()
    clock.tick(60) #60fps
    #print(player.points)
print(gameFinished,player.points)
pygame.quit()

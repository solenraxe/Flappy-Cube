import pygame
from random import randint
import math
import json
pygame.init()
pygame.font.init()
pygame.joystick.init()

data = {}
with open('data/data.json', 'r') as f:
    data = json.load(f)

bad_words = []
with open("data/bad_words.json", "r") as f:
    bad_words = json.load(f)

best_scores = []
for i in range(1, len(data) + 1):
    best_scores.append(data[str(i)]["score"])
best_score = best_scores[-1] if best_scores != [] else 0

choosingName = False
currentLetter = 0
letterList = [chr(i) for i in range(97, 123)] + [str(i) for i in range(0, 10)] + ["_"]
currentLetterIndex = -1
chosenLetters = ["_", "_", "_"]
previousScore = 0

joysticks = []
joysticks_nb = pygame.joystick.get_count()

#font = pygame.font.get_fonts()[randint(0, len(pygame.font.get_fonts()) - 1)]
#print(f"Using font : {font}")
comicSans = pygame.font.SysFont('Comic Sans MS', 30)
#liberationmono, segoemdl2assets

WIDTH, HEIGHT = 800, 600
framecount = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption("Flappy Cube")
pygame.display.set_icon(pygame.image.load('assets/Dino/DinoWhite.png').convert_alpha())

itemsSize = {
    "Player": (WIDTH//16, HEIGHT//12),
    "Pipe": (WIDTH//12.3, HEIGHT),
    "PipeTop": (WIDTH//13.33, HEIGHT//22.22),
    "Background": (WIDTH, HEIGHT),
    "Cloud": (WIDTH//5.33, HEIGHT//4)
}

assets = {
    "Pipe": pygame.image.load('assets/pipe.png').convert_alpha(),
    "PipeTop": pygame.image.load('assets/pipeTop.png').convert_alpha(),
    "Background": pygame.image.load('assets/background.png').convert(),
    "Cloud": pygame.image.load('assets/cloud.png').convert_alpha(),
    "Laser": pygame.image.load('assets/laser.png').convert_alpha()
}
assets["Cloud"].set_alpha(200)
assets["PipeTop180"] = pygame.transform.rotate(assets["PipeTop"], 180)
assets["Pipe"] = pygame.transform.scale(assets["Pipe"], itemsSize["Pipe"])
assets["Pipe180"] = pygame.transform.rotate(assets["Pipe"], 180)

colorList = ["White", "Green", "Blue", "Red", "Yellow", "Cyan", "Magenta"]
skinList = ["Dino", "Cube", "Pig", "Duck", "Bear", "Cat"]
colors = {
    "White": (255, 255, 255),
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Black": (0, 0, 0),
    "CoolerBlue": (0, 183, 239),
    "Gray": (64, 64, 64)
}
currentSelection = 0

for skin in skinList:
    for color in colorList:
        assets[f"{skin}{color}"] = pygame.image.load(f'assets/{skin}/{skin}{color}.png').convert_alpha()

class Player:
    def __init__(self, num):
        self.rect = pygame.Rect(100 - num * 10 + 20, HEIGHT//2, 50, 50)
        self.sprite = assets["DinoWhite"]
        self.color = 0
        self.vy = 0
        self.jumpPower = 18
        self.gravity = 0.5
        self.inertia = 0.5
        self.number = num
        self.alive = True
        self.unspentPoints = 2
        self.skin = 0
        self.ability = 0
        self.coolDown = 0
        self.effects = []

    def physics_update(self, deltat):
        if self.vy < 20 and self.vy >= -10:
            if self.vy >= 0:
                self.vy += self.gravity * 2 * self.inertia
            else:
                self.vy = (self.vy * 1.950 * self.inertia + self.gravity * 2 * self.inertia) if self.inertia * 1.95 < 1 else (self.vy * 0.999 + self.gravity * 2 * self.inertia)
        elif self.vy < -10:
            self.vy *= 1.6 * self.inertia if self.inertia * 1.6 < 0.95 else 0.95
        if self.rect.y + self.vy < HEIGHT - self.rect.height and self.rect.y + self.vy > 0:
            self.rect.y += self.vy * deltat * 60
        else:
            if self.rect.y + self.vy >= HEIGHT - self.rect.height:
                self.rect.y = HEIGHT - self.rect.height
            else:
                self.rect.y = 0
            self.vy = 0
        
        self.coolDown -= 1 if self.coolDown >= 1 else 0
        for effect in self.effects:
            effect["Duration"] -= 1
            if effect["Duration"] <= 0:
                player_effect(self, effect["Name"], on=False)

    def reset(self):
        self.rect.y = HEIGHT//2
        self.vy = 0
        self.alive = True
        for effect in self.effects:
            effect["Duration"] = 0
            player_effect(self, effect["Name"], on=False)
        self.coolDown = 0
        self.rect = pygame.Rect(100 - self.number * 10 + 20, HEIGHT//2, 50, 50)

class ObstacleTuple:
    def __init__(self, randomNum, gavePoint=False):
        self.top = pygame.Rect(WIDTH, randomNum - HEIGHT, 65, 600)
        self.bottom = pygame.Rect(WIDTH, randomNum + 200 * gameVariables["gapSize"], 65, 600)
        self.gavePoint = gavePoint

        self.top_surf = assets["Pipe180"]
        self.bottom_surf = assets["Pipe"]

        self.top_cap = assets["PipeTop180"]
        self.bottom_cap = assets["PipeTop"]

    def move(self, dx):
        self.top.x += dx
        self.bottom.x += dx

class Cloud:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 200, 200)

    def update(self, deltat):
        self.rect.x -= int(gameSpeed * deltat * 60)
        if self.rect.x + self.rect.width < 0:
            self.rect.x = WIDTH + randint(0, 800)

class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 20)
        self.lifetime = 60
        self.speed = 20

    def update(self, deltat):
        self.rect.x += self.speed * deltat * 60
        self.lifetime -= 1

obstacleList = []
playerList = []
cloudList = []
laserList = []
background_x = 0
playersAlive = 1
playerList.append(Player(1))

gameSpeed = 5
score = 0

def render_score(s):
    return comicSans.render(f"Score : {s}", False, (255, 255, 255))
scoreText = render_score(score)
gameStarted = False
gameInit = False

dt = 0.1
currentSpacing = 90

menuList = ["Play", "Skins", "Colors", "Stats", "Abilities", "Leaderboard", "Settings"]
currentMenu = 0
menuText = comicSans.render(menuList[currentMenu], False, colors["White"])

menusTexts = {
    "PlayTexts" : {
        1 : comicSans.render("Press DOWN to play!", False, colors["White"])
    },
    "SkinsTexts" : {
        1 : comicSans.render("Press DOWN or UP to change skin!", False, colors["White"]),
        2 : comicSans.render(f"Current skin : Dino", False, colors["White"])
    },
    "ColorsTexts" : {
        1 : comicSans.render("Press DOWN or UP to change color!", False, colors["White"]),
        2 : comicSans.render(f"Current color : {colorList[playerList[currentSelection].color]}", False, colors["White"])
    },
    "StatsTexts" : {
        1 : comicSans.render("Press UP to increase, DOWN to decrease.", False, colors["White"]),
        2 : comicSans.render(f"Unspent Points : {playerList[currentSelection].unspentPoints}", False, colors["White"])
    },
    "AbilitiesTexts" : {
        1 : comicSans.render(f"Current ability : Shrink", False, colors["White"])
    },
    "LeaderboardTexts" : {
        # to be filled dynamically
    },
    "SettingsTexts" : {
        1 : comicSans.render("Press TAB to change setting.", False, colors["White"]),
        2 : comicSans.render("Press UP or DOWN to change setting value.", False, colors["White"])
    }
}

def updateLeaderboard():
    for i, v in enumerate(data.values()):
        menusTexts["LeaderboardTexts"][i + 1] = comicSans.render(f"{i + 1}. {v['playerName']} : {v['score']}", False, colors["White"])
updateLeaderboard()

menusOffset = {
    "Play": 125,
    "Skins": 0,
    "Colors": 0,
    "Stats": 0,
    "Abilities": 125,
    "Leaderboard": -20,
    "Settings": 0
}

colorSpecialText = comicSans.render(f"Current player selection : P{currentSelection + 1}", False, colors["White"])

pauseText = comicSans.render("Game Paused! Press ESC to resume.", False, colors["White"])

settingsList = ["Player Count", "Difficulty", "Clouds Number", "Background"]
currentSetting = 0
difficultyList = ["Easy", "Normal", "Hard"]
cloudsNumber = 5
clouds = True
settings = {
    "Player Count": [comicSans.render(f"Player Count : {1}", False, colors["Red"]), "Red", 1],
    "Difficulty": [comicSans.render(f"Difficulty : {difficultyList[1]}", False, colors["White"]), "White", "Normal", 1],
    "Clouds Number": [comicSans.render(f"Clouds Number : 5", False, colors["White"]), "White", 5],
    "Background": [comicSans.render(f"Background : On", False, colors["White"]), "White", "On"]
}

max_players = 2

statsList = ["Jump Power", "Inertia", "Gravity"]
currentStat = 0
stats = {
    "Jump Power": [18, "Red", "jumpPower"],
    "Inertia": [0.5, "White", "inertia"],
    "Gravity": [0.5, "White", "gravity"]
}

abilitiesList = ["Shrink", "Laser", "Revive"]
abilitiesCoolDown = [400, 800, 2000]
for ability in abilitiesList:
    assets[f"{ability}Icon"] = pygame.image.load(f'assets/Icons/{ability}.png').convert_alpha()

gameVariables = {
    "gameSpeedMax": 1,
    "adjustment": 1,
    "spacing": 1,
    "gapSize": 1
}

def create_obstacle():
    previousObstacle = obstacleList[-1] if len(obstacleList) > 0 else None
    minY, maxY = 50, 350
    if previousObstacle:
        lastY = previousObstacle.top.height
        minY = max(50, lastY - math.floor((currentSpacing - gameSpeed*4 * gameVariables["adjustment"]) * 2 * gameVariables["adjustment"]))
        maxY = min(HEIGHT - 250, lastY + math.floor((currentSpacing - gameSpeed*4 * gameVariables["adjustment"]) * 2 * gameVariables["adjustment"]))
    randomNum = randint(minY, maxY)
    obstacleList.append(ObstacleTuple(randomNum))

def player_effect(player, effect, on=True, duration=180):
    if effect == "Shrinked":
        if on:
            player.effects.append({"Name": "Shrinked", "Duration": duration})
            player.rect.height, player.rect.width = 25, 25
            player.sprite = pygame.transform.scale(player.sprite, (25, 25))
            player.rect.y += 12
            player.rect.x += 12
        else:
            player.effects.remove({"Name": "Shrinked", "Duration": 0})
            player.rect.height, player.rect.width = 50, 50
            player.sprite = pygame.transform.scale(player.sprite, (50, 50))
            player.rect.y -= 12
            player.rect.x -= 12

def use_ability(player, abilityNum):
    if player.coolDown == 0:
        if abilityNum == 0:  # Shrink
            player_effect(player, "Shrinked", on=True, duration=180)
        elif abilityNum == 1:  # Laser
            laserList.append(Laser(player.rect.x + player.rect.width, player.rect.y + player.rect.height//2 - 5))
        elif abilityNum == 2:  # Revive
            for player in playerList:
                player.alive = True
        
        player.coolDown = abilitiesCoolDown[abilityNum]

def keyRightMenu():
    global currentMenu, menuText
    if currentMenu < len(menuList) - 1:
        currentMenu += 1
    else:
        currentMenu = 0
    menuText = comicSans.render(menuList[currentMenu], False, colors["White"])

def keyLeftMenu():
    global currentMenu, menuText
    if currentMenu > 0:
        currentMenu -= 1
    else:
        currentMenu = len(menuList) - 1
    menuText = comicSans.render(menuList[currentMenu], False, colors["White"])

def keyDownMenu():
    global currentMenu, gameStarted, currentSelection, currentSetting, currentStat, playerList, skinList, colorList, settings, cloudsNumber, clouds, stats, abilitiesList, max_players, colors, menusTexts, menuList, difficultyList, gameVariables, statsList, settingsList
    if menuList[currentMenu] == "Play":
        gameStarted = True

    elif menuList[currentMenu] == "Skins":
        if playerList[currentSelection].skin < len(skinList) - 1:
            playerList[currentSelection].skin += 1
        else:
            playerList[currentSelection].skin = 0
        menusTexts["SkinsTexts"][2] = comicSans.render(f"Current skin : {skinList[playerList[currentSelection].skin]}", False, colors["White"])
        playerList[currentSelection].sprite = assets[f"{skinList[playerList[currentSelection].skin]}{colorList[playerList[currentSelection].color]}"]
                        
    elif menuList[currentMenu] == "Colors":
        if playerList[currentSelection].color < len(colorList) - 1:
            playerList[currentSelection].color += 1
        else:
            playerList[currentSelection].color = 0
        menusTexts["ColorsTexts"][2] = comicSans.render(f"Current color : {colorList[playerList[currentSelection].color]}", False, colors["White"])
        playerList[currentSelection].sprite = assets[f"{skinList[playerList[currentSelection].skin]}{colorList[playerList[currentSelection].color]}"]
                        
    elif menuList[currentMenu] == "Settings":
        changedSetting = settingsList[currentSetting]
                            
        if changedSetting == "Difficulty":
            settings["Difficulty"][3] -= 1
            if settings["Difficulty"][3] < 0:
                settings["Difficulty"][3] = len(difficultyList) - 1
            settings["Difficulty"][2] = difficultyList[settings["Difficulty"][3]]
            for i, v in gameVariables.items():
                gameVariables[i] = 1 - (settings["Difficulty"][3] - 1) * 0.2
                           
        elif changedSetting == "Player Count":
            settings["Player Count"][2] -= 1
            if settings["Player Count"][2] <= 0:
                settings["Player Count"][2] = max_players
            playerStats = []
            for i in range(max_players):
                if len(playerList) > i:
                    playerStats.append((playerList[i].jumpPower, playerList[i].inertia, playerList[i].gravity, playerList[i].unspentPoints, playerList[i].color, playerList[i].sprite, playerList[i].skin))
                else:
                    playerStats.append((18, 0.5, 0.5, 2, 0, assets["DinoWhite"], 0))
            playerList = []
            for i in range(settings["Player Count"][2]):
                playerList.append(Player(i + 1))
                playerList[i].jumpPower, playerList[i].inertia, playerList[i].gravity, playerList[i].unspentPoints, playerList[i].color, playerList[i].sprite, playerList[i].skin = playerStats[i]
            currentSelection = 0
                                
        elif changedSetting == "Clouds Number":
            settings["Clouds Number"][2] -= 1
            if settings["Clouds Number"][2] < 0:
                settings["Clouds Number"][2] = 15
            cloudsNumber = settings["Clouds Number"][2]
            clouds = cloudsNumber > 0
                                
        elif changedSetting == "Background":
            if settings["Background"][2] == "On":
                settings["Background"][2] = "Off"
        else:
            settings["Background"][2] = "On"
        settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                        
    elif menuList[currentMenu] == "Stats":
        statName = statsList[currentStat]
        decrease = 1
        newValue = getattr(playerList[currentSelection], stats[statName][2])
        if newValue > 0.1 * decrease:
            newValue = ((newValue * 10 - decrease)/10) if statName != "Jump Power" else newValue - decrease
            playerList[currentSelection].unspentPoints += 1
            setattr(playerList[currentSelection], stats[statName][2], newValue)
        menusTexts["StatsTexts"][2] = comicSans.render(f"Unspent Points : {playerList[currentSelection].unspentPoints}", False, colors["White"])
                    
    elif menuList[currentMenu] == "Abilities":
        if playerList[currentSelection].ability > 0:
            playerList[currentSelection].ability -= 1
        else:
            playerList[currentSelection].ability = len(abilitiesList) - 1
        menusTexts["AbilitiesTexts"][1] = comicSans.render(f"Current ability : {abilitiesList[playerList[currentSelection].ability]}", False, colors["White"])

def keyUpMenu():
    global currentMenu, gameStarted, currentSelection, currentSetting, currentStat, playerList, skinList, colorList, settings, cloudsNumber, clouds, stats, abilitiesList, max_players, colors, menusTexts, menuList, difficultyList, gameVariables, statsList, settingsList
    if menuList[currentMenu] == "Skins":
        if playerList[currentSelection].skin > 0:
            playerList[currentSelection].skin -= 1
        else:
            playerList[currentSelection].skin = len(skinList) - 1
        menusTexts["SkinsTexts"][2] = comicSans.render(f"Current skin : {skinList[playerList[currentSelection].skin]}", False, colors["White"])
        playerList[currentSelection].sprite = assets[f"{skinList[playerList[currentSelection].skin]}{colorList[playerList[currentSelection].color]}"]
                        
    elif menuList[currentMenu] == "Colors":
        if playerList[currentSelection].color > 0:
            playerList[currentSelection].color -= 1
        else:
            playerList[currentSelection].color = len(colorList) - 1
        menusTexts["ColorsTexts"][2] = comicSans.render(f"Current color : {colorList[playerList[currentSelection].color]}", False, colors["White"])
        playerList[currentSelection].sprite = assets[f"{skinList[playerList[currentSelection].skin]}{colorList[playerList[currentSelection].color]}"]
                        
    elif menuList[currentMenu] == "Settings":
        changedSetting = settingsList[currentSetting]
                        
        if changedSetting == "Difficulty":
            settings["Difficulty"][3] += 1
            if settings["Difficulty"][3] > len(difficultyList) - 1:
                settings["Difficulty"][3] = 0
            settings["Difficulty"][2] = difficultyList[settings["Difficulty"][3]]
            for i, v in gameVariables.items():
                gameVariables[i] = 1 - (settings["Difficulty"][3] - 1) * 0.2
       
        elif changedSetting == "Player Count":
            settings["Player Count"][2] += 1
            if settings["Player Count"][2] > max_players:
                settings["Player Count"][2] = 1
            playerStats = []
            for i in range(max_players):
                if len(playerList) > i:
                    playerStats.append((playerList[i].jumpPower, playerList[i].inertia, playerList[i].gravity, playerList[i].unspentPoints, playerList[i].color, playerList[i].sprite, playerList[i].skin))
                else:
                    playerStats.append((18, 0.5, 0.5, 2, 0, assets["DinoWhite"], 0))
            playerList = []
            for i in range(settings["Player Count"][2]):
                playerList.append(Player(i + 1))
                playerList[i].jumpPower, playerList[i].inertia, playerList[i].gravity, playerList[i].unspentPoints, playerList[i].color, playerList[i].sprite, playerList[i].skin = playerStats[i]
            currentSelection = 0
                           
        elif changedSetting == "Clouds Number":
            settings["Clouds Number"][2] += 1
            if settings["Clouds Number"][2] > 15:
                settings["Clouds Number"][2] = 0
            cloudsNumber = settings["Clouds Number"][2]
            clouds = cloudsNumber > 0
                        
        elif changedSetting == "Background":
            if settings["Background"][2] == "On":
                settings["Background"][2] = "Off"
            else:
                settings["Background"][2] = "On"
        settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                        
    elif menuList[currentMenu] == "Stats":
        statName = statsList[currentStat]
        increase = 1
        newValue = getattr(playerList[currentSelection], stats[statName][2])
        if playerList[currentSelection].unspentPoints > 0:
            newValue = ((newValue * 10 + increase)/10) if statName != "Jump Power" else newValue + increase
            playerList[currentSelection].unspentPoints -= 1
            setattr(playerList[currentSelection], stats[statName][2], newValue)
        menusTexts["StatsTexts"][2] = comicSans.render(f"Unspent Points : {playerList[currentSelection].unspentPoints}", False, colors["White"])
                
    elif menuList[currentMenu] == "Abilities":
        playerList[currentSelection].ability = (playerList[currentSelection].ability + 1) % len(abilitiesList)
        menusTexts["AbilitiesTexts"][1] = comicSans.render(f"Current ability : {abilitiesList[playerList[currentSelection].ability]}", False, colors["White"])

running = True
while running:
    if gameStarted == True:
        if not gameInit:
            screen.fill(colors["Black"])
            obstacleList = []
            for player in playerList:
                player.reset()
            if len(playerList) < settings["Player Count"][2]:
                for i in range(settings["Player Count"][2] - len(playerList)):
                    playerList.append(Player(len(playerList) + 1))
            else:
                playerList = playerList[:settings["Player Count"][2]]
            playersAlive = settings["Player Count"][2]
            score = 0
            scoreText = render_score(score)
            gameSpeed = 5
            currentSpacing = 90
            gameInit = True
            cloudList = [Cloud(WIDTH + randint(0, WIDTH * 2), i * int(600/cloudsNumber) + 20) for i in range(cloudsNumber)]

            joysticks = []
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joystick)
            joysticks_nb = pygame.joystick.get_count()

            if joysticks_nb > 0:
                max_players = min(joysticks_nb, 4)

        framecount += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    playerList[0].vy -= playerList[0].jumpPower
                elif event.key == pygame.K_DOWN and settings["Player Count"][2] >= 2:
                    playerList[1].vy -= playerList[1].jumpPower
                elif event.key == pygame.K_RIGHT and settings["Player Count"][2] >= 3:
                    playerList[2].vy -= playerList[2].jumpPower
                elif event.key == pygame.K_LEFT and settings["Player Count"][2] >= 4:
                    playerList[3].vy -= playerList[3].jumpPower
                elif event.key == pygame.K_ESCAPE:
                    gameStarted = not gameStarted
                elif event.key == pygame.K_z:
                    use_ability(playerList[0], playerList[0].ability)
                elif event.key == pygame.K_s and settings["Player Count"][2] >= 2:
                    use_ability(playerList[1], playerList[1].ability)

        for i in range(joysticks_nb):
            horiz_move_0 = joysticks[i].get_axis(0)
            vert_move_0 = joysticks[i].get_axis(1)
            if abs(vert_move_0) > 0.2 or abs(horiz_move_0) > 0.2:
                use_ability(playerList[i], playerList[i].ability)
            for j in range(0,4):
                if joysticks[i].get_buttons(j):
                    playerList[i].vy -= playerList[i].jumpPower
            if joysticks[i].get_buttons(4):
                use_ability(playerList[i], playerList[i].ability)
            if joysticks[i].get_buttons(5):
                gameStarted = not gameStarted
            if joysticks[i].get_hat(0)[1] == 1 or joysticks[i].get_hat(0)[1] == -1 or joysticks[i].get_hat(0)[0] == 1 or joysticks[i].get_hat(0)[0] == -1:
                use_ability(playerList[i], playerList[i].ability)

        for player in playerList:
            player.physics_update(dt)

        newObstacleList = []
        for obstacle in obstacleList:
            dx = -int(gameSpeed * dt * 60)
            obstacle.move(dx)

            availablePoints = playersAlive * (settings["Difficulty"][3] + 1)
            top, bottom = obstacle.top, obstacle.bottom

            for player in playerList:
                if player.alive:
                    if not obstacle.gavePoint and top.x <= player.rect.x:
                        obstacle.gavePoint = True
                        score += availablePoints
                        scoreText = render_score(score)
                    if top.colliderect(player.rect) or bottom.colliderect(player.rect):
                        player.alive = False
                        playersAlive = 0
                        for player in playerList:
                            if player.alive == True:
                                playersAlive += 1
                        if playersAlive == 0:
                            gameStarted = False
                            gameInit = False
                            previousScore = score
                            if score > best_score:
                                choosingName = True

            if top.x + top.width > 0:
                newObstacleList.append(obstacle)

        for laser in laserList:
            laser.update(dt)
            for obstacle in obstacleList:
                if laser.rect.colliderect(obstacle.top) or laser.rect.colliderect(obstacle.bottom):
                    newObstacleList.remove(obstacle)
            if laser.lifetime <= 0:
                laserList.remove(laser)
        
        if clouds:
            for cloud in cloudList:
                cloud.update(dt)

        obstacleList = newObstacleList

        if gameSpeed < 10 * (2 - gameVariables["gameSpeedMax"]):
            gameSpeed = score // 8 + 5

        if obstacleList == [] or obstacleList[-1].top.x < WIDTH - currentSpacing:
            create_obstacle()
            currentSpacing = randint(max(int(250 * gameVariables["spacing"]), int((300 - score//2) * gameVariables["spacing"])), max(int(400 * gameVariables["spacing"]), int((600 - score) * gameVariables["spacing"]))) + 65

        screen.fill(colors["CoolerBlue"])
        if settings["Background"][2] == "On":
            background_x += int(gameSpeed * dt * 60)
            background_x = background_x % WIDTH
            screen.blit(assets["Background"], (-background_x, 0))
            screen.blit(assets["Background"], (WIDTH - background_x, 0))

        for obstacle in obstacleList:
            top, bottom = obstacle.top, obstacle.bottom
            screen.blit(obstacle.top_surf, top)
            screen.blit(obstacle.bottom_surf, bottom)
            screen.blit(obstacle.top_cap, (top.x + 2, top.y + HEIGHT - 25))
            screen.blit(obstacle.bottom_cap, (bottom.x + 2, bottom.y))

        if clouds:
            for cloud in cloudList:
                screen.blit(assets["Cloud"], cloud.rect)

        for player in playerList:
            if player.alive:
                #pygame.draw.rect(screen, colors["Red"], player.rect)
                screen.blit(player.sprite, player.rect)
                pygame.draw.rect(screen, colors["White"], (WIDTH - 75 * player.number - 3, HEIGHT - 103, 56, 56))
                screen.blit(assets[f"{abilitiesList[player.ability]}Icon"], (WIDTH - 75 * player.number, HEIGHT - 100))
                pygame.draw.rect(screen, colors["Gray"], (WIDTH - 75 * player.number, HEIGHT - 100, 50, 50 * (player.coolDown / abilitiesCoolDown[player.ability])))
                if settings["Player Count"][2] > 1:
                    ptext = comicSans.render(f"P{player.number}", False, colors[colorList[player.color]])
                    screen.blit(ptext, (player.rect.x + player.rect.width//4, player.rect.y - comicSans.get_height()))

        for laser in laserList:
            #pygame.draw.rect(screen, colors["Red"], laser.rect)
            screen.blit(assets["Laser"], laser.rect)

        screen.blit(scoreText, (25, 25))
        pygame.display.flip()

    else:
        if not gameInit and not choosingName:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_RIGHT:
                        keyRightMenu()
                    
                    elif event.key == pygame.K_LEFT:
                        keyLeftMenu()
                    
                    elif event.key == pygame.K_DOWN:
                       keyDownMenu()
                    
                    elif event.key == pygame.K_UP:
                        keyUpMenu()
                    
                    elif event.key == pygame.K_TAB:
                        
                        if menuList[currentMenu] == "Colors" or menuList[currentMenu] == "Skins" or menuList[currentMenu] == "Abilities":
                            if currentSelection < settings["Player Count"][2] - 1:
                                currentSelection += 1
                            else:
                                currentSelection = 0
                            colorSpecialText = comicSans.render(f"Current player selection : P{currentSelection + 1}", False, colors["White"])
                            menusTexts["ColorsTexts"][2] = comicSans.render(f"Current color : {colorList[playerList[currentSelection].color]}", False, colors["White"])
                        
                        elif menuList[currentMenu] == "Settings":
                            changedSetting = settingsList[currentSetting]
                            settings[changedSetting][1] = "White"
                            settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                            if currentSetting < len(settingsList) - 1:
                                currentSetting += 1
                            else:
                                currentSetting = 0
                            changedSetting = settingsList[currentSetting]
                            settings[changedSetting][1] = "Red"
                            settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                        
                        elif menuList[currentMenu] == "Stats":
                            stats[statsList[currentStat]][1] = "White"
                            if currentStat < len(statsList) - 1:
                                currentStat += 1
                            else:
                                currentStat = 0
                            stats[statsList[currentStat]][1] = "Red"

            for i in range(joysticks_nb):
                horiz_move_0 = joysticks[i].get_axis(0)
                vert_move_0 = joysticks[i].get_axis(1)
                if vert_move_0 > 0.2:
                    keyUpMenu()

                elif vert_move_0 < -0.2:
                    keyDownMenu()
                
                if horiz_move_0 > 0.2:
                    keyRightMenu()
                
                elif horiz_move_0 < -0.2:
                    keyDownMenu()

                for j in range(4):
                    if joysticks[i].get_buttons(j):
                        if j == 0:
                            keyUpMenu()
                        elif j == 1:
                            keyDownMenu()
                        elif j == 2:
                            keyLeftMenu()
                        elif j == 3:
                            keyRightMenu()
                    
                if joysticks[i].get_buttons(4):
                    if menuList[currentMenu] == "Settings":
                        changedSetting = settingsList[currentSetting]
                        settings[changedSetting][1] = "White"
                        settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                        if currentSetting < len(settingsList) - 1:
                            currentSetting += 1
                        else:
                            currentSetting = 0
                        changedSetting = settingsList[currentSetting]
                        settings[changedSetting][1] = "Red"
                        settings[changedSetting][0] = comicSans.render(f"{changedSetting} : {settings[changedSetting][2]}", False, colors[settings[changedSetting][1]])
                        
                    elif menuList[currentMenu] == "Stats":
                        stats[statsList[currentStat]][1] = "White"
                        if currentStat < len(statsList) - 1:
                            currentStat += 1
                        else:
                            currentStat = 0
                        stats[statsList[currentStat]][1] = "Red"
                
                if joysticks[i].get_buttons(5):
                    if menuList[currentMenu] == "Colors" or menuList[currentMenu] == "Skins" or menuList[currentMenu] == "Abilities" or menuList[currentMenu] == "Stats":
                        if currentSelection < settings["Player Count"][2] - 1:
                            currentSelection += 1
                        else:
                            currentSelection = 0
                        colorSpecialText = comicSans.render(f"Current player selection : P{currentSelection + 1}", False, colors["White"])
                        menusTexts["ColorsTexts"][2] = comicSans.render(f"Current color : {colorList[playerList[currentSelection].color]}", False, colors["White"])
                
                if joysticks[i].get_hat(0)[1] == 1:           # On appuie sur la touche HAUT
                    keyUpMenu()
                if joysticks[i].get_hat(0)[1] == -1:          # On appuie sur la touche BAS
                    keyDownMenu()
                if joysticks[i].get_hat(0)[0] == 1:           # On appuie sur la touche DROITE
                    keyRightMenu()
                if joysticks[i].get_hat(0)[0] == -1:          # On appuie sur la touche GAUCHE
                    keyLeftMenu()
            
            screen.blit(menuText, (WIDTH//2 - menuText.get_width()//2, HEIGHT//2 - menuText.get_height()//2 - 200))
           
            pygame.draw.polygon(screen, colors["White"], [[WIDTH//2 - menuText.get_width()//2 - 50, HEIGHT//2 - 200], [WIDTH//2 - menuText.get_width()//2 - 25, HEIGHT//2 - 175], [WIDTH//2 - menuText.get_width()//2 - 25, HEIGHT//2 - 225]], 0)
            pygame.draw.polygon(screen, colors["White"], [[WIDTH//2 + menuText.get_width()//2 + 50, HEIGHT//2 - 200], [WIDTH//2 + menuText.get_width()//2 + 25, HEIGHT//2 - 175], [WIDTH//2 + menuText.get_width()//2 + 25, HEIGHT//2 - 225]], 0)

            for i, v in enumerate(menusTexts[f"{menuList[currentMenu]}Texts"].values()):
                screen.blit(v, (WIDTH//2 - v.get_width()//2, HEIGHT//2 - v.get_height()//2 - 100 + menusOffset[menuList[currentMenu]] + i * 40))
           
            if menuList[currentMenu] == "Colors" or menuList[currentMenu] == "Skins" or menuList[currentMenu] == "Abilities" or menuList[currentMenu] == "Stats":
                if settings["Player Count"][2] > 1:
                    screen.blit(colorSpecialText, (WIDTH//2 - colorSpecialText.get_width()//2, HEIGHT//2 - colorSpecialText.get_height()//2 - 20))

            if menuList[currentMenu] == "Colors" or menuList[currentMenu] == "Skins":
                screen.blit(assets[f"{skinList[playerList[currentSelection].skin]}{colorList[playerList[currentSelection].color]}"], (WIDTH//2 - 25, HEIGHT//2 + 100))
            
            elif menuList[currentMenu] == "Stats":
                for i, stat in enumerate(statsList):
                    statText = comicSans.render(f"{stat} : {getattr(playerList[currentSelection], stats[stat][2])}", False, colors[stats[stat][1]])
                    screen.blit(statText, (WIDTH//2 - statText.get_width()//2, HEIGHT//2 - statText.get_height()//2 + i * 50 + 75))
            
            elif menuList[currentMenu] == "Settings":
                for i, setting in enumerate(settingsList):
                    screen.blit(settings[setting][0], (WIDTH//2 - settings[setting][0].get_width()//2, HEIGHT//2 - settings[setting][0].get_height()//2 + i * 50))

            elif menuList[currentMenu] == "Abilities":
                #pygame.draw.rect(screen, colors["White"], (WIDTH//2 - assets[f"{abilitiesList[playerList[currentSelection].ability]}Icon"].get_width()//2 - 3, HEIGHT + 103, 56, 56))
                screen.blit(assets[f"{abilitiesList[playerList[currentSelection].ability]}Icon"], (WIDTH//2 - assets[f"{abilitiesList[playerList[currentSelection].ability]}Icon"].get_width()//2, HEIGHT//2 + 100))
        
        elif not choosingName:
            for event in pygame.event.get():   
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        gameStarted = not gameStarted 

            screen.blit(pauseText, (WIDTH//2 - pauseText.get_width()//2, HEIGHT//2 - pauseText.get_height()//2))

        else:
            for event in pygame.event.get():   
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        badwordfound = False
                        for word in bad_words:
                            if "".join(chosenLetters).lower() == word:
                                chosenLetters = ["_", "_", "_"]
                                currentLetterIndex = 0
                                currentLetter = 0
                                badwordfound = True
                                break
                        if not badwordfound:
                            found = False
                            previous_data = data.copy()
                            for i in range(0, 10):
                                if previousScore > best_scores[i] and not found:
                                    best_scores.insert(i, previousScore)
                                    best_scores.pop()
                                    data[str(i + 1)] = {"playerName": "".join(chosenLetters), "score": previousScore}
                                    best_score = best_scores[-1]
                                    found = True
                                elif found and i < 10:
                                    data[str(i + 1)] = previous_data[str(i)]
                            updateLeaderboard()
                            choosingName = False
                    if event.key == pygame.K_DOWN:
                        currentLetterIndex = (currentLetterIndex - 1) % len(letterList)
                        chosenLetters[currentLetter] = letterList[currentLetterIndex]
                    if event.key == pygame.K_UP:
                        currentLetterIndex = (currentLetterIndex + 1) % len(letterList)
                        chosenLetters[currentLetter] = letterList[currentLetterIndex]
                    if event.key == pygame.K_TAB:
                        if currentLetter < 2:
                            currentLetter += 1
                            currentLetterIndex = letterList.index(chosenLetters[currentLetter])
                        else:
                            currentLetter = 0
                            currentLetterIndex = letterList.index(chosenLetters[currentLetter])

            underscoreText = comicSans.render("_", False, colors["White"])

            screen.blit(comicSans.render("New High Score!", False, colors["White"]), (WIDTH//2 - comicSans.render("New High Score!", False, colors["White"]).get_width()//2, HEIGHT//2 - 100))
            screen.blit(comicSans.render(f"Your Score: {previousScore}", False, colors["White"]), (WIDTH//2 - comicSans.render(f"Your Score: {previousScore}", False, colors["White"]).get_width()//2, HEIGHT//2 - 50))
            screen.blit(comicSans.render("Enter your name and press a:", False, colors["White"]), (WIDTH//2 - comicSans.render("Enter your name and press a:", False, colors["White"]).get_width()//2, HEIGHT//2))
            for i in range(3):
                if currentLetter == i:
                    screen.blit(comicSans.render(chosenLetters[i], False, colors["Red"]), (WIDTH//2 - underscoreText.get_width()//2 - 25 + i * 25, HEIGHT//2 + 50))
                else:
                    screen.blit(comicSans.render(chosenLetters[i], False, colors["White"]), (WIDTH//2 - underscoreText.get_width()//2 - 25 + i * 25, HEIGHT//2 + 50))

        pygame.display.flip()
        screen.fill(colors["Black"])

    dt = clock.tick(60)/1000
    dt = max(0.001, min(0.1, dt))

pygame.quit()

with open('data/data.json', 'w') as f:
    json.dump(data, f)
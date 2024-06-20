
import pygame, sys, random
from pygame.locals import *

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

BACKGROUND = pygame.image.load('FileGame/img/background-night.png')
BACKGROUND = pygame.transform.scale2x(BACKGROUND)

pygame.init()
FPS = 60

fpsClock = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('Flappy Bird')
GAME_FONT = pygame.font.Font('FileGame/04B_19.TTF',40)

#tạo chim
BIRD_WIDTH = 45
BIRD_HEIGHT = 40
G = 0.5
SPEED_FLY = -8
BIRD_DOWN = pygame.transform.scale(pygame.image.load('FileGame/img/yellowbird-downflap.png'),(BIRD_WIDTH, BIRD_HEIGHT)).convert_alpha()
BIRD_MID = pygame.transform.scale(pygame.image.load('FileGame/img/yellowbird-midflap.png'),(BIRD_WIDTH, BIRD_HEIGHT)).convert_alpha()
BIRD_UP = pygame.transform.scale(pygame.image.load('FileGame/img/yellowbird-upflap.png'),(BIRD_WIDTH, BIRD_HEIGHT)).convert_alpha()

BIRDFLAP = pygame.USEREVENT + 1 #  +1 sự kiện đặc biệt của chim (đập cánh)
pygame.time.set_timer(BIRDFLAP, 300)#200 miligiay

#tạo cột
COLUMN_WIDTH = 50
COLUMN_HEIGHT = 500
BLANK = 160
DISTANCE = 200
COLUMN_SPEED = 2
COLUMN_IMG = pygame.image.load('FileGame/img/column.png')

#tạo sàn
FLOOR_IMG = pygame.image.load('FileGame/img/floor.png')
FLOOR_IMG = pygame.transform.scale2x(FLOOR_IMG)

#tạo màn hình kết thúc
GAME_OVER_SURFACE = pygame.transform.scale(pygame.image.load('FileGame/img/message.png'),(200,330))
GAME_OVER_RECT = GAME_OVER_SURFACE.get_rect(center = (200,260))

#chèn âm thanh
flap_sound = pygame.mixer.Sound('FileGame/sound/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('FileGame/sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('FileGame/sound/sfx_point.wav')

#xoay chim
def rotate_bird(bird1):
    new_bird = pygame.transform.rotozoom(bird1.bird,-bird1.speed*3,1) #rotozoom: hiệu ứng xoay chim
    return new_bird
class Bird():
    def __init__(self):
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.x = (WINDOW_WIDTH - self.width) / 2 #bird khởi tạo giữa màn hình
        self.y = (WINDOW_HEIGHT - self.height) / 2
        self.speed = 0
        self.suface_down = BIRD_DOWN
        self.suface_mid = BIRD_MID
        self.suface_up = BIRD_UP
        self.list = [BIRD_DOWN, BIRD_MID, BIRD_UP]
        self.index = 0
        self.bird = self.list[self.index]

    def draw(self):
        rotated_bird = rotate_bird(self)  # tạo hệu ứng để chim cúi lên cúi xuống
        SCREEN.blit(rotated_bird, (int(self.x), int(self.y)))

    def update(self, mouseClick):
        self.y += self.speed + 0.5 * G
        self.speed += G
        if mouseClick == True:
            self.speed = SPEED_FLY
            flap_sound.play()

class Columns():
    def __init__(self):
        self.width = COLUMN_WIDTH
        self.height = COLUMN_HEIGHT #chiều cao max của ống
        self.blank = BLANK #khoảng cách giữa ống trên và ống dưới
        self.distance = DISTANCE #khoảng cách giữa 2 ống
        self.speed = COLUMN_SPEED
        self.surface = COLUMN_IMG
        self.ls = [] #list: danh sách tọa độ 3 ống (x,y)
        for i in range(3):
            x = WINDOW_WIDTH + i * self.distance #tọa độ x các ống lần lượt: 400, 600, 800 (mỗi ống cách nhau: distance(200))
            y = random.randrange(60, WINDOW_HEIGHT - self.blank - 60, 20) #(60, 380, 20)
            self.ls.append([x, y])

    def draw(self):
        for i in range(3):
            SCREEN.blit(self.surface, (self.ls[i][0], self.ls[i][1] - self.height)) #ống trên (ra âm)
            SCREEN.blit(self.surface, (self.ls[i][0], self.ls[i][1] + self.blank)) #ống dưới

    def update(self):
        for i in range(3):
            self.ls[i][0] -= self.speed #ống di chuyển sang trái (giảm x)

        if self.ls[0][0] < -self.width: #ống thứ 1 nối tiếp ống thứ 3
            self.ls.pop(0) #xóa ống 1 -> tọa độ x của: (ống 2: [0,0] và ống 3: [1,0])
            #tạo ống mới (lấy ống cuối cùng + khoảng cách giữa 2 ống)
            x = self.ls[1][0] + self.distance
            y = random.randrange(60, WINDOW_HEIGHT - self.blank - 60, 10)
            self.ls.append([x, y])

#kiểm tra va chạm (true: chim chạm ống)
def rectCollision(rect1, rect2):
    if rect1[0] <= rect2[0] + rect2[2] and rect2[0] <= rect1[0] + rect1[2] and rect1[1] <= rect2[1] + rect2[3] and \
            rect2[1] <= rect1[1] + rect1[3]:
        return True
    return False

#true: gameover
def isGameOver(bird, columns, floor):
    for i in range(3):
        rectBird = [bird.x, bird.y, bird.width, bird.height]
        rectColumn1 = [columns.ls[i][0], columns.ls[i][1] - columns.height, columns.width, columns.height] #ống trên(y: âm)
        rectColumn2 = [columns.ls[i][0], columns.ls[i][1] + columns.blank, columns.width, columns.height] #ống dưới
        if rectCollision(rectBird, rectColumn1) == True or rectCollision(rectBird, rectColumn2) == True:
            hit_sound.play()
            return True
    if bird.y+ bird.height < 0 or bird.y + bird.height > floor.floor_y_pos:#nếu chim bay quá màn hình or rớt xuống sàn
        return True
    return False

class Floor():
    def __init__(self):
        self.surface = FLOOR_IMG
        self.floor_x_pos = 0
        self.floor_y_pos = 550

    def draw(self):
        SCREEN.blit(self.surface, (self.floor_x_pos, self.floor_y_pos))  # sàn thứ 1
        SCREEN.blit(self.surface, (self.floor_x_pos + 200, self.floor_y_pos))  # cái sàn thứ 2 nối tiếp sàn thứ 1, chiều dài sàn = 200

    def update(self):
        self.floor_x_pos -= 1  # lùi về trái
        # để sàn thứ 1 nối lên sàn thứ 2, 2 cái sàn cứ thay đổi vị trí cho nhau (do sàn di chuyển ko theo kịp con chim)
        if self.floor_x_pos <= -432:
            self.floor_x_pos = 0

class Score():
    def __init__(self, high_score=0):
        self.score = 0
        self.addScore = True #trạng thái đã add điểm hay chưa
        self.high_score = high_score

    def draw(self):
        scoreSuface = GAME_FONT.render(str(self.score), True, (255, 255, 255))
        textSize = scoreSuface.get_size()
        SCREEN.blit(scoreSuface, (int((WINDOW_WIDTH - textSize[0]) / 2), 100))

    def update(self, bird, columns):
        collision = False
        for i in range(3):
            if columns.ls[i][0]+columns.width <= bird.x:
                collision = True
                break
        if collision == True:
            if self.addScore == True:
                self.score += 1
                score_sound.play()
            self.addScore = False  # đã add điểm
        else:
            self.addScore = True

    def update_highscore(self):
        if self.score > self.high_score:
            self.high_score = self.score
        return self.high_score

#màn hình bắt đầu
def gameStart(bird, floor):
    bird.__init__()
    floor.__init__()

    headingSuface = GAME_FONT.render('FLAPPY BIRD', True, (255, 255, 255)) # đỏ: (255, 0, 0)
    headingSuface_rect = headingSuface.get_rect(center=(200, 140))

    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Click to start', True, (0, 0, 0))
    commentSuface_rect = commentSuface.get_rect(center=(200, 500))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return

        SCREEN.blit(BACKGROUND, (0, 0))
        floor.draw()
        bird.draw()
        SCREEN.blit(headingSuface, headingSuface_rect)
        SCREEN.blit(commentSuface, commentSuface_rect)

        pygame.display.update()
        fpsClock.tick(FPS)

#hiệu ứng đập cánh
def bird_animation(bird):
    new_bird = bird.list[bird.index]
    return new_bird
def gamePlay(bird, columns, floor, score):
    bird.__init__()
    bird.speed = SPEED_FLY
    columns.__init__()
    floor.__init__()
    score.__init__(score.high_score) #nếu không để high_core sẽ set=0
    while True:
        mouseClick = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:

                mouseClick = True
            if event.type == BIRDFLAP:
                if bird.index < 2:
                    bird.index += 1
                else:
                    bird.index = 0
                bird.bird = bird_animation(bird)  # hàm tạ hiệu ứng đập cánh cho chim

        SCREEN.blit(BACKGROUND, (0, 0))
        columns.draw()
        columns.update()
        bird.draw()
        bird.update(mouseClick) #mouseClick = true: có click chuột, update lại vị trí bird
        score.draw()
        score.update(bird, columns)
        floor.draw()
        floor.update()

        if isGameOver(bird, columns, floor) == True:
            return
        pygame.display.update()
        fpsClock.tick(FPS)


def gameOver(bird, columns, floor, score):

    score.high_score = score.update_highscore()

    score_surface = GAME_FONT.render(f'Score: {int(score.score)}', True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(200, 50))

    high_score_surface = GAME_FONT.render(f'High Score: {int(score.high_score)}', True, (255, 255, 255))
    high_score_rect = high_score_surface.get_rect(center=(200, 460))

    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Press "space" to replay', True, (0, 0, 0))
    commentSuface_rect = commentSuface.get_rect(center=(200, 520))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    return

        SCREEN.blit(BACKGROUND, (0, 0))
        #columns.draw()
        floor.draw()
        floor.update()
        #bird.draw()

        SCREEN.blit(GAME_OVER_SURFACE, GAME_OVER_RECT)
        SCREEN.blit(score_surface, score_rect)
        SCREEN.blit(high_score_surface, high_score_rect)
        SCREEN.blit(commentSuface, commentSuface_rect)

        pygame.display.update()
        fpsClock.tick(FPS)


def main():
    bird = Bird()
    columns = Columns()
    floor = Floor()
    score = Score()

    while True:
        gameStart(bird, floor)
        gamePlay(bird, columns, floor,score)
        gameOver(bird, columns, floor,score)


if __name__ == '__main__':
    main()
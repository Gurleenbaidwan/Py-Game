import pygame
import random
import os
# from spritesheet import SpriteSheet
# from enemy import Enemy

pygame.init()  # initialize pygame
# game window dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# main game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BLOB GAME')

# setting framerate to slow down the game
clock = pygame.time.Clock()
FPS = 60

# game variables
SCROLL_THRESH = 200
scroll = 0
GRAVITY = 1
MAX_PLATFORMS = 10
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.text'):   # we are checking if the file already exists
    with open('score.text', 'r') as file:  # open that file and read the score
        high_score = int(file.read())
else:
    high_score = 0

# define font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

# images
jumpy_image = pygame.image.load('blob.png').convert_alpha()
bg = pygame.image.load('bg-2.png').convert_alpha()
platform_image = pygame.image.load('wood.png').convert_alpha()
# bird spritesheet
bird_sheet_img = pygame.image.load('bird.png').convert_alpha()
# bird_sheet = SpriteSheet(bird_sheet_img)

# function for outputting text onto the screen


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# function for drawing the info panel


def draw_panel():
    pygame.draw.rect(screen, (153, 217, 234), (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, "white", (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE:' + str(score), font_small, "white", 0, 0)


def draw_bg(bg_scroll):  # fxn for drawing the background
    screen.blit(bg, (0, 0 + bg_scroll))
    screen.blit(bg, (0, -600 + bg_scroll))


class Player():  # player class
    def __init__(self, x, y):
        self.image = pygame.transform.scale(
            jumpy_image, (45, 45))  # to increse the size of blob
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0  # velocity in y direction
        self.flip = False

    def move(self):
        # reset variables
        scroll = 0
        dx = 0  # d = delta(change)
        dy = 0  # made to control the position of rect

        # keyboard setup for presses
        key = pygame.key.get_pressed()  # keys that are going to be pressed
        if key[pygame.K_a]:  # -x for left
            dx = -10
            self.flip = True  # can also slow down the speed of the blob by making the rect slow
        if key[pygame.K_d]:  # +x for right
            dx = 10
            self.flip = False

        # gravity
        # as the variable goes higher and higher it also increases(constantly increasing by gravity)
        self.vel_y += GRAVITY
        dy += self.vel_y  # dy is increased by gravity

        # ensure player doesn't go off the edge screen
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # check collision with the platform
        for platform in platform_group:
            # collisoin in the y-direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if above the platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:  # -ve num means falling
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20

        # check collision with the ground
        # if self.rect.bottom + dy > SCREEN_HEIGHT:
        #     dy = 0
        #     self.vel_y = -20  # to stop the player from going down the screen and start jumping

        # check if the player has bounced to the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            # if player is jumping
            if self.vel_y < 0:
                scroll = -dy

        # update rectangles position
        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip,
                    False), (self.rect.x - 12, self.rect.y - 5))
        # this to draw the rect around the blob with the 2 border
        pygame.draw.rect(screen, "white", self.rect, 2)


class Platform (pygame.sprite.Sprite):  # inheritance
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x  # coordinates
        self.rect.y = y

    def update(self, scroll):
        # update platform's vertical position
        self.rect.y += scroll
        # check if the platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# player instance
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)  # (x,y)

# create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
platform_group.add(platform)

# game loop
run = True
while run:
    clock.tick(FPS)  # framerate
    if game_over == False:
        scroll = jumpy.move()

        # draw background
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        # generate platforms
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            platform = Platform(p_x, p_y, p_w)
            platform_group.add(platform)

        # update platforms
        platform_group.update(scroll)

        # generate enemies
        # if len(enemy_group) == 0:  # if there is no enemy in the group then create it
        #     enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
        #     enemy_group.add(enemy)

        # update enemies-
        enemy_group.update(scroll, SCREEN_WIDTH)

        # update score
        if scroll > 0:
            score += scroll

        # draw line at previous high score (it will come as high score )
        pygame.draw.line(screen, "white", (0, score - high_score + SCROLL_THRESH),
                         (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, "white", SCREEN_WIDTH -
                  130, score - high_score + SCROLL_THRESH)

        # draw sprites -
        platform_group.draw(screen)
        enemy_group.draw(screen)
        jumpy.draw()

        # draw panel
        draw_panel()

        # check game over
        if jumpy.rect .top > SCREEN_HEIGHT:
            game_over = True

    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(
                    screen, "black", (0, y * 100, fade_counter, 100))
                pygame.draw.rect(
                    screen, "black", (SCREEN_WIDTH - fade_counter, (y+1) * 100, SCREEN_WIDTH, 100))
        else:  # to make the fade counter appear after the fade counter comes
            draw_text('GAME OVER', font_big, "white", 130, 200)
            draw_text('SCORE:' + str(score), font_big, "white", 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, "white", 40, 300)
            # update the high score
            if score > high_score:  # if u dont have high score it will some to this section to update write ur score on the file
                high_score = score
                with open('score.text', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # reset variables
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                # reposition jumpy
                jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                # reset platforms
                platform_group.empty()
                # create starting platform
                platform = Platform(SCREEN_WIDTH // 2 - 50,
                                    SCREEN_HEIGHT - 50, 100)
                platform_group.add(platform)

    # event handler - to make the game working
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # update the high score
            if score > high_score:  # if u dont have high score it will some to this section to update write ur score on the file
                high_score = score
                with open('score.text', 'w') as file:
                    file.write(str(high_score))
            run = False

    pygame.display.update()  # alwayz update the game changes made by us
pygame.quit()

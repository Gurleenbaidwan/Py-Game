import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

mixer.init()
pygame.init()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BLOB GAME')

clock = pygame.time.Clock()
FPS = 60

pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0, 0)
jump_fx = pygame.mixer.Sound('jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('death.mp3')
death_fx.set_volume(0.5)

SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.text'):
    with open('score.text', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

font_small = pygame.font.Font('Pixeltype.ttf', 27)
font_big = pygame.font.Font('Pixeltype.ttf', 35)

jumpy_image = pygame.image.load('blob.png').convert_alpha()
bg = pygame.image.load('bg-2.png').convert_alpha()
platform_image = pygame.image.load('wood.png').convert_alpha()
bird_sheet_img = pygame.image.load('bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_panel():
    pygame.draw.rect(screen, (153, 217, 234), (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, "white", (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE:' + str(score // 50), font_small, "black", 0, 0)


def draw_bg(bg_scroll):
    screen.blit(bg, (0, 0 + bg_scroll))
    screen.blit(bg, (0, -600 + bg_scroll))


class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        scroll = 0
        dx = 0
        dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            dx = 10
            self.flip = False

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()

        if self.rect.top <= SCROLL_THRESH:
            if self.vel_y < 0:
                scroll = -dy
        self.rect.x += dx
        self.rect.y += dy + scroll
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip,
                    False), (self.rect.x - 12, self.rect.y - 5))


class Platform (pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        self.rect.y += scroll
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
platform_group.add(platform)

run = True
while run:
    clock.tick(FPS)
    if game_over == False:
        scroll = jumpy.move()
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            platform = Platform(p_x, p_y, p_w)
            platform_group.add(platform)

        platform_group.update(scroll)
        if len(enemy_group) == 0 and score > 1500:
            enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)

        enemy_group.update(scroll, SCREEN_WIDTH)
        if scroll > 0:
            score += scroll

        pygame.draw.line(screen, "white", (0, score - high_score + SCROLL_THRESH),
                         (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, "white", SCREEN_WIDTH -
                  130, score - high_score + SCROLL_THRESH)

        platform_group.draw(screen)
        enemy_group.draw(screen)
        jumpy.draw()

        draw_panel()

        if jumpy.rect .top > SCREEN_HEIGHT:
            game_over = True
            death_fx.play()

        if pygame.sprite.spritecollide(jumpy, enemy_group, False):
            if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(
                    screen, "black", (0, y * 100, fade_counter, 100))
                pygame.draw.rect(
                    screen, "black", (SCREEN_WIDTH - fade_counter, (y+1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text('GAME OVER', font_big, (111, 196, 169), 138, 200)
            draw_text('SCORE:' + str(score // 50),
                      font_big, (111, 196, 169), 145, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN',
                      font_big, (111, 196, 169), 48, 300)
            if score > high_score:
                high_score = score
                with open('score.text', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                enemy_group.empty()
                platform_group.empty()
                platform = Platform(SCREEN_WIDTH // 2 - 50,
                                    SCREEN_HEIGHT - 50, 100)
                platform_group.add(platform)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if score > high_score:
                high_score = score
                with open('score.text', 'w') as file:
                    file.write(str(high_score))
            run = False

    pygame.display.update()
pygame.quit()

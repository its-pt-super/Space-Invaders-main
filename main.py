import cv2
import mediapipe as mp
import pygame
import sys
import random
import math
from pygame import mixer

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("ufo.png")
pygame.display.set_icon(icon)

background = pygame.image.load("Back.jpg")
mixer.music.load("background.wav")
mixer.music.play(-1)

playerimg = pygame.image.load("player.png")
player_width = 100
player_height = 150
playerX = width // 2 - player_width // 2
playerY = 430

enemyimg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyimg.append(pygame.image.load("enemy.png"))
    enemyX.append(random.randint(0, 600))
    enemyY.append(random.randint(0, 200))
    enemyX_change.append(4)
    enemyY_change.append(40)

bulletimg = pygame.image.load("bullet.png")
bulletX = 0
bulletY = 450
bulletY_change = 30
bullet_state = "ready"

score_value = 0
font = pygame.font.Font("freesansbold.ttf", 32)
textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (150, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (200, 250))

def player(x, y):
    screen.blit(playerimg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyimg[i], (enemyX[i], enemyY[i]))

def draw_bullet(x, y):
    screen.blit(bulletimg, (x, y))

def incollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    return distance < 35

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Replay button setup
replay_button_rect = pygame.Rect(width // 2 - 75, height // 2 + 24, 150, 40)
replay_font = pygame.font.Font('freesansbold.ttf', 32)

# Pause button setup
pause_button_rect = pygame.Rect(700, 0, 150, 40)
pause_font = pygame.font.Font('freesansbold.ttf', 32)

game_over = False
paused = False

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if replay_button_rect.collidepoint(mouse_x, mouse_y) and game_over:
                # Reset the game
                game_over = False
                paused = False
                score_value = 0
                for i in range(num_of_enemies):
                    enemyX[i] = random.randint(0, 600)
                    enemyY[i] = random.randint(0, 200)
            elif pause_button_rect.collidepoint(mouse_x, mouse_y) and not game_over:
                paused = not paused  # Toggle pause state

    if not paused:
        # Capture video from the camera
        ret, frame = cap.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            hand_center_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * width)
            playerX = width - (hand_center_x + player_width // 2)

        # Draw the background
        screen.fill((0, 255, 255))
        screen.blit(background, (0, 0))

        # Draw enemies
        for i in range(num_of_enemies):
            if enemyY[i] > 400 and enemyX[i] > 200:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000
                game_over_text()
                game_over = True  # Set game over state
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 8
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 740:
                enemyX_change[i] = -8
                enemyY[i] += enemyY_change[i]
            collision = incollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = 450
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 800)
                enemyY[i] = random.randint(0, 200)

            enemy(enemyX[i], enemyY[i], i)

        # Draw the player
        player(playerX, playerY)

        # Draw the bullet
        if bullet_state == "fire":
            draw_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        # Fire bullet when hand is open
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            is_hand_open = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            if is_hand_open:
                if bullet_state == "ready":
                    bulletX = playerX
                    bulletY = playerY-40
                    bullet_state = "fire"
            else:
                bullet_state = "ready"  # Reset bullet state when hand is not open

        # Draw the score
        show_score(textX, textY)

        # Draw replay button when the game is over
        if game_over:
            pygame.draw.rect(screen, (0, 255, 0), replay_button_rect)
            replay_text = replay_font.render("Replay", True, (0, 0, 0))
            screen.blit(replay_text, (width // 2 - 58, height // 2 + 30))

        # Draw pause button
        pygame.draw.rect(screen, (255, 55, 25), pause_button_rect)
        pause_text = pause_font.render("Pause", True, (0, 0, 0))
        screen.blit(pause_text, (700,0))

    pygame.display.update()

pygame.quit()
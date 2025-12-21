import cv2
import mediapipe as mp
import pygame
import sys

# -------------------- PYGAME INIT --------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Gesture Pong")

clock = pygame.time.Clock()
FPS = 60

# -------------------- CONSTANTS --------------------
BALL_SPEED = 5
PADDLE_SPEED = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -------------------- GAME OBJECTS --------------------
ball = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 30, 30)
ball_speed_x = BALL_SPEED
ball_speed_y = BALL_SPEED

paddle1 = pygame.Rect(50, HEIGHT // 2 - 60, 10, 120)
paddle2 = pygame.Rect(WIDTH - 60, HEIGHT // 2 - 60, 10, 120)

score1 = 0
score2 = 0

font = pygame.font.Font(None, 36)

# -------------------- MEDIAPIPE INIT --------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# -------------------- CAMERA INIT --------------------
cap = cv2.VideoCapture(0)

# -------------------- MAIN LOOP --------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    screen.fill(BLACK)

    # Convert to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # -------------------- HAND TRACKING --------------------
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger = hand_landmarks.landmark[8]
            x = int(index_finger.x * WIDTH)
            y = int(index_finger.y * HEIGHT)

            if x < WIDTH // 2:
                paddle1.centery = y
            else:
                paddle2.centery = y

    # Clamp paddles inside screen
    paddle1.top = max(paddle1.top, 0)
    paddle1.bottom = min(paddle1.bottom, HEIGHT)
    paddle2.top = max(paddle2.top, 0)
    paddle2.bottom = min(paddle2.bottom, HEIGHT)

    # -------------------- BALL MOVEMENT --------------------
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Wall collision
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Paddle collision
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_speed_x *= -1

    # Scoring
    if ball.left <= 0:
        score2 += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED

    if ball.right >= WIDTH:
        score1 += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = -BALL_SPEED

    # -------------------- DRAW --------------------
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)

    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    pygame.display.update()

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()

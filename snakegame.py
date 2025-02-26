import pygame
import random
import time

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen dimensions
WIDTH = 600
HEIGHT = 400

# Snake and food settings
CELL_SIZE = 20
SPEED = 15

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

def game_loop():
    # Initial snake position and properties
    snake = [[WIDTH//2, HEIGHT//2]]
    dx = CELL_SIZE
    dy = 0
    food = None
    score = 0

    def create_food():
        while True:
            x = random.randrange(0, WIDTH, CELL_SIZE)
            y = random.randrange(0, HEIGHT, CELL_SIZE)
            if [x, y] not in snake:
                return [x, y]

    food = create_food()

    game_over = False

    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx != CELL_SIZE:
                    dx = -CELL_SIZE
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx != -CELL_SIZE:
                    dx = CELL_SIZE
                    dy = 0
                elif event.key == pygame.K_UP and dy != CELL_SIZE:
                    dy = -CELL_SIZE
                    dx = 0
                elif event.key == pygame.K_DOWN and dy != -CELL_SIZE:
                    dy = CELL_SIZE
                    dx = 0

        # Move snake
        new_head = [snake[0][0] + dx, snake[0][1] + dy]
        
        # Check boundaries collision
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            game_over = True
        
        # Check self collision
        if new_head in snake:
            game_over = True

        snake.insert(0, new_head)

        # Check food collision
        if snake[0] == food:
            score += 1
            food = create_food()
        else:
            snake.pop()

        # Drawing
        screen.fill(BLACK)
        
        # Draw snake
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Draw food
        pygame.draw.rect(screen, RED,
                        (food[0], food[1], CELL_SIZE, CELL_SIZE))
        
        # Display score
        font = pygame.font.SysFont(None, 35)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.update()
        clock.tick(SPEED)

    # Game Over message
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 50)
    text = font.render(f"Game Over! Score: {score}", True, RED)
    screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 25))
    text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 + 25))
    pygame.display.update()

    # Wait for restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

# Start the game
game_loop()
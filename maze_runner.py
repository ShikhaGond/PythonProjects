import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 40
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner")

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE

        if self.walls['top']:
            pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls['right']:
            pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls['bottom']:
            pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 2)
        if self.walls['left']:
            pygame.draw.line(screen, BLACK, (x, y + CELL_SIZE), (x, y), 2)

        if self.visited:
            pygame.draw.rect(screen, WHITE, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))

def generate_maze():
    grid = [[Cell(x, y) for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]
    stack = []
    current = grid[0][0]
    current.visited = True

    while True:
        neighbors = []
        if current.x > 0 and not grid[current.x - 1][current.y].visited:
            neighbors.append(grid[current.x - 1][current.y])
        if current.x < GRID_WIDTH - 1 and not grid[current.x + 1][current.y].visited:
            neighbors.append(grid[current.x + 1][current.y])
        if current.y > 0 and not grid[current.x][current.y - 1].visited:
            neighbors.append(grid[current.x][current.y - 1])
        if current.y < GRID_HEIGHT - 1 and not grid[current.x][current.y + 1].visited:
            neighbors.append(grid[current.x][current.y + 1])

        if neighbors:
            next_cell = random.choice(neighbors)
            stack.append(current)

            if next_cell.x == current.x + 1:
                current.walls['right'] = False
                next_cell.walls['left'] = False
            elif next_cell.x == current.x - 1:
                current.walls['left'] = False
                next_cell.walls['right'] = False
            elif next_cell.y == current.y + 1:
                current.walls['bottom'] = False
                next_cell.walls['top'] = False
            elif next_cell.y == current.y - 1:
                current.walls['top'] = False
                next_cell.walls['bottom'] = False

            current = next_cell
            current.visited = True
        elif stack:
            current = stack.pop()
        else:
            break
    return grid

# Generate maze
grid = generate_maze()

# Player setup
player_size = CELL_SIZE // 2
player = pygame.Rect(CELL_SIZE//4, CELL_SIZE//4, player_size, player_size)
exit_pos = pygame.Rect((GRID_WIDTH - 1) * CELL_SIZE + CELL_SIZE//4, 
                       (GRID_HEIGHT - 1) * CELL_SIZE + CELL_SIZE//4, 
                       player_size, player_size)

# Movement variables
MOVE_SPEED = 5  # For smoother movement

def get_current_cell():
    """Determine the cell the player is currently in using its center."""
    col = int(player.centerx // CELL_SIZE)
    row = int(player.centery // CELL_SIZE)
    # Clamp indices to be within the grid bounds
    col = min(max(col, 0), GRID_WIDTH - 1)
    row = min(max(row, 0), GRID_HEIGHT - 1)
    return grid[col][row]

def can_move(direction):
    """Allow movement if there is no wall in the specified direction."""
    current_cell = get_current_cell()

    if direction == 'left':
        if player.left <= 0:
            return False
        return not current_cell.walls['left']
    elif direction == 'right':
        if player.right >= WIDTH:
            return False
        return not current_cell.walls['right']
    elif direction == 'up':
        if player.top <= 0:
            return False
        return not current_cell.walls['top']
    elif direction == 'down':
        if player.bottom >= HEIGHT:
            return False
        return not current_cell.walls['bottom']
    
    return True

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    # Draw maze
    for col in grid:
        for cell in col:
            cell.draw()
    
    # Draw exit
    pygame.draw.rect(screen, RED, exit_pos)
    
    # Draw player
    pygame.draw.rect(screen, BLUE, player)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Smooth movement with proper wall collision
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT] and can_move('left'):
        player.x -= MOVE_SPEED
    if keys[pygame.K_RIGHT] and can_move('right'):
        player.x += MOVE_SPEED
    if keys[pygame.K_UP] and can_move('up'):
        player.y -= MOVE_SPEED
    if keys[pygame.K_DOWN] and can_move('down'):
        player.y += MOVE_SPEED
    
    # Check win condition
    if player.colliderect(exit_pos):
        print("You escaped the maze!")
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

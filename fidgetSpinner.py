import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fidget Spinner Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPINNER_COLORS = [
    (255, 0, 0),     
    (0, 0, 255),     
    (0, 255, 0),     
    (255, 255, 0),   
    (255, 0, 255),   
    (0, 255, 255),   
]

center = (WIDTH // 2, HEIGHT // 2)
radius = 100
arm_length = 80
arm_width = 25
rotation_angle = 0
angular_velocity = 0
friction = 0.99  
selected_color = random.choice(SPINNER_COLORS)

spinning = False
last_mouse_pos = None
high_score = 0  

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_spinner(surface, center, angle, color):
    pygame.draw.circle(surface, BLACK, center, 30)
    pygame.draw.circle(surface, color, center, 25)
    
    for i in range(3):
        arm_angle = angle + (i * 120)
        rad_angle = math.radians(arm_angle)
        
        x1 = center[0] + arm_length * 0.3 * math.cos(rad_angle)
        y1 = center[1] + arm_length * 0.3 * math.sin(rad_angle)
        x2 = center[0] + arm_length * math.cos(rad_angle)
        y2 = center[1] + arm_length * math.sin(rad_angle)
        
        perp_angle = rad_angle + math.pi/2
        dx = arm_width * math.cos(perp_angle)
        dy = arm_width * math.sin(perp_angle)
        
        points = [
            (x1 + dx/2, y1 + dy/2),
            (x1 - dx/2, y1 - dy/2),
            (x2 - dx/2, y2 - dy/2),
            (x2 + dx/2, y2 + dy/2)
        ]
        
        pygame.draw.polygon(surface, color, points)
        
        pygame.draw.circle(surface, BLACK, (int(x2), int(y2)), 20)
        pygame.draw.circle(surface, color, (int(x2), int(y2)), 15)

def calculate_angular_velocity(pos1, pos2, center):
    angle1 = math.atan2(pos1[1] - center[1], pos1[0] - center[0])
    angle2 = math.atan2(pos2[1] - center[1], pos2[0] - center[0])
    
    diff = (angle2 - angle1) % (2 * math.pi)
    if diff > math.pi:
        diff -= 2 * math.pi
    
    return diff * 10  

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not spinning:
                spinning = True
                last_mouse_pos = pygame.mouse.get_pos()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            spinning = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                selected_color = random.choice(SPINNER_COLORS)
    
    screen.fill(WHITE)
    
    if spinning and pygame.mouse.get_pressed()[0]:  
        current_mouse_pos = pygame.mouse.get_pos()
        if last_mouse_pos:
            new_velocity = calculate_angular_velocity(last_mouse_pos, current_mouse_pos, center)
            angular_velocity += new_velocity
            
            current_speed = abs(angular_velocity)
            if current_speed > high_score:
                high_score = current_speed
                
        last_mouse_pos = current_mouse_pos
    else:
        angular_velocity *= friction
    
    rotation_angle += angular_velocity
    rotation_angle %= 360
    
    draw_spinner(screen, center, rotation_angle, selected_color)
    
    speed_text = font.render(f"Speed: {abs(angular_velocity):.1f}", True, BLACK)
    highscore_text = font.render(f"High Score: {high_score:.1f}", True, BLACK)
    instructions = font.render("Click and drag to spin! Space to change color", True, BLACK)
    
    screen.blit(speed_text, (20, 20))
    screen.blit(highscore_text, (20, 60))
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    clock.tick(60)
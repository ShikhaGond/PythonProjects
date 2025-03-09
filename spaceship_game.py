import pygame
import math
import random
import sys
from pygame import mixer

# Initialize pygame
pygame.init()

# Screen dimensions (same as template)
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Space Shooter")

CST_ANG_VEL = 0.07  # angle velocity of ship
CST_ACC_SPEED = 0.055  #  acceleration speed of ship
COE_FRI = 0.008  # Coefficient of friction
MIS_SPEED = 10  #  missile speed

def create_starfield(num_stars, speed, size_range, color_range):
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(size_range[0], size_range[1])
        brightness = random.randint(color_range[0], color_range[1])
        color = (brightness, brightness, brightness)
        stars.append([x, y, size, color, speed])
    return stars

# nebula effect
def create_nebula():
    nebula = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(100, 300)
        r = random.randint(0, 100)
        g = random.randint(0, 100)
        b = random.randint(100, 200)
        for i in range(radius, 0, -1):
            alpha = 2 if i > radius - 20 else 0
            pygame.draw.circle(nebula, (r, g, b, alpha), (x, y), i)
    return nebula

# multiple star layers for parallax effect
distant_stars = create_starfield(200, 0.1, (1, 2), (100, 180))
mid_stars = create_starfield(100, 0.3, (1, 3), (150, 220))
close_stars = create_starfield(50, 0.5, (2, 4), (180, 255))
nebula_surface = create_nebula()

# realistic spaceship image
def create_spaceship():
    ship_surface = pygame.Surface((50, 40), pygame.SRCALPHA)
    
    # Main body
    pygame.draw.ellipse(ship_surface, (180, 180, 200), (10, 5, 30, 25))
    
    # Cockpit
    pygame.draw.ellipse(ship_surface, (100, 180, 255), (15, 10, 20, 12))
    
    # Wings
    pygame.draw.polygon(ship_surface, (150, 150, 170), [(5, 15), (15, 15), (5, 30)])
    pygame.draw.polygon(ship_surface, (150, 150, 170), [(45, 15), (35, 15), (45, 30)])
    
    # Thrusters
    pygame.draw.rect(ship_surface, (100, 100, 120), (15, 30, 20, 5))
    
    # Engines with no thrust
    pygame.draw.rect(ship_surface, (80, 80, 100), (18, 35, 5, 3))
    pygame.draw.rect(ship_surface, (80, 80, 100), (27, 35, 5, 3))
    
    return ship_surface

# thrust effect for spaceship
def create_thrust_effect():
    thrust_surface = pygame.Surface((14, 20), pygame.SRCALPHA)
    
    # Inner flame (brighter)
    pygame.draw.polygon(thrust_surface, (255, 200, 50, 200), [(2, 0), (12, 0), (7, 15)])
    
    # Outer flame (more transparent)
    pygame.draw.polygon(thrust_surface, (255, 100, 0, 150), [(0, 0), (14, 0), (7, 20)])
    
    return thrust_surface

# missile image
def create_missile():
    missile_surface = pygame.Surface((8, 20), pygame.SRCALPHA)
    
    # Missile body
    pygame.draw.rect(missile_surface, (200, 200, 220), (2, 0, 4, 16))
    
    # Missile head
    pygame.draw.polygon(missile_surface, (220, 220, 240), [(2, 0), (6, 0), (4, -4)])
    
    # Missile thruster flame
    pygame.draw.polygon(missile_surface, (255, 100, 0, 200), [(2, 16), (6, 16), (4, 20)])
    
    return missile_surface

# asteroid
def create_asteroid(size):
    asteroid_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Base circle
    pygame.draw.circle(asteroid_surface, (100, 90, 90), (size//2, size//2), size//2)
    
    # some crater details and texture
    for _ in range(size//10):
        crater_x = random.randint(5, size-5)
        crater_y = random.randint(5, size-5)
        crater_size = random.randint(2, size//8)
        shade = random.randint(60, 90)
        pygame.draw.circle(asteroid_surface, (shade, shade, shade), (crater_x, crater_y), crater_size)
    
    # some highlights/shadows to give 3D effect
    for _ in range(size//5):
        x = random.randint(0, size)
        y = random.randint(0, size)
        s = random.randint(1, 4)
        if math.sqrt((x - size//2)**2 + (y - size//2)**2) < size//2:
            shade = random.randint(110, 140)
            pygame.draw.circle(asteroid_surface, (shade, shade, shade), (x, y), s)
    
    return asteroid_surface

# explosion animation frames
def create_explosion_frames(num_frames=8, size=50):
    frames = []
    for i in range(num_frames):
        scale = (i + 1) / num_frames
        frame = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Inner bright part
        inner_radius = int(size * 0.4 * scale)
        pygame.draw.circle(frame, (255, 255, 200, 255), (size//2, size//2), inner_radius)
        
        # Middle orange part
        middle_radius = int(size * 0.7 * scale)
        if middle_radius > inner_radius:
            pygame.draw.circle(frame, (255, 150, 50, 200), (size//2, size//2), middle_radius)
        
        # Outer red part
        outer_radius = int(size * scale)
        if outer_radius > middle_radius:
            pygame.draw.circle(frame, (255, 50, 0, 150 - int(140 * i/num_frames)), (size//2, size//2), outer_radius)
        
        frames.append(frame)
    return frames

# game assets
ship_img = create_spaceship()
ship_thrust_img = create_thrust_effect()
missile_img = create_missile()
explosion_frames = create_explosion_frames()

# Attempt to load sounds
try:
    mixer.init()
    shoot_sound = mixer.Sound('shoot.wav')
    explosion_sound = mixer.Sound('explosion.wav')
    thruster_sound = mixer.Sound('thruster.wav')
    mixer.music.load('background.wav')
    mixer.music.play(-1)
    sound_enabled = True
except:
    print("Sound files not found. Game will run without sound.")
    sound_enabled = False

# Sprite Class 
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, radius, is_missile=False, is_asteroid=False):
        self.pos = list(pos)
        self.vel = list(vel)
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.radius = radius
        self.age = 0
        self.lifespan = 60 if is_missile else float('inf')  # Missiles live for 60 frames
        self.is_missile = is_missile
        self.is_asteroid = is_asteroid
        self.size = image.get_width()  # For scaling and drawing
        
        # For asteroid rotation animation
        if is_asteroid:
            self.original_image = image
        
    def draw(self, surface):
        if self.is_asteroid:
            # Rotate the asteroid
            rotated_image = pygame.transform.rotate(self.original_image, math.degrees(self.angle))
            rect = rotated_image.get_rect(center=(self.pos[0], self.pos[1]))
            surface.blit(rotated_image, rect.topleft)
        else:
            # For missiles or other sprites, rotate and position
            rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle) - 90)
            rect = rotated_image.get_rect(center=(self.pos[0], self.pos[1]))
            surface.blit(rotated_image, rect.topleft)
    
    def update(self):
        # angle
        self.angle += self.angle_vel
        
        # position based on velocity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # Wrap around screen edges
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        
        # age for missiles
        if self.is_missile:
            self.age += 1
            
        return self.age < self.lifespan

# Ship class
class Ship:
    def __init__(self, pos, vel, angle):
        self.pos = list(pos)
        self.vel = list(vel)
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = ship_img
        self.thrust_image = ship_thrust_img
        self.radius = 20
        self.thrusting = False
    
    def draw(self, surface):
        # Draw the ship at the correct angle
        rotated_ship = pygame.transform.rotate(self.image, math.degrees(-self.angle) - 90)
        ship_rect = rotated_ship.get_rect(center=(self.pos[0], self.pos[1]))
        surface.blit(rotated_ship, ship_rect.topleft)
        
        # Draw the thrust if ship is thrusting
        if self.thrusting:
            # Calculate position behind the ship
            thrust_angle = -self.angle - math.pi/2
            thrust_x = self.pos[0] + 20 * math.cos(thrust_angle)
            thrust_y = self.pos[1] + 20 * math.sin(thrust_angle)
            
            # Rotate thrust image
            rotated_thrust = pygame.transform.rotate(self.thrust_image, math.degrees(-self.angle) - 90)
            thrust_rect = rotated_thrust.get_rect(center=(thrust_x, thrust_y))
            surface.blit(rotated_thrust, thrust_rect.topleft)
    
    def update(self):
        #  angle
        self.angle += self.angle_vel
        
        # Apply thrust if thrusting
        if self.thrusting:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * CST_ACC_SPEED
            self.vel[1] += acc[1] * CST_ACC_SPEED
        
        # Apply friction
        self.vel[0] *= (1 - COE_FRI)
        self.vel[1] *= (1 - COE_FRI)
        
        # Update position
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # Wrap around screen edges
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
    
    def shoot(self):
        # Calculate missile position and velocity
        forward = angle_to_vector(self.angle)
        missile_pos = [
            self.pos[0] + self.radius * forward[0],
            self.pos[1] + self.radius * forward[1]
        ]
        missile_vel = [
            self.vel[0] + forward[0] * MIS_SPEED,
            self.vel[1] + forward[1] * MIS_SPEED
        ]
        
        # Create and return a new missile
        if sound_enabled:
            shoot_sound.play()
        return Sprite(missile_pos, missile_vel, self.angle, 0, missile_img, 4, is_missile=True)

# Explosion class for better visual effects
class Explosion:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.frames = explosion_frames
        self.current_frame = 0
        self.frame_delay = 2  # Show each frame for 2 game loops
        self.current_delay = 0
        if sound_enabled:
            explosion_sound.play()
    
    def update(self):
        self.current_delay += 1
        if self.current_delay >= self.frame_delay:
            self.current_frame += 1
            self.current_delay = 0
        return self.current_frame < len(self.frames)
    
    def draw(self, surface):
        if self.current_frame < len(self.frames):
            frame = self.frames[self.current_frame]
            scaled_frame = pygame.transform.scale(frame, (self.size, self.size))
            rect = scaled_frame.get_rect(center=self.pos)
            surface.blit(scaled_frame, rect.topleft)

# Helper functions
def angle_to_vector(angle):
    return [math.cos(angle), math.sin(angle)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

# Asteroid spawner
def spawn_asteroid():
    size = random.randint(30, 70)
    pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
    
    # Ensure asteroid doesn't spawn too close to the ship
    while dist(pos, my_ship.pos) < 100:
        pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
    
    vel = [random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)]
    ang_vel = random.uniform(-0.1, 0.1)
    asteroid_img = create_asteroid(size)
    
    return Sprite(pos, vel, 0, ang_vel, asteroid_img, size//2, is_asteroid=True)

# Game variables
score = 0
lives = 3
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0)
missiles = []
asteroids = []
explosions = []
game_over = False
last_asteroid_time = 0
asteroid_spawn_interval = 1500  # milliseconds

# Initialize some asteroids
for _ in range(4):
    asteroids.append(spawn_asteroid())

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    my_ship.angle_vel = CST_ANG_VEL
                elif event.key == pygame.K_RIGHT:
                    my_ship.angle_vel = -CST_ANG_VEL
                elif event.key == pygame.K_UP:
                    my_ship.thrusting = True
                    if sound_enabled:
                        thruster_sound.play(-1)  # Loop the sound
                elif event.key == pygame.K_SPACE:
                    if len(missiles) < 5:  # Limit number of missiles
                        missiles.append(my_ship.shoot())
                elif event.key == pygame.K_r and game_over:
                    # Reset game
                    score = 0
                    lives = 3
                    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0)
                    missiles = []
                    asteroids = []
                    explosions = []
                    game_over = False
                    for _ in range(4):
                        asteroids.append(spawn_asteroid())
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    my_ship.angle_vel = 0
                elif event.key == pygame.K_UP:
                    my_ship.thrusting = False
                    if sound_enabled:
                        thruster_sound.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Reset game
            score = 0
            lives = 3
            my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0)
            missiles = []
            asteroids = []
            explosions = []
            game_over = False
            for _ in range(4):
                asteroids.append(spawn_asteroid())
    
    # Update game state
    if not game_over:
        # Spawn new asteroids over time
        current_time = pygame.time.get_ticks()
        if current_time - last_asteroid_time > asteroid_spawn_interval and len(asteroids) < 12:
            asteroids.append(spawn_asteroid())
            last_asteroid_time = current_time
            # Increase difficulty over time
            asteroid_spawn_interval = max(500, asteroid_spawn_interval - 10)
        
        # Update ship
        my_ship.update()
        
        # Update and filter missiles
        missiles = [missile for missile in missiles if missile.update()]
        
        # Update and filter asteroids
        asteroids = [asteroid for asteroid in asteroids if asteroid.update()]
        
        # Update and filter explosions
        explosions = [explosion for explosion in explosions if explosion.update()]
        
        # Check for missile-asteroid collisions
        for missile in missiles[:]:
            for asteroid in asteroids[:]:
                if dist(missile.pos, asteroid.pos) < missile.radius + asteroid.radius:
                    # Remove missile and asteroid
                    if missile in missiles:
                        missiles.remove(missile)
                    if asteroid in asteroids:
                        asteroids.remove(asteroid)
                    
                    # Create explosion
                    explosions.append(Explosion(asteroid.pos, asteroid.size * 2))
                    
                    # Update score
                    score += 10 + asteroid.size // 10
                    break
        
        # Check for ship-asteroid collisions
        for asteroid in asteroids[:]:
            if dist(my_ship.pos, asteroid.pos) < my_ship.radius + asteroid.radius:
                # Remove asteroid
                asteroids.remove(asteroid)
                
                # Create explosion
                explosions.append(Explosion(asteroid.pos, asteroid.size * 2))
                
                # Lose a life
                lives -= 1
                
                if lives <= 0:
                    game_over = True
                
                break
    
    # Draw everything
    screen.fill((0, 0, 15))  
    
    # Draw parallax star layers
    for star in distant_stars:
        pygame.draw.circle(screen, star[3], (int(star[0]), int(star[1])), star[2])
        # Move stars slowly
        star[0] = (star[0] + star[4]) % WIDTH
    
    # Draw nebula
    screen.blit(nebula_surface, (0, 0))
    
    # Draw mid-distance stars
    for star in mid_stars:
        pygame.draw.circle(screen, star[3], (int(star[0]), int(star[1])), star[2])
        # Move stars at medium speed
        star[0] = (star[0] + star[4]) % WIDTH
    
    # Draw close stars
    for star in close_stars:
        pygame.draw.circle(screen, star[3], (int(star[0]), int(star[1])), star[2])
        # Move stars faster
        star[0] = (star[0] + star[4]) % WIDTH
    
    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw(screen)
    
    # Draw explosions
    for explosion in explosions:
        explosion.draw(screen)
    
    # Draw missiles
    for missile in missiles:
        missile.draw(screen)
    
    # Draw ship
    if not game_over:
        my_ship.draw(screen)
    
    # Draw HUD
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))
    
    # Draw game over screen
    if game_over:
        game_over_text = font.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit()
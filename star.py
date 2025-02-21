import pygame
import math
import random
import sys

def get_star_vertices(outer_radius, inner_radius, n_points=5, start_angle=-math.pi/2):
    """Calculate the 10 vertices (alternating outer and inner) of a star."""
    vertices = []
    for i in range(2 * n_points):
        angle = start_angle + i * (math.pi / n_points)
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        vertices.append((x, y))
    return vertices

def interpolate_points(p1, p2, num_points):
    """Linearly interpolate between two points."""
    points = []
    for i in range(num_points):
        t = i / float(num_points)
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        points.append((x, y))
    return points

def get_star_points(outer_radius, inner_radius, resolution=50, n_points=5, start_angle=-math.pi/2):
    """
    Generate a list of points along the star boundary by interpolating between the vertices.
    'resolution' sets how many points between each vertex.
    """
    vertices = get_star_vertices(outer_radius, inner_radius, n_points, start_angle)
    star_points = []
    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
        interp = interpolate_points(p1, p2, resolution)
        star_points.extend(interp)
    return star_points

def scale_and_translate(pos, sx, sy, dx, dy):
    return (dx + pos[0] * sx, dy + pos[1] * sy)

def hsl_to_rgb(h, s, l):
    """
    Convert HSL to RGB.
    h: 0-360, s: 0-100, l: 0-100
    Returns tuple of 0-255 integers.
    """
    s /= 100.0
    l /= 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs(((h / 60.0) % 2) - 1))
    m = l - c / 2.0
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Lost in Space")
clock = pygame.time.Clock()

# Surface for fading trails (alpha)
fade_surface = pygame.Surface((width, height))
fade_surface.set_alpha(25)  
fade_surface.fill((0, 0, 0))

font = pygame.font.SysFont("Tangerine", 64)  

# Star Points & Particles
trace_count = 60

# Generating star points with different scales/resolutions
star_points_set1 = get_star_points(outer_radius=210, inner_radius=100, resolution=50)
star_points_set2 = get_star_points(outer_radius=150, inner_radius=80, resolution=50)
star_points_set3 = get_star_points(outer_radius=90, inner_radius=50, resolution=50)

points_origin = []
for pt in star_points_set1:
    points_origin.append(pt)
for pt in star_points_set2:
    points_origin.append(pt)
for pt in star_points_set3:
    points_origin.append(pt)

star_points_count = len(points_origin)
target_points = [(0, 0)] * star_points_count

def pulse(kx, ky):
    global target_points
    target_points = [(kx * pt[0] + width / 2, ky * pt[1] + height / 2) for pt in points_origin]

# 1/1 particle
particles = []
for i in range(star_points_count):
    x = random.random() * width
    y = random.random() * height
    
    sat = int(40 * random.random() + 60)  
    lig = int(60 * random.random() + 20)    
    color = hsl_to_rgb(240, sat, lig)
    particle = {
        "vx": 0.0,
        "vy": 0.0,
        "R": 2,
        "speed": random.random() + 5,
        "q": random.randrange(star_points_count),
        "D": 1 if i % 2 == 0 else -1,
        "force": 0.2 * random.random() + 0.7,
        "color": color,
        "trace": [{"x": x, "y": y} for _ in range(trace_count)]
    }
    particles.append(particle)

config = {"traceK": 0.4, "timeDelta": 0.01}
time_val = 0.0

running = True
while running:
    clock.tick(60)  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(fade_surface, (0, 0))
    
    # Pulse Parameter
    n = -math.cos(time_val)
    k_val = (1 + n) * 0.5
    pulse(k_val, k_val)
    if math.sin(time_val) < 0:
        delta = 9
    elif n > 0.8:
        delta = 0.2
    else:
        delta = 1
    time_val += delta * config["timeDelta"]

    # Particle Update
    for particle in particles:
        q_index = particle["q"]
        qx, qy = target_points[q_index]
        dx = particle["trace"][0]["x"] - qx
        dy = particle["trace"][0]["y"] - qy
        length = math.sqrt(dx * dx + dy * dy) or 0.001  

        if length < 10:
            if random.random() > 0.95:
                particle["q"] = random.randrange(star_points_count)
            else:
                if random.random() > 0.99:
                    particle["D"] *= -1
                particle["q"] = (particle["q"] + particle["D"]) % star_points_count

        particle["vx"] += (-dx / length) * particle["speed"]
        particle["vy"] += (-dy / length) * particle["speed"]

        particle["trace"][0]["x"] += particle["vx"]
        particle["trace"][0]["y"] += particle["vy"]

        particle["vx"] *= particle["force"]
        particle["vy"] *= particle["force"]

        for k in range(len(particle["trace"]) - 1):
            T = particle["trace"][k]
            N = particle["trace"][k + 1]
            N["x"] -= config["traceK"] * (N["x"] - T["x"])
            N["y"] -= config["traceK"] * (N["y"] - T["y"])

        for pt in particle["trace"]:
            pygame.draw.rect(screen, particle["color"], (int(pt["x"]), int(pt["y"]), 1, 1))

    
    text_surface = font.render("Lost in Space", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(width // 2, int(height * 0.9)))
    screen.blit(text_surface, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()

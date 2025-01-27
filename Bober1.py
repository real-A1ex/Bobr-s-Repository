import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 900

# Colors
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
BROWN = (0.545, 0.271, 0.075)
GRAY = (0.502, 0.502, 0.502)
LIGHT_GRAY = (0.7, 0.7, 0.7)
DARK_GRAY = (0.3, 0.3, 0.3)
LIGHT_GREEN = (0.565, 0.933, 0.565)
GREEN = (0, 1, 0)
RED = (1, 0, 0)
BLUE = (0, 0, 1)
YELLOW = (1, 1, 0)
CYAN = (0, 1, 1)
MAGENTA = (1, 0, 1)

def draw_cube(x, y, z, size, colors):
    glPushMatrix()
    glTranslatef(x, y, z)
    glBegin(GL_QUADS)

    # Front face
    glColor3fv(colors[0])
    glVertex3f(0, 0, 0)
    glVertex3f(size, 0, 0)
    glVertex3f(size, size, 0)
    glVertex3f(0, size, 0)

    # Back face
    glColor3fv(colors[1])
    glVertex3f(0, 0, -size)
    glVertex3f(size, 0, -size)
    glVertex3f(size, size, -size)
    glVertex3f(0, size, -size)

    # Left face
    glColor3fv(colors[2])
    glVertex3f(0, 0, 0)
    glVertex3f(0, size, 0)
    glVertex3f(0, size, -size)
    glVertex3f(0, 0, -size)

    # Right face
    glColor3fv(colors[3])
    glVertex3f(size, 0, 0)
    glVertex3f(size, size, 0)
    glVertex3f(size, size, -size)
    glVertex3f(size, 0, -size)

    # Top face
    glColor3fv(colors[4])
    glVertex3f(0, size, 0)
    glVertex3f(size, size, 0)
    glVertex3f(size, size, -size)
    glVertex3f(0, size, -size)

    # Bottom face
    glColor3fv(colors[5])
    glVertex3f(0, 0, 0)
    glVertex3f(size, 0, 0)
    glVertex3f(size, 0, -size)
    glVertex3f(0, 0, -size)

    glEnd()
    glPopMatrix()

class Tile:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.height = height

    def draw(self):
        glColor3fv(LIGHT_GREEN)
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, -1)
        glVertex3f(1, 0, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(0, 1, -1)
        glEnd()
        glPopMatrix()

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = random.randint(5, 10)
        self.health = 10  # Trees now have health

    def grow(self):
        if self.age < 10 and random.random() < 0.1:
            self.age += 2

    def fell(self):
        return Item('wood')

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # Tree is destroyed
        return False

    def draw(self):
        colors = [BROWN, BROWN, BROWN, BROWN, GREEN, GREEN] if self.age < 10 else [GREEN, GREEN, GREEN, GREEN, BROWN, BROWN]
        draw_cube(self.x, self.y, 0, 1, colors)

class Item:
    def __init__(self, name):
        self.name = name

class Bober:
    def __init__(self, x, y, speed=0.1, color=None):
        self.x = x
        self.y = y
        self.speed = speed
        self.inventory = []
        self.color = color if color else RED
        self.teeth_level = 1  # Start with level 1 teeth
        self.attack_damage = 2  # Damage per attack

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if not is_collision(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def chop_tree(self, tree):
        if tree.age >= 10:
            item = tree.fell()
            self.pick_up(item)

    def pick_up(self, item):
        self.inventory.append(item)

    def upgrade_castle(self, castle):
        wood_count = sum(1 for item in self.inventory if item.name == 'wood')
        if wood_count >= 2 and abs(self.x - castle.x) < 2 and abs(self.y - castle.y) < 2:
            removed = 0
            for item in self.inventory[:]:
                if item.name == 'wood' and removed < 2:
                    self.inventory.remove(item)
                    removed += 1
            castle.improve()

    def upgrade_teeth(self):
        wood_count = sum(1 for item in self.inventory if item.name == 'wood')
        if wood_count >= 10:
            # Remove 10 wood from inventory
            removed = 0
            for item in self.inventory[:]:
                if item.name == 'wood' and removed < 10:
                    self.inventory.remove(item)
                    removed += 1
            # Increase teeth level
            self.teeth_level += 1
            self.attack_damage += 1  # Increase attack damage with teeth level
            print(f"Teeth upgraded to level {self.teeth_level}!")

    def attack(self):
        for tree in trees:
            if abs(self.x - tree.x) <= 1 and abs(self.y - tree.y) <= 1:
                if tree.take_damage(self.attack_damage):
                    trees.remove(tree)  # Remove tree if health <= 0
                    print("Tree destroyed!")
                break

    def draw(self):
        colors = [self.color] * 6
        draw_cube(self.x, self.y, 0, 1, colors)

class Castle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1

    def improve(self):
        self.level += 1

    def draw(self):
        colors = [LIGHT_GRAY] * 6 if self.level < 2 else [DARK_GRAY] * 6
        for lvl in range(self.level):
            draw_cube(self.x, self.y, lvl, 1, colors)

# Create world
tiles = [[Tile(x, y, random.randint(1, 5)) for x in range(20)] for y in range(20)]
trees = [Tree(random.randint(0, 19), random.randint(0, 19)) for _ in range(20)]
bobers = [Bober(1, 1, color=CYAN), Bober(10, 10, color=MAGENTA)]
castles = [Castle(2, 2), Castle(17, 17)]

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(WHITE[0], WHITE[1], WHITE[2], 1)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def tick_tiles():
    sampled_tiles = random.sample([tile for row in tiles for tile in row], k=1)
    for tile in sampled_tiles:
        if random.random() < 0.01:
            trees.append(Tree(tile.x, tile.y))

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(10, -25, 20, 10, 10, 0, 0, 0, 1)

    for row in tiles:
        for tile in row:
            tile.draw()
    for tree in trees:
        tree.draw()
    for bober in bobers:
        bober.draw()
    for castle in castles:
        castle.draw()

    pygame.display.flip()

def is_collision(x, y):
    if x < 0 or y < 0 or x >= 20 or y >= 20:
        return True
    for tree in trees:
        if abs(x - tree.x) < 1 and abs(y - tree.y) < 1:
            return True
    for castle in castles:
        if abs(x - castle.x) < 1 and abs(y - castle.y) < 1:
            return True
    return False

def chop_tree_near_bober(bober):
    for tree in trees:
        if abs(bober.x - tree.x) <= 2 and abs(bober.y - tree.y) <= 2:
            bober.chop_tree(tree)
            trees.remove(tree)
            break

def handleKeypresses():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        bobers[0].move(-1, 0)
    if keys[pygame.K_RIGHT]:
        bobers[0].move(1, 0)
    if keys[pygame.K_UP]:
        bobers[0].move(0, 1)
    if keys[pygame.K_DOWN]:
        bobers[0].move(0, -1)
    if keys[pygame.K_SPACE]:
        chop_tree_near_bober(bobers[0])
    if keys[pygame.K_l]:
        bobers[0].upgrade_castle(castles[0])
    if keys[pygame.K_k]:  # Upgrade teeth for bober 1
        bobers[0].upgrade_teeth()
    if keys[pygame.K_f]:  # Attack for bober 1
        bobers[0].attack()

    if keys[pygame.K_a]:
        bobers[1].move(-1, 0)
    if keys[pygame.K_d]:
        bobers[1].move(1, 0)
    if keys[pygame.K_w]:
        bobers[1].move(0, 1)
    if keys[pygame.K_s]:
        bobers[1].move(0, -1)
    if keys[pygame.K_LSHIFT]:
        chop_tree_near_bober(bobers[1])
    if keys[pygame.K_q]:
        bobers[1].upgrade_castle(castles[1])
    if keys[pygame.K_e]:  # Upgrade teeth for bober 2
        bobers[1].upgrade_teeth()
    if keys[pygame.K_r]:  # Attack for bober 2
        bobers[1].attack()

# Main game loop
running = True
screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Bober World")
init_gl()
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handleKeypresses()
    for tree in trees:
        tree.grow()
    tick_tiles()
    draw_scene()
    clock.tick(60)

pygame.quit()

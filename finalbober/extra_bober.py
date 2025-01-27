import glfw
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import glm

# Constants
WIDTH, HEIGHT = 1200, 1200

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
BACKGROUND_COLOR = (66 / 255, 135 / 255, 245 / 255)  # Normalized RGB values

def load_texture(image_path):
    img = Image.open(image_path)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  
    img_data = img.convert("RGBA").tobytes() 
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id


running = True

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
    def __init__(self, x, y, height, texture_id):
        self.x = x
        self.y = y
        self.height = height
        self.texture_id = texture_id

    def draw(self):
        glEnable(GL_TEXTURE_2D)  # Enable texturing
        glBindTexture(GL_TEXTURE_2D, self.texture_id)  # Bind the texture

        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glBegin(GL_QUADS)

        # Define texture coordinates and vertices for the tile
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, -1)
        glTexCoord2f(1, 0)
        glVertex3f(1, 0, -1)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, -1)
        glTexCoord2f(0, 1)
        glVertex3f(0, 1, -1)

        glEnd()
        glPopMatrix()

        glBindTexture(GL_TEXTURE_2D, 0)  # Unbind the texture
        glDisable(GL_TEXTURE_2D)  # Disable texturing

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = random.randint(5, 10)
        self.health = 100  # Trees now have health

    def fell(self):
        return Item('wood')

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False

    def draw(self):
        colors = [BROWN, BROWN, BROWN, BROWN, BROWN, BROWN]
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
        self.teeth_level = 1  
        self.attack_damage = 2  
        self.wood_amount = 0

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
        self.wood_amount += 1

    def upgrade_castle(self, castle):
        price = castle.level * castle.level + 3

        if self.wood_amount >= price and abs(self.x - castle.x) < 2 and abs(self.y - castle.y) < 2:
            self.wood_amount -= price
            castle.improve()

    def upgrade_teeth(self):
        price = self.teeth_level * self.teeth_level + 5
        self.wood_amount = sum(1 for item in self.inventory if item.name == 'wood')
        if self.wood_amount >= price:
            self.wood_amount -= price
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
        self.health = 100

    def improve(self):
        self.level += 200

    def draw(self):
        colors = [LIGHT_GRAY] * 6 if self.level < 2 else [DARK_GRAY] * 6
        for lvl in range(self.level):
            draw_cube(self.x, self.y, lvl, 1, colors)


trees = [Tree(random.randint(0, 19), random.randint(0, 19)) for _ in range(20)]
bobers = [Bober(1, 1, color=CYAN), Bober(10, 10, color=MAGENTA)]
castles = [Castle(2, 2), Castle(17, 17)]

def init_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D) 
    glClearColor(*BACKGROUND_COLOR, 1.0)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def tick_tiles():
    sampled_tiles = random.sample([tile for row in tiles for tile in row], k=1)
    for tile in sampled_tiles:
        if random.random() < 0.01:
            trees.append(Tree(tile.x, tile.y))

def is_collision(x, y):
    if x < 0 or y < 0 or x >= 19 or y >= 19:
        return True
    for tree in trees:
        if abs(x - tree.x) < 0.9 and abs(y - tree.y) < 0.9:
            return True
    for castle in castles:
        if abs(x - castle.x) < 1 and abs(y - castle.y) < 1:
            return True
    return False

def chop_tree_near_bober(bober):
    for tree in trees:
        if abs(bober.x - tree.x) <= 1.1 and abs(bober.y - tree.y) <= 1.1:
            bober.chop_tree(tree)
            trees.remove(tree)
            break

def handleKeypresses(window):
    global running
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        bobers[0].move(-1, 0)
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        bobers[0].move(1, 0)
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        bobers[0].move(0, 1)
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        bobers[0].move(0, -1)
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        chop_tree_near_bober(bobers[0])
    if glfw.get_key(window, glfw.KEY_L) == glfw.PRESS:  # upgrade castle bob1
        bobers[0].upgrade_castle(castles[0])
    if glfw.get_key(window, glfw.KEY_K) == glfw.PRESS:  # upgrade teeth bob1
        bobers[0].upgrade_teeth()
    if glfw.get_key(window, glfw.KEY_F) == glfw.PRESS:  # attack bob1
        bobers[0].attack()
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        bobers[1].move(-1, 0)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        bobers[1].move(1, 0)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        bobers[1].move(0, 1)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        bobers[1].move(0, -1)
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        chop_tree_near_bober(bobers[1])
    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:  # bob2 castle upgrade
        bobers[1].upgrade_castle(castles[1])
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:  # upgrade teeth for bob2
        bobers[1].upgrade_teeth()
    if glfw.get_key(window, glfw.KEY_R) == glfw.PRESS:  # attack for bober2
        bobers[1].attack()
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        running = False
        glfw.set_window_should_close(window, True)

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

# Main game loop
if not glfw.init():
    raise Exception("Error")

window = glfw.create_window(WIDTH, HEIGHT, "3D Bober World", None, None)
if not window:
    glfw.terminate()
    raise Exception("Failed to create GLFW window")

glfw.make_context_current(window)
init_gl()

texture_id = load_texture("finalbober\\grass.png")
tiles = [[Tile(x, y, random.randint(1, 5), texture_id) for x in range(20)] for y in range(20)]


while not glfw.window_should_close(window) and running:
    handleKeypresses(window)
    tick_tiles()
    draw_scene()
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate() 
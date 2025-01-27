from OpenGL.GL import *
import glfw
import sys
import os
from extra_bober import *
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
        colors = [BROWN, BROWN, BROWN, BROWN, GREEN, GREEN]
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

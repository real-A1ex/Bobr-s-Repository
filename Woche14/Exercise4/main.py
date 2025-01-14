import sys
import random
import math
import glm
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from Sphere import Sphere

class OpenGLWindow(QOpenGLWidget):

    def initializeGL(self):
        self.setMinimumSize(800, 800)
        self.sphere_list = []
        self.fly = False
        self.camera_position = glm.vec3(10, 10, 10)
        self.view_matrix = glm.lookAt(self.camera_position, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        self.projection_matrix = glm.perspective(glm.radians(60.0), 800.0 / 800.0, 0.1, 1000.0)

        for i in range(4):
            sphere = Sphere(random.randint(0, 100) / 100,
                            glm.vec3(random.randint(0, 100) / 100, random.randint(0, 100) / 100,
                                     random.randint(0, 100) / 100))
            sphere.translate(glm.vec3(random.randint(0, 100) / 10 * i, random.randint(0, 100) / 10 * i,
                                      random.randint(0, 100) / 10 * i))
            self.sphere_list.append(sphere)

        glClearColor(0.5, 0.5, 0.5, 0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Set up a timer to trigger updates (render loop)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)  # Connect the timer to the update method
        self.timer.start(16)  # Approximately 60 FPS


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.fly:
            dx = self.camera_position.x
            dz = self.camera_position.z
            radius = math.sqrt(self.camera_position.x**2 + self.camera_position.z**2)

            # Calculate the angle in radians
            angle_radians = np.arctan2(dz, dx)
            new_angle_radians = angle_radians - np.radians(0.1)  # For clockwise rotation

            # Set new camera positions
            self.camera_position.x = radius * np.cos(new_angle_radians)
            self.camera_position.z = radius * np.sin(new_angle_radians)

            self.view_matrix = glm.lookAt(self.camera_position, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

        for sphere in self.sphere_list:
            sphere.draw(self.view_matrix, self.projection_matrix)



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_I:
            self.camera_position *= 0.7
        elif event.key() == Qt.Key_O:
            self.camera_position *= 1.3
        elif event.key() == Qt.Key_F:
            self.fly = not self.fly

        self.view_matrix = glm.lookAt(self.camera_position, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OpenGL with PyQt5")
        self.setGeometry(100, 100, 800, 800)
        self.opengl_widget = OpenGLWindow(self)
        self.setCentralWidget(self.opengl_widget)

        self.b = QLabel(self)

    def keyPressEvent(self, a0):
        self.opengl_widget.keyPressEvent(a0)


        self.b.setText(str(a0.text()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()



    window.show()
    sys.exit(app.exec_())
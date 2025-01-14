import glm
import math
import numpy as np

from cg_helper import *

class Sphere:
    def __init__(self, rotational_speed, rotational_axis):
        self.model_matrix = glm.mat4()
        self.rotational_speed = rotational_speed
        self.rotational_axis = rotational_axis

        # load shader programs
        vertex_shader_source_sphere = read_shader_source('sphere.vertex')
        fragment_shader_source_sphere = read_shader_source('sphere.fragment')

        self.shader_program_sphere = create_shader_program(vertex_shader_source_sphere, fragment_shader_source_sphere)

        self.vertices = []
        self.normals = []

        sector_count = 16
        stack_count = 8
        self.compute_vertices(stack_count, sector_count)
        self.compute_normals(stack_count, sector_count)

        # VAO for sphere
        self.vao_sphere = glGenVertexArrays(1)
        glBindVertexArray(self.vao_sphere)

        # VBO for positions
        vertex_buffer_sphere = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_sphere)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # connection to vertex shader (in-attributes)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * self.vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # VBO for indices
        face_buffer_sphere = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, face_buffer_sphere)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # VBO for colors
        color_buffer_sphere = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, color_buffer_sphere)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

        # connection to vertex shader (in-attributes)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * self.normals.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)


    def translate(self, translation_vector):
        self.model_matrix = glm.translate(self.model_matrix, translation_vector)

    def rotate(self):
        self.model_matrix = glm.rotate(self.model_matrix, math.pi / 180 * self.rotational_speed, self.rotational_axis)

    def draw(self, view_matrix, projection_matrix):
        # rotate first
        self.rotate()

        # general approach to draw an object: activate shader, bind VAO, call draw
        glUseProgram(self.shader_program_sphere)

        # send matrices to shader
        view_loc = glGetUniformLocation(self.shader_program_sphere, 'view_matrix')
        projection_loc = glGetUniformLocation(self.shader_program_sphere, 'projection_matrix')
        model_loc = glGetUniformLocation(self.shader_program_sphere, 'model_matrix')

        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view_matrix))
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(projection_matrix))
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(self.model_matrix))

        glBindVertexArray(self.vao_sphere)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

    def compute_vertices(self, stack_count, sector_count):
        radius = 1.0
        lengthInv = 1.0 / radius

        sectorStep = 2 * math.pi / sector_count
        stackStep = math.pi / stack_count

        for i in range(stack_count + 1):
            stackAngle = math.pi / 2 - i * stackStep  # starting from pi/2 to -pi/2
            xy = radius * math.cos(stackAngle)  # r * cos(u)
            z = radius * math.sin(stackAngle)  # r * sin(u)

            # Add (sectorCount+1) vertices per stack
            # First and last vertices have same position and normal
            for j in range(sector_count + 1):
                sectorAngle = j * sectorStep  # starting from 0 to 2pi

                # Vertex position (x, y, z)
                x = xy * math.cos(sectorAngle)  # r * cos(u) * cos(v)
                y = xy * math.sin(sectorAngle)  # r * cos(u) * sin(v)
                self.vertices.extend([x, y, z])

                # Normalized vertex normal (nx, ny, nz)
                nx = x * lengthInv
                ny = y * lengthInv
                nz = z * lengthInv

                self.normals.extend([nx, ny, nz])

        self.vertices = np.array(self.vertices).astype(np.float32)
        self.normals = np.array(self.normals).astype(np.float32)

    def compute_normals(self, stack_count, sector_count):
        self.indices = []

        # Generate CCW index list of sphere triangles
        for i in range(stack_count):
            k1 = i * (sector_count + 1)  # beginning of current stack
            k2 = k1 + sector_count + 1  # beginning of next stack

            for j in range(sector_count):
                # 2 triangles per sector excluding first and last stacks
                # k1 => k2 => k1+1
                if i != 0:
                    self.indices.extend([k1, k2, k1 + 1])

                # k1+1 => k2 => k2+1
                if i != (stack_count - 1):
                    self.indices.extend([k1 + 1, k2, k2 + 1])

                k1 += 1
                k2 += 1

        self.indices = np.array(self.indices).astype(np.uint32)

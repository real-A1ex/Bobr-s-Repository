from OpenGL.GL import *
import glfw
import pywavefront
import numpy as np
from PIL import Image

import os


def load_texture(image_path):
    # Load image using PIL
    image = Image.open(image_path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(image.convert("RGBA"), dtype=np.uint8)

    # Generate texture ID
    texture_id = glGenTextures(1)

    # Bind the texture
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Upload texture data
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
    return texture_id

def load_mtl(file_path, folder="models"):
    materials = {}
    current_material = None

    try:
        with open(os.path.join(folder, file_path), 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('newmtl'):
                    parts = line.strip().split()
                    current_material = parts[1]
                    materials[current_material] = {}
                elif line.startswith('Ns'):
                    parts = line.strip().split()
                    materials[current_material]['Ns'] = float(parts[1])
                elif line.startswith('Ni'):
                    parts = line.strip().split()
                    materials[current_material]['Ni'] = float(parts[1])
                elif line.startswith('d'):
                    parts = line.strip().split()
                    materials[current_material]['d'] = float(parts[1])
                elif line.startswith('Tr'):
                    parts = line.strip().split()
                    materials[current_material]['Tr'] = float(parts[1])
                elif line.startswith('Tf'):
                    parts = line.strip().split()
                    materials[current_material]['Tf'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                elif line.startswith('illum'):
                    parts = line.strip().split()
                    materials[current_material]['illum'] = int(parts[1])
                elif line.startswith('Ka'):
                    parts = line.strip().split()
                    materials[current_material]['Ka'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                elif line.startswith('Kd'):
                    parts = line.strip().split()
                    materials[current_material]['Kd'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                elif line.startswith('Ks'):
                    parts = line.strip().split()
                    materials[current_material]['Ks'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                elif line.startswith('Ke'):
                    parts = line.strip().split()
                    materials[current_material]['Ke'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                elif line.startswith('map_Ka'):
                    parts = line.strip().split()
                    materials[current_material]['map_Ka'] = parts[1]
                elif line.startswith('map_Kd'):
                    parts = line.strip().split()
                    materials[current_material]['map_Kd'] = parts[1]
                elif line.startswith('map_bump'):
                    parts = line.strip().split()
                    materials[current_material]['map_bump'] = parts[1]
                elif line.startswith('bump'):
                    parts = line.strip().split()
                    materials[current_material]['bump'] = parts[1]
        return materials
    except Exception as e:
        print(f"An error occurred while loading the MTL file: {e}")
        return None
        
def load_obj(file_path, folder="models"):
    vertices = []
    tex_coords = []
    normals = []
    indices = []
    temp_vertices = []
    temp_tex_coords = []
    temp_normals = []
    materials = {}
    current_material = None

    base_dir = os.path.dirname(file_path)

    try:
        with open(os.path.join(folder, file_path), 'r') as file:
            for line in file:
                if line.startswith('mtllib'):
                    parts = line.strip().split()
                    mtl_file_path = os.path.join(base_dir, parts[1])
                    #materials = load_mtl(mtl_file_path)
                elif line.startswith('usemtl'):
                    parts = line.strip().split()
                    current_material = parts[1]
                elif line.startswith('v '):
                    parts = line.strip().split()
                    temp_vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    temp_tex_coords.append([float(parts[1]), float(parts[2])])
                elif line.startswith('vn '):
                    parts = line.strip().split()
                    temp_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('f '):
                    parts = line.strip().split()
                    face_vertices = []
                    face_tex_coords = []
                    face_normals = []
                    for part in parts[1:]:
                        vals = part.split('/')
                        vertex_idx = int(vals[0]) - 1
                        tex_coord_idx = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else -1
                        normal_idx = int(vals[2]) - 1 if len(vals) > 2 and vals[2] else -1
                        face_vertices.append(temp_vertices[vertex_idx])
                        face_tex_coords.append(temp_tex_coords[tex_coord_idx] if tex_coord_idx != -1 else [0.0, 0.0])
                        face_normals.append(temp_normals[normal_idx] if normal_idx != -1 else [0.0, 0.0, 0.0])
                    
                    # Triangulate the face (assuming it is a convex polygon)
                    for i in range(1, len(face_vertices) - 1):
                        vertices.extend(face_vertices[0])
                        vertices.extend(face_vertices[i])
                        vertices.extend(face_vertices[i + 1])
                        tex_coords.extend(face_tex_coords[0])
                        tex_coords.extend(face_tex_coords[i])
                        tex_coords.extend(face_tex_coords[i + 1])
                        normals.extend(face_normals[0])
                        normals.extend(face_normals[i])
                        normals.extend(face_normals[i + 1])
                        indices.extend([len(indices), len(indices) + 1, len(indices) + 2])

        vertices = np.array(vertices, dtype=np.float32)
        tex_coords = np.array(tex_coords, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, tex_coords, indices, materials
    except Exception as e:
        print(f"An error occurred while loading the OBJ file: {e}")
        return None
    
    
def create_window(window_name, width=800, height=800):
    glfw.init()

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(width, height, window_name, None, None)
    if not window:
        sys.exit(2)
    glfw.make_context_current(window)
    
    glfw.set_input_mode(window, glfw.STICKY_KEYS, True)
    
    return window
    
    
def read_shader_source(file_path):
    with open(os.path.join("shaders", file_path), 'r') as shader_file:
        shader_source = shader_file.read()
    return shader_source

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    # Check for compilation errors
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        raise RuntimeError(glGetShaderInfoLog(shader))
    
    return shader

def create_shader_program(vertex_shader_source, fragment_shader_source):
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        raise RuntimeError(glGetProgramInfoLog(program))
    
    return program
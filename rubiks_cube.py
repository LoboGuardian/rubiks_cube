import pygame
import math
import numpy as np
from typing import List, Tuple, Dict, Optional
import random
import time

# Inicializar Pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CUBE_SIZE = 0.95
CUBE_GAP = 0.08  # Aumentado para mayor separación
GRID_SIZE = 3
ANIMATION_DURATION = 500  # milisegundos
ROTATION_SPEED = 0.002
ZOOM_FACTOR = 550  # Para controlar el tamaño visual

# Colores del cubo de Rubik
COLORS = {
    'RED': (255, 0, 0),
    'ORANGE': (255, 127, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'WHITE': (255, 255, 255),
    'YELLOW': (255, 255, 0),
    'BLACK': (26, 26, 26),
    'GRAY': (128, 128, 128)
}

FACE_COLORS = [
    COLORS['RED'],     # front
    COLORS['ORANGE'],  # back
    COLORS['BLUE'],    # right
    COLORS['GREEN'],   # left
    COLORS['WHITE'],   # up
    COLORS['YELLOW']   # down
]

FACE_NAMES = ['F', 'B', 'R', 'L', 'U', 'D']

class Vector3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3()
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def copy(self):
        return Vector3(self.x, self.y, self.z)

class Matrix4:
    def __init__(self):
        self.m = [[0 for _ in range(4)] for _ in range(4)]
        # Matriz identidad
        for i in range(4):
            self.m[i][i] = 1
    
    @staticmethod
    def rotation_x(angle):
        matrix = Matrix4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[1][1] = cos_a
        matrix.m[1][2] = -sin_a
        matrix.m[2][1] = sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_y(angle):
        matrix = Matrix4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[0][0] = cos_a
        matrix.m[0][2] = sin_a
        matrix.m[2][0] = -sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_z(angle):
        matrix = Matrix4()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        matrix.m[0][0] = cos_a
        matrix.m[0][1] = -sin_a
        matrix.m[1][0] = sin_a
        matrix.m[1][1] = cos_a
        return matrix
    
    @staticmethod
    def rotation_axis(axis: Vector3, angle: float):
        """Rotación alrededor de un eje arbitrario"""
        axis = axis.normalize()
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        one_minus_cos = 1 - cos_a
        
        matrix = Matrix4()
        matrix.m[0][0] = cos_a + axis.x * axis.x * one_minus_cos
        matrix.m[0][1] = axis.x * axis.y * one_minus_cos - axis.z * sin_a
        matrix.m[0][2] = axis.x * axis.z * one_minus_cos + axis.y * sin_a
        
        matrix.m[1][0] = axis.y * axis.x * one_minus_cos + axis.z * sin_a
        matrix.m[1][1] = cos_a + axis.y * axis.y * one_minus_cos
        matrix.m[1][2] = axis.y * axis.z * one_minus_cos - axis.x * sin_a
        
        matrix.m[2][0] = axis.z * axis.x * one_minus_cos - axis.y * sin_a
        matrix.m[2][1] = axis.z * axis.y * one_minus_cos + axis.x * sin_a
        matrix.m[2][2] = cos_a + axis.z * axis.z * one_minus_cos
        
        return matrix
    
    def multiply(self, other):
        result = Matrix4()
        for i in range(4):
            for j in range(4):
                result.m[i][j] = 0
                for k in range(4):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result
    
    def transform_vector(self, vector: Vector3):
        x = vector.x * self.m[0][0] + vector.y * self.m[0][1] + vector.z * self.m[0][2] + self.m[0][3]
        y = vector.x * self.m[1][0] + vector.y * self.m[1][1] + vector.z * self.m[1][2] + self.m[1][3]
        z = vector.x * self.m[2][0] + vector.y * self.m[2][1] + vector.z * self.m[2][2] + self.m[2][3]
        return Vector3(x, y, z)

class GridPosition:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
    
    def copy(self):
        return GridPosition(self.x, self.y, self.z)

class SmallCube:
    def __init__(self, grid_position: GridPosition):
        self.grid_position = grid_position.copy()
        self.position = self.get_world_position()
        self.rotation_matrix = Matrix4()
        self.id = f"{grid_position.x}-{grid_position.y}-{grid_position.z}"
        self.colors = self.get_face_colors()
    
    def get_world_position(self) -> Vector3:
        offset = CUBE_SIZE + CUBE_GAP
        return Vector3(
            (self.grid_position.x - 1) * offset,
            (self.grid_position.y - 1) * offset,
            (self.grid_position.z - 1) * offset
        )
    
    def get_face_colors(self) -> List[Tuple[int, int, int]]:
        """Retorna los colores de las caras en orden: derecha, izquierda, arriba, abajo, frente, atrás"""
        colors = []
        x, y, z = self.grid_position.x, self.grid_position.y, self.grid_position.z
        
        # Derecha (x=2), Izquierda (x=0), Arriba (y=2), Abajo (y=0), Frente (z=2), Atrás (z=0)
        colors.append(FACE_COLORS[2] if x == 2 else COLORS['BLACK'])  # derecha
        colors.append(FACE_COLORS[3] if x == 0 else COLORS['BLACK'])  # izquierda
        colors.append(FACE_COLORS[4] if y == 2 else COLORS['BLACK'])  # arriba
        colors.append(FACE_COLORS[5] if y == 0 else COLORS['BLACK'])  # abajo
        colors.append(FACE_COLORS[0] if z == 2 else COLORS['BLACK'])  # frente
        colors.append(FACE_COLORS[1] if z == 0 else COLORS['BLACK'])  # atrás
        
        return colors
    
    def get_vertices(self) -> List[Vector3]:
        """Retorna los 8 vértices del cubo"""
        size = CUBE_SIZE / 2
        vertices = [
            Vector3(-size, -size, -size),  # 0
            Vector3(size, -size, -size),   # 1
            Vector3(size, size, -size),    # 2
            Vector3(-size, size, -size),   # 3
            Vector3(-size, -size, size),   # 4
            Vector3(size, -size, size),    # 5
            Vector3(size, size, size),     # 6
            Vector3(-size, size, size)     # 7
        ]
        
        # Aplicar rotación y posición
        transformed_vertices = []
        for vertex in vertices:
            # Aplicar rotación
            rotated = self.rotation_matrix.transform_vector(vertex)
            # Aplicar posición
            final_pos = rotated + self.position
            transformed_vertices.append(final_pos)
        
        return transformed_vertices

class Camera:
    def __init__(self):
        self.position = Vector3(6, 5, 6)
        self.target = Vector3(0, 0, 0)
        self.up = Vector3(0, 1, 0)
        self.fov = 60
        self.near = 0.1
        self.far = 1000
    
    def get_view_matrix(self):
        forward = (self.target - self.position).normalize()
        right = forward.cross(self.up).normalize()
        up = right.cross(forward)
        
        view = Matrix4()
        view.m[0][0] = right.x
        view.m[0][1] = right.y
        view.m[0][2] = right.z
        view.m[0][3] = -right.dot(self.position)
        
        view.m[1][0] = up.x
        view.m[1][1] = up.y
        view.m[1][2] = up.z
        view.m[1][3] = -up.dot(self.position)
        
        view.m[2][0] = -forward.x
        view.m[2][1] = -forward.y
        view.m[2][2] = -forward.z
        view.m[2][3] = forward.dot(self.position)
        
        return view
    
    def project_point(self, point: Vector3, screen_width: int, screen_height: int) -> Tuple[int, int, float]:
        """Proyecta un punto 3D a coordenadas de pantalla con perspectiva mejorada"""
        # Calcular vector desde cámara al punto
        cam_to_point = point - self.position
        
        # Crear sistema de coordenadas de la cámara
        forward = (self.target - self.position).normalize()
        right = forward.cross(self.up).normalize()
        up = right.cross(forward)
        
        # Transformar punto a espacio de cámara
        local_x = cam_to_point.dot(right)
        local_y = cam_to_point.dot(up)
        local_z = cam_to_point.dot(forward)
        
        # Verificar si está delante de la cámara
        if local_z > 0.1:
            # Proyección perspectiva mejorada
            screen_x = int(screen_width / 2 + (local_x * ZOOM_FACTOR) / local_z)
            screen_y = int(screen_height / 2 - (local_y * ZOOM_FACTOR) / local_z)
            
            return screen_x, screen_y, local_z
        
        return -1000, -1000, float('inf')

class RubiksCube:
    def __init__(self):
        self.cubes: List[SmallCube] = []
        self.rotation_x = 0
        self.rotation_y = 0
        self.camera = Camera()
        self.is_animating = False
        self.animation_start_time = 0
        self.animating_cubes = []
        self.animation_axis = Vector3()
        self.animation_angle = 0
        self.target_rotation_matrices = []
        
        self.create_cubes()
    
    def create_cubes(self):
        """Crea todos los cubitos del cubo de Rubik"""
        self.cubes = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                for z in range(GRID_SIZE):
                    cube = SmallCube(GridPosition(x, y, z))
                    self.cubes.append(cube)
    
    def get_face_cubes(self, face_name: str) -> List[SmallCube]:
        """Retorna los cubitos de una cara específica"""
        face_cubes = []
        
        for cube in self.cubes:
            pos = cube.grid_position
            should_include = False
            
            if face_name == 'F' and pos.z == 2:
                should_include = True
            elif face_name == 'B' and pos.z == 0:
                should_include = True
            elif face_name == 'R' and pos.x == 2:
                should_include = True
            elif face_name == 'L' and pos.x == 0:
                should_include = True
            elif face_name == 'U' and pos.y == 2:
                should_include = True
            elif face_name == 'D' and pos.y == 0:
                should_include = True
            
            if should_include:
                face_cubes.append(cube)
        
        return face_cubes
    
    def get_rotation_axis(self, face_name: str) -> Vector3:
        """Retorna el eje de rotación para una cara"""
        axes = {
            'F': Vector3(0, 0, 1),
            'B': Vector3(0, 0, -1),
            'R': Vector3(1, 0, 0),
            'L': Vector3(-1, 0, 0),
            'U': Vector3(0, 1, 0),
            'D': Vector3(0, -1, 0)
        }
        return axes.get(face_name, Vector3(0, 1, 0))
    
    def rotate_face(self, face_name: str):
        """Inicia la animación de rotación de una cara"""
        if self.is_animating:
            return
        
        self.is_animating = True
        self.animation_start_time = pygame.time.get_ticks()
        self.animating_cubes = self.get_face_cubes(face_name)
        self.animation_axis = self.get_rotation_axis(face_name)
        self.animation_angle = math.pi / 2
        
        # Guardar las matrices de rotación objetivo
        self.target_rotation_matrices = []
        rotation_matrix = Matrix4.rotation_axis(self.animation_axis, self.animation_angle)
        
        for cube in self.animating_cubes:
            target_matrix = cube.rotation_matrix.multiply(rotation_matrix)
            self.target_rotation_matrices.append(target_matrix)
    
    def update_animation(self):
        """Actualiza la animación de rotación con interpolación"""
        if not self.is_animating:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start_time
        progress = min(elapsed / ANIMATION_DURATION, 1.0)
        
        # Easing function (ease out back)
        if progress == 1.0:
            eased_progress = 1.0
        else:
            c1 = 1.70158
            c3 = c1 + 1
            eased_progress = 1 + c3 * pow(progress - 1, 3) + c1 * pow(progress - 1, 2)
        
        # Interpolación temporal para animación suave
        current_angle = self.animation_angle * eased_progress
        temp_rotation_matrix = Matrix4.rotation_axis(self.animation_axis, current_angle)
        
        # Aplicar rotación temporal a los cubitos
        for i, cube in enumerate(self.animating_cubes):
            # Posición base sin rotación
            base_pos = cube.get_world_position()
            
            # Calcular posición rotada temporalmente
            relative_pos = base_pos
            rotated_relative = temp_rotation_matrix.transform_vector(relative_pos)
            cube.position = rotated_relative
            
            # Actualizar matriz de rotación temporal
            if i < len(self.target_rotation_matrices):
                base_matrix = Matrix4()
                cube.rotation_matrix = base_matrix.multiply(temp_rotation_matrix)
        
        # Finalizar animación
        if progress >= 1.0:
            self.finish_animation()
    
    def finish_animation(self):
        """Finaliza la animación y actualiza las posiciones de los cubitos"""
        self.is_animating = False
        
        # Actualizar posiciones de los cubitos después de la rotación
        for cube in self.animating_cubes:
            self.update_cube_grid_position(cube)
            cube.position = cube.get_world_position()
            cube.colors = cube.get_face_colors()
    
    def update_cube_grid_position(self, cube: SmallCube):
        """Actualiza la posición de grilla después de una rotación"""
        # Esta es una simplificación. En una implementación completa,
        # necesitarías calcular las nuevas posiciones basándose en la rotación
        # Por ahora, mantenemos las posiciones originales
        pass
    
    def scramble(self):
        """Mezcla el cubo con movimientos aleatorios"""
        if self.is_animating:
            return
        
        # Realizar múltiples rotaciones rápidas para mezclar
        moves = 15
        for i in range(moves):
            face = random.choice(FACE_NAMES)
            # Para una mezcla real, aplicaríamos las rotaciones sin animación
            self.apply_face_rotation_immediately(face)
    
    def apply_face_rotation_immediately(self, face_name: str):
        """Aplica una rotación de cara inmediatamente sin animación"""
        face_cubes = self.get_face_cubes(face_name)
        axis = self.get_rotation_axis(face_name)
        angle = math.pi / 2
        
        rotation_matrix = Matrix4.rotation_axis(axis, angle)
        
        for cube in face_cubes:
            # Aplicar rotación
            cube.rotation_matrix = cube.rotation_matrix.multiply(rotation_matrix)
            
            # Actualizar posición (simplificado)
            old_pos = cube.position.copy()
            
            # Rotar posición alrededor del origen
            if face_name in ['F', 'B']:
                # Rotación en Z
                if face_name == 'F':
                    new_x = -old_pos.y
                    new_y = old_pos.x
                    cube.position = Vector3(new_x, new_y, old_pos.z)
                else:
                    new_x = old_pos.y
                    new_y = -old_pos.x
                    cube.position = Vector3(new_x, new_y, old_pos.z)
            elif face_name in ['R', 'L']:
                # Rotación en X
                if face_name == 'R':
                    new_y = -old_pos.z
                    new_z = old_pos.y
                    cube.position = Vector3(old_pos.x, new_y, new_z)
                else:
                    new_y = old_pos.z
                    new_z = -old_pos.y
                    cube.position = Vector3(old_pos.x, new_y, new_z)
            elif face_name in ['U', 'D']:
                # Rotación en Y
                if face_name == 'U':
                    new_x = old_pos.z
                    new_z = -old_pos.x
                    cube.position = Vector3(new_x, old_pos.y, new_z)
                else:
                    new_x = -old_pos.z
                    new_z = old_pos.x
                    cube.position = Vector3(new_x, old_pos.y, new_z)
            
            # Actualizar grid position basándose en nueva posición
            self.update_cube_grid_position_from_world(cube)
            cube.colors = cube.get_face_colors()
    
    def update_cube_grid_position_from_world(self, cube: SmallCube):
        """Actualiza la posición de grid basándose en la posición mundial"""
        offset = CUBE_SIZE + CUBE_GAP
        
        # Convertir posición mundial a coordenadas de grid
        grid_x = round((cube.position.x / offset) + 1)
        grid_y = round((cube.position.y / offset) + 1)
        grid_z = round((cube.position.z / offset) + 1)
        
        # Asegurar que están en el rango válido
        grid_x = max(0, min(2, grid_x))
        grid_y = max(0, min(2, grid_y))
        grid_z = max(0, min(2, grid_z))
        
        cube.grid_position = GridPosition(grid_x, grid_y, grid_z)
    
    def solve(self):
        """Resetea el cubo a su estado resuelto"""
        if self.is_animating:
            return
        
        self.create_cubes()
    
    def update_rotation(self, delta_x: float, delta_y: float):
        """Actualiza la rotación global del cubo"""
        if self.is_animating:
            return
        
        self.rotation_y += delta_x * 0.005
        self.rotation_x += delta_y * 0.005
        
        # Aplicar rotación a todos los cubitos
        for cube in self.cubes:
            # Obtener posición base del cubo
            base_position = cube.get_world_position()
            
            # Crear matriz de rotación global
            rot_y = Matrix4.rotation_y(self.rotation_y)
            rot_x = Matrix4.rotation_x(self.rotation_x)
            global_rotation = rot_y.multiply(rot_x)
            
            # Aplicar rotación a la posición base
            rotated_pos = global_rotation.transform_vector(base_position)
            cube.position = rotated_pos
    
    def draw_cube_face(self, screen, vertices: List[Vector3], face_indices: List[int], color: Tuple[int, int, int]):
        """Dibuja una cara del cubo con sombreado"""
        # Proyectar vértices a 2D
        screen_points = []
        valid_points = 0
        
        for i in face_indices:
            x, y, distance = self.camera.project_point(vertices[i], WINDOW_WIDTH, WINDOW_HEIGHT)
            screen_points.append((x, y))
            
            # Contar puntos válidos
            if -200 <= x <= WINDOW_WIDTH + 200 and -200 <= y <= WINDOW_HEIGHT + 200 and distance < 50:
                valid_points += 1
        
        # Solo renderizar si tenemos suficientes puntos válidos
        if valid_points >= 3:
            # Calcular normal de la cara para backface culling y sombreado
            if len(face_indices) >= 3:
                v1 = vertices[face_indices[1]] - vertices[face_indices[0]]
                v2 = vertices[face_indices[2]] - vertices[face_indices[0]]
                normal = v1.cross(v2).normalize()
                
                # Vector hacia la cámara
                face_center = vertices[face_indices[0]]
                to_camera = (self.camera.position - face_center).normalize()
                
                # Solo dibujar caras que miran hacia la cámara
                if normal.dot(to_camera) > 0:
                    try:
                        if color != COLORS['BLACK']:
                            # Calcular sombreado básico
                            light_dir = Vector3(0.5, 0.7, 0.3).normalize()  # Luz direccional
                            lighting = max(0.3, normal.dot(light_dir))  # Mínimo 30% de luz
                            
                            # Aplicar sombreado al color
                            shaded_color = (
                                int(color[0] * lighting),
                                int(color[1] * lighting),
                                int(color[2] * lighting)
                            )
                            
                            pygame.draw.polygon(screen, shaded_color, screen_points)
                            pygame.draw.polygon(screen, (0, 0, 0), screen_points, 1)
                        else:
                            # Caras internas con sombreado sutil
                            pygame.draw.polygon(screen, (20, 20, 25), screen_points)
                            pygame.draw.polygon(screen, (0, 0, 0), screen_points, 1)
                    except ValueError:
                        pass
    
    def render(self, screen):
        """Renderiza el cubo completo"""
        self.update_animation()
        
        # Definir las caras del cubo con orden correcto de vértices
        faces = [
            ([1, 5, 6, 2], 0),  # derecha (x+)
            ([4, 0, 3, 7], 1),  # izquierda (x-)
            ([3, 2, 6, 7], 2),  # arriba (y+)
            ([0, 4, 5, 1], 3),  # abajo (y-)
            ([5, 4, 7, 6], 4),  # frente (z+)
            ([0, 1, 2, 3], 5)   # atrás (z-)
        ]
        
        # Recopilar todas las caras con su distancia para ordenamiento
        all_faces = []
        
        for cube in self.cubes:
            vertices = cube.get_vertices()
            cube_center = cube.position
            distance_to_camera = (cube_center - self.camera.position).length()
            
            for face_indices, color_index in faces:
                # Calcular centro de la cara
                face_center = Vector3()
                for idx in face_indices:
                    face_center = face_center + vertices[idx]
                face_center = face_center * (1.0 / len(face_indices))
                
                face_distance = (face_center - self.camera.position).length()
                
                all_faces.append({
                    'vertices': vertices,
                    'indices': face_indices,
                    'color': cube.colors[color_index],
                    'distance': face_distance
                })
        
        # Ordenar caras por distancia (más lejanas primero)
        all_faces.sort(key=lambda x: x['distance'], reverse=True)
        
        # Renderizar todas las caras ordenadas
        for face in all_faces:
            self.draw_cube_face(screen, face['vertices'], face['indices'], face['color'])

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cubo de Rubik 3D")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Ventana adicional para mostrar las caras desplegadas
        self.face_window = None
        self.show_faces = False
        self.face_window_size = (600, 450)
        
        self.cube = RubiksCube()
        self.mouse_down = False
        self.last_mouse_pos = (0, 0)
        self.zoom_level = 1.0
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
    def toggle_face_window(self):
        """Alterna la ventana de caras desplegadas"""
        self.show_faces = not self.show_faces
        if self.show_faces and self.face_window is None:
            # Crear ventana secundaria
            self.face_window = pygame.display.set_mode(self.face_window_size, pygame.RESIZABLE)
            pygame.display.set_caption("Caras del Cubo - Vista Desplegada")
        elif not self.show_faces:
            self.face_window = None
            # Restaurar ventana principal
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Cubo de Rubik 3D")
    
    def draw_face_grid(self, surface, face_data, x_offset, y_offset, face_size, face_name):
        """Dibuja una cara del cubo como una grilla 3x3"""
        cell_size = face_size // 3
        
        # Título de la cara
        title_text = self.font.render(face_name, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x_offset + face_size // 2, y_offset - 25))
        surface.blit(title_text, title_rect)
        
        # Dibujar grilla 3x3
        for row in range(3):
            for col in range(3):
                x = x_offset + col * cell_size
                y = y_offset + row * cell_size
                
                # Determinar color basado en la posición y cara
                color = self.get_face_color_at_position(face_name, col, row)
                
                # Dibujar celda
                cell_rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(surface, color, cell_rect)
                pygame.draw.rect(surface, (0, 0, 0), cell_rect, 2)
                
                # Añadir brillo/sombra para efecto 3D
                highlight_rect = pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4)
                highlight_color = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(surface, highlight_color, highlight_rect, 1)
    
    def get_face_color_at_position(self, face_name, col, row):
        """Obtiene el color de una posición específica en una cara"""
        # Mapear cara y posición a coordenadas de grid 3D
        face_mapping = {
            'U': lambda c, r: (c, 2, r),      # Arriba
            'D': lambda c, r: (c, 0, 2-r),   # Abajo  
            'F': lambda c, r: (c, 2-r, 2),   # Frente
            'B': lambda c, r: (2-c, 2-r, 0), # Atrás
            'R': lambda c, r: (2, 2-r, 2-c), # Derecha
            'L': lambda c, r: (0, 2-r, c)    # Izquierda
        }
        
        if face_name in face_mapping:
            grid_x, grid_y, grid_z = face_mapping[face_name](col, row)
            
            # Buscar el cubito en esa posición
            for cube in self.cube.cubes:
                if (cube.grid_position.x == grid_x and 
                    cube.grid_position.y == grid_y and 
                    cube.grid_position.z == grid_z):
                    
                    # Determinar qué cara del cubito corresponde a la cara del cubo
                    face_index = self.get_cube_face_index(face_name, cube.grid_position)
                    return cube.colors[face_index]
        
        return (50, 50, 50)  # Color por defecto
    
    def get_cube_face_index(self, face_name, grid_pos):
        """Obtiene el índice de la cara del cubito que corresponde a la cara del cubo"""
        # Índices: 0=derecha, 1=izquierda, 2=arriba, 3=abajo, 4=frente, 5=atrás
        if face_name == 'U':
            return 2  # arriba
        elif face_name == 'D':
            return 3  # abajo
        elif face_name == 'F':
            return 4  # frente
        elif face_name == 'B':
            return 5  # atrás
        elif face_name == 'R':
            return 0  # derecha
        elif face_name == 'L':
            return 1  # izquierda
        return 0
    
    def draw_cube_net(self, surface):
        """Dibuja el patrón desplegado del cubo (net)"""
        surface.fill((40, 40, 50))
        
        face_size = 100
        margin = 20
        
        # Título principal
        title = self.title_font.render("Cube Faces - Unfolded View", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.face_window_size[0] // 2, 30))
        surface.blit(title, title_rect)
        
        # Layout del patrón desplegado (cruz):
        #     [U]
        # [L] [F] [R] [B]
        #     [D]
        
        base_x = self.face_window_size[0] // 2 - face_size * 2
        base_y = 80
        
        # Posiciones de las caras
        face_positions = {
            'U': (base_x + face_size, base_y),                    # Arriba
            'L': (base_x, base_y + face_size),                    # Izquierda  
            'F': (base_x + face_size, base_y + face_size),        # Frente
            'R': (base_x + face_size * 2, base_y + face_size),    # Derecha
            'B': (base_x + face_size * 3, base_y + face_size),    # Atrás
            'D': (base_x + face_size, base_y + face_size * 2)     # Abajo
        }
        
        # Dibujar cada cara
        for face_name, (x, y) in face_positions.items():
            self.draw_face_grid(surface, None, x, y, face_size, face_name)
        
        # Instrucciones
        instructions = [
            "Press T to toggle this window",
            "Each 3x3 grid shows one face of the cube",
            "Colors update in real-time as you rotate faces"
        ]
        
        y_offset = base_y + face_size * 3 + 40
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.face_window_size[0] // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 25
        
    def handle_events(self):
        global ZOOM_FACTOR
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botón izquierdo
                    # Verificar si se hizo clic en botones de la UI
                    if self.handle_ui_click(event.pos):
                        continue
                    self.mouse_down = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Scroll up - zoom in
                    ZOOM_FACTOR = min(ZOOM_FACTOR + 20, 600)
                elif event.button == 5:  # Scroll down - zoom out
                    ZOOM_FACTOR = max(ZOOM_FACTOR - 20, 150)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_down and not self.show_faces:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.cube.update_rotation(dx, dy)
                    self.last_mouse_pos = event.pos
            
            elif event.type == pygame.KEYDOWN:
                # Controles de teclado para rotaciones
                if event.key == pygame.K_f:
                    self.cube.rotate_face('F')
                elif event.key == pygame.K_b:
                    self.cube.rotate_face('B')
                elif event.key == pygame.K_r:
                    self.cube.rotate_face('R')
                elif event.key == pygame.K_l:
                    self.cube.rotate_face('L')
                elif event.key == pygame.K_u:
                    self.cube.rotate_face('U')
                elif event.key == pygame.K_d:
                    self.cube.rotate_face('D')
                elif event.key == pygame.K_s:
                    self.cube.scramble()
                elif event.key == pygame.K_SPACE:
                    self.cube.solve()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_t:  # Toggle face window
                    self.toggle_face_window()
                # Controles de zoom con teclado
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    ZOOM_FACTOR = min(ZOOM_FACTOR + 30, 600)
                elif event.key == pygame.K_MINUS:
                    ZOOM_FACTOR = max(ZOOM_FACTOR - 30, 150)
    
    def handle_ui_click(self, pos):
        """Maneja clics en la interfaz de usuario mejorada"""
        x, y = pos
        
        # Verificar botones de caras con nuevas dimensiones
        y_pos = 135  # Ajustado para la nueva interfaz
        button_width = 70
        button_height = 45
        
        for i, face in enumerate(FACE_NAMES):
            button_x = WINDOW_WIDTH - 250 + (i % 3) * 80
            button_y = y_pos + (i // 3) * 55
            
            if (button_x <= x <= button_x + button_width and 
                button_y <= y <= button_y + button_height and 
                not self.cube.is_animating):
                self.cube.rotate_face(face)
                return True
        
        # Verificar botón Scramble con nuevas coordenadas
        scramble_rect = pygame.Rect(WINDOW_WIDTH - 250, 315, 200, 45)
        if scramble_rect.collidepoint(pos) and not self.cube.is_animating:
            self.cube.scramble()
            return True
        
        # Verificar botón Solve con nuevas coordenadas
        solve_rect = pygame.Rect(WINDOW_WIDTH - 250, 370, 200, 45)
        if solve_rect.collidepoint(pos) and not self.cube.is_animating:
            self.cube.solve()
            return True
        
        # Verificar botón Face View
        face_view_rect = pygame.Rect(WINDOW_WIDTH - 250, 425, 200, 45)
        if face_view_rect.collidepoint(pos):
            self.toggle_face_window()
            return True
        
        return False
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario mejorada"""
        # Fondo del panel de control con gradiente
        panel_rect = pygame.Rect(WINDOW_WIDTH - 280, 0, 280, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_rect)
        pygame.draw.line(self.screen, (80, 80, 100), (WINDOW_WIDTH - 280, 0), (WINDOW_WIDTH - 280, WINDOW_HEIGHT), 3)
        
        # Título principal
        title = self.title_font.render("Rubik's Cube", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH - 140, 40))
        self.screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.small_font.render("3D Interactive", True, (180, 180, 200))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH - 140, 65))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Sección de botones de caras
        face_section_y = 100
        section_title = self.font.render("Face Rotations", True, (200, 200, 220))
        self.screen.blit(section_title, (WINDOW_WIDTH - 270, face_section_y))
        
        # Botones de caras con colores
        y_pos = face_section_y + 35
        button_width = 70
        button_height = 45
        
        face_colors_ui = {
            'F': (220, 60, 60),   # Rojo más suave
            'B': (255, 140, 60),  # Naranja
            'R': (60, 60, 220),   # Azul
            'L': (60, 220, 60),   # Verde
            'U': (240, 240, 240), # Blanco
            'D': (240, 240, 60)   # Amarillo
        }
        
        for i, face in enumerate(FACE_NAMES):
            x = WINDOW_WIDTH - 250 + (i % 3) * 80
            y = y_pos + (i // 3) * 55
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Color del botón basado en la cara
            if not self.cube.is_animating:
                base_color = face_colors_ui[face]
                # Efecto hover simulado
                color = tuple(min(255, c + 20) for c in base_color)
            else:
                color = (100, 100, 100)
            
            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2, border_radius=8)
            
            # Sombra del texto
            shadow_text = self.font.render(face, True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(button_rect.centerx + 1, button_rect.centery + 1))
            self.screen.blit(shadow_text, shadow_rect)
            
            # Texto principal
            text_color = (0, 0, 0) if face == 'U' or face == 'D' else (255, 255, 255)
            text = self.font.render(face, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # Sección de acciones
        action_section_y = 280
        action_title = self.font.render("Actions", True, (200, 200, 220))
        self.screen.blit(action_title, (WINDOW_WIDTH - 270, action_section_y))
        
        # Botón Scramble
        scramble_rect = pygame.Rect(WINDOW_WIDTH - 250, action_section_y + 35, 200, 45)
        scramble_color = (200, 60, 60) if not self.cube.is_animating else (100, 100, 100)
        pygame.draw.rect(self.screen, scramble_color, scramble_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), scramble_rect, 2, border_radius=10)
        
        scramble_text = self.font.render("Scramble (S)", True, (255, 255, 255))
        scramble_text_rect = scramble_text.get_rect(center=scramble_rect.center)
        self.screen.blit(scramble_text, scramble_text_rect)
        
        # Botón Solve
        solve_rect = pygame.Rect(WINDOW_WIDTH - 250, action_section_y + 90, 200, 45)
        solve_color = (60, 200, 60) if not self.cube.is_animating else (100, 100, 100)
        pygame.draw.rect(self.screen, solve_color, solve_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), solve_rect, 2, border_radius=10)
        
        solve_text = self.font.render("Solve (Space)", True, (255, 255, 255))
        solve_text_rect = solve_text.get_rect(center=solve_rect.center)
        self.screen.blit(solve_text, solve_text_rect)
        
        # Botón Face View
        face_view_rect = pygame.Rect(WINDOW_WIDTH - 250, action_section_y + 145, 200, 45)
        face_view_color = (100, 100, 200) if not self.show_faces else (150, 150, 250)
        pygame.draw.rect(self.screen, face_view_color, face_view_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), face_view_rect, 2, border_radius=10)
        
        face_view_text = self.font.render("Face View (T)", True, (255, 255, 255))
        face_view_text_rect = face_view_text.get_rect(center=face_view_rect.center)
        self.screen.blit(face_view_text, face_view_text_rect)
        
        # Información de zoom (ajustada hacia abajo)
        zoom_section_y = 480
        zoom_title = self.font.render("Zoom", True, (200, 200, 220))
        self.screen.blit(zoom_title, (WINDOW_WIDTH - 270, zoom_section_y))
        
        zoom_info = self.small_font.render(f"Level: {ZOOM_FACTOR}", True, (180, 180, 200))
        self.screen.blit(zoom_info, (WINDOW_WIDTH - 270, zoom_section_y + 25))
        
        zoom_controls = self.small_font.render("Mouse Wheel / +/-", True, (150, 150, 170))
        self.screen.blit(zoom_controls, (WINDOW_WIDTH - 270, zoom_section_y + 45))
        
        # Sección de controles (ajustada hacia abajo)
        controls_section_y = 550
        controls_title = self.font.render("Controls", True, (200, 200, 220))
        self.screen.blit(controls_title, (WINDOW_WIDTH - 270, controls_section_y))
        
        instructions = [
            "• Drag: Rotate cube",
            "• F/B: Front/Back",
            "• R/L: Right/Left", 
            "• U/D: Up/Down",
            "• S: Scramble",
            "• Space: Solve",
            "• T: Toggle Face View",
            "• ESC: Exit"
        ]
        
        y_offset = controls_section_y + 30
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (180, 180, 200))
            self.screen.blit(text, (WINDOW_WIDTH - 270, y_offset))
            y_offset += 20  # Reducido para que quepa todo
        
        # Estado de animación y vista de caras
        status_y = WINDOW_HEIGHT - 50
        if self.cube.is_animating:
            status_text = self.small_font.render("Animating...", True, (255, 200, 100))
            self.screen.blit(status_text, (WINDOW_WIDTH - 270, status_y))
            status_y += 20
        
        if self.show_faces:
            face_status = self.small_font.render("Face View: ON", True, (100, 255, 100))
            self.screen.blit(face_status, (WINDOW_WIDTH - 270, status_y))
            y_pos += 25
    
    def run(self):
        while self.running:
            self.handle_events()
            
            # Limpiar pantalla
            self.screen.fill((20, 20, 20))
            
            # Renderizar cubo
            self.cube.render(self.screen)
            
            # Dibujar UI
            self.draw_ui()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
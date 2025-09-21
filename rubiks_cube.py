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
CUBE_GAP = 0.05
GRID_SIZE = 3
ANIMATION_DURATION = 500  # milisegundos
ROTATION_SPEED = 0.002

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
        self.position = Vector3(5, 4, 5)
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
    
    def project_point(self, point: Vector3, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Proyecta un punto 3D a coordenadas de pantalla"""
        # Transformar a espacio de cámara
        view_matrix = self.get_view_matrix()
        view_point = view_matrix.transform_vector(point)
        
        # Proyección perspectiva
        if view_point.z > 0:
            aspect = screen_width / screen_height
            fov_rad = math.radians(self.fov)
            
            x = view_point.x / (view_point.z * math.tan(fov_rad / 2))
            y = view_point.y / (view_point.z * math.tan(fov_rad / 2) / aspect)
            
            # Convertir a coordenadas de pantalla
            screen_x = int((x + 1) * screen_width / 2)
            screen_y = int((1 - y) * screen_height / 2)
            
            return screen_x, screen_y
        
        return -1000, -1000  # Punto detrás de la cámara

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
        """Actualiza la animación de rotación"""
        if not self.is_animating:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start_time
        progress = min(elapsed / ANIMATION_DURATION, 1.0)
        
        # Easing function (ease out cubic)
        eased_progress = 1 - (1 - progress) ** 3
        current_angle = self.animation_angle * eased_progress
        
        # Aplicar rotación a los cubitos
        rotation_matrix = Matrix4.rotation_axis(self.animation_axis, current_angle)
        
        for i, cube in enumerate(self.animating_cubes):
            cube.rotation_matrix = self.target_rotation_matrices[i]
        
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
        
        self.rotation_y += delta_x * 0.01
        self.rotation_x += delta_y * 0.01
        
        # Aplicar rotación a todos los cubitos
        for cube in self.cubes:
            # Crear matriz de rotación global
            rot_y = Matrix4.rotation_y(self.rotation_y)
            rot_x = Matrix4.rotation_x(self.rotation_x)
            global_rotation = rot_y.multiply(rot_x)
            
            # Aplicar a la posición
            rotated_pos = global_rotation.transform_vector(cube.get_world_position())
            cube.position = rotated_pos
    
    def draw_cube_face(self, screen, vertices: List[Vector3], face_indices: List[int], color: Tuple[int, int, int]):
        """Dibuja una cara del cubo"""
        # Proyectar vértices a 2D
        screen_points = []
        for i in face_indices:
            x, y = self.camera.project_point(vertices[i], WINDOW_WIDTH, WINDOW_HEIGHT)
            screen_points.append((x, y))
        
        # Verificar si todos los puntos están en pantalla
        if all(0 <= x <= WINDOW_WIDTH and 0 <= y <= WINDOW_HEIGHT for x, y in screen_points):
            # Calcular normal de la cara para determinar si es visible
            v1 = vertices[face_indices[1]] - vertices[face_indices[0]]
            v2 = vertices[face_indices[2]] - vertices[face_indices[0]]
            normal = v1.cross(v2)
            
            # Vector hacia la cámara
            to_camera = self.camera.position - vertices[face_indices[0]]
            
            # Solo dibujar si la cara está orientada hacia la cámara
            if normal.dot(to_camera) > 0:
                pygame.draw.polygon(screen, color, screen_points)
                pygame.draw.polygon(screen, COLORS['BLACK'], screen_points, 2)
    
    def render(self, screen):
        """Renderiza el cubo completo"""
        self.update_animation()
        
        # Definir las caras del cubo (índices de vértices)
        faces = [
            ([1, 5, 6, 2], 0),  # derecha
            ([4, 0, 3, 7], 1),  # izquierda
            ([3, 2, 6, 7], 2),  # arriba
            ([0, 1, 5, 4], 3),  # abajo
            ([4, 5, 6, 7], 4),  # frente
            ([0, 3, 2, 1], 5)   # atrás
        ]
        
        # Ordenar cubitos por distancia a la cámara para renderizado correcto
        cubes_with_distance = []
        for cube in self.cubes:
            distance = (cube.position - self.camera.position).length()
            cubes_with_distance.append((cube, distance))
        
        # Ordenar por distancia (más lejanos primero)
        cubes_with_distance.sort(key=lambda x: x[1], reverse=True)
        
        # Renderizar cada cubo
        for cube, _ in cubes_with_distance:
            vertices = cube.get_vertices()
            
            for face_indices, color_index in faces:
                color = cube.colors[color_index]
                self.draw_cube_face(screen, vertices, face_indices, color)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cubo de Rubik 3D")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.cube = RubiksCube()
        self.mouse_down = False
        self.last_mouse_pos = (0, 0)
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self):
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
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_down:
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
    
    def handle_ui_click(self, pos):
        """Maneja clics en la interfaz de usuario"""
        x, y = pos
        
        # Verificar botones de caras
        y_pos = 80
        button_width = 60
        button_height = 40
        
        for i, face in enumerate(FACE_NAMES):
            button_x = WINDOW_WIDTH - 220 + (i % 3) * 70
            button_y = y_pos + (i // 3) * 50
            
            if (button_x <= x <= button_x + button_width and 
                button_y <= y <= button_y + button_height and 
                not self.cube.is_animating):
                self.cube.rotate_face(face)
                return True
        
        # Verificar botón Scramble
        scramble_rect = pygame.Rect(WINDOW_WIDTH - 220, 250, 180, 40)
        if scramble_rect.collidepoint(pos) and not self.cube.is_animating:
            self.cube.scramble()
            return True
        
        # Verificar botón Solve
        solve_rect = pygame.Rect(WINDOW_WIDTH - 220, 310, 180, 40)
        if solve_rect.collidepoint(pos) and not self.cube.is_animating:
            self.cube.solve()
            return True
        
        return False
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Fondo del panel de control
        panel_rect = pygame.Rect(WINDOW_WIDTH - 250, 0, 250, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
        pygame.draw.line(self.screen, (80, 80, 80), (WINDOW_WIDTH - 250, 0), (WINDOW_WIDTH - 250, WINDOW_HEIGHT), 2)
        
        # Título
        title = self.font.render("Cubo de Rubik", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH - 240, 20))
        
        # Botones de caras
        y_pos = 80
        button_width = 60
        button_height = 40
        
        for i, face in enumerate(FACE_NAMES):
            x = WINDOW_WIDTH - 220 + (i % 3) * 70
            y = y_pos + (i // 3) * 50
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            color = (60, 120, 200) if not self.cube.is_animating else (100, 100, 100)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2)
            
            text = self.small_font.render(face, True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # Botones de acción
        y_pos = 250
        
        # Botón Scramble
        scramble_rect = pygame.Rect(WINDOW_WIDTH - 220, y_pos, 180, 40)
        color = (200, 60, 60) if not self.cube.is_animating else (100, 100, 100)
        pygame.draw.rect(self.screen, color, scramble_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), scramble_rect, 2)
        text = self.small_font.render("Scramble (S)", True, (255, 255, 255))
        text_rect = text.get_rect(center=scramble_rect.center)
        self.screen.blit(text, text_rect)
        
        # Botón Solve
        solve_rect = pygame.Rect(WINDOW_WIDTH - 220, y_pos + 60, 180, 40)
        color = (60, 200, 60) if not self.cube.is_animating else (100, 100, 100)
        pygame.draw.rect(self.screen, color, solve_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), solve_rect, 2)
        text = self.small_font.render("Solve (Space)", True, (255, 255, 255))
        text_rect = text.get_rect(center=solve_rect.center)
        self.screen.blit(text, text_rect)
        
        # Instrucciones
        instructions = [
            "Controles:",
            "- Arrastra para rotar",
            "- F/B: Frente/Atrás",
            "- R/L: Derecha/Izquierda", 
            "- U/D: Arriba/Abajo",
            "- S: Mezclar",
            "- Space: Resolver"
        ]
        
        y_pos = 400
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (WINDOW_WIDTH - 240, y_pos))
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
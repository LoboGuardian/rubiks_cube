"""
Rubik's Cube OpenGL Renderer - High-performance 3D rendering
Uses hardware-accelerated OpenGL for smooth, efficient visualization
"""

import numpy as np
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from cube_model import CubePiece, COLORS


class OpenGLRenderer:
    """
    High-performance OpenGL renderer for Rubik's Cube
    Hardware-accelerated 3D rendering with proper lighting and shading
    """

    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize OpenGL renderer

        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        self.screen = None

        # Camera control
        self.camera_distance = 8.0

        # Cube rotation (visual rotation of the entire cube)
        self.cube_rotation_x = 20.0
        self.cube_rotation_y = 45.0

        # Mouse state
        self.mouse_down = False
        self.last_mouse_pos = None

        self._initialize_pygame()
        self._initialize_opengl()
        self._setup_lighting()

    def _initialize_pygame(self):
        """Initialize Pygame window"""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption("Rubik's Cube 3D - OpenGL Accelerated")

    def _initialize_opengl(self):
        """Initialize OpenGL settings"""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        # Enable smooth shading
        glShadeModel(GL_SMOOTH)

        # Enable blending for better colors
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set clear color (dark background)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Setup perspective
        self._setup_perspective()

    def _setup_perspective(self):
        """Setup perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def _setup_lighting(self):
        """Setup OpenGL lighting for realistic appearance"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Light position (above and to the right)
        light_position = [5.0, 5.0, 5.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Light properties
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # Material properties
        mat_specular = [1.0, 1.0, 1.0, 1.0]
        mat_shininess = [50.0]
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB float values (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)

    def _draw_cube_face(self, vertices: np.ndarray, color: str, is_sticker: bool = True):
        """
        Draw a single cube face as a quad with realistic appearance

        Args:
            vertices: 4 vertices of the face
            color: Hex color string
            is_sticker: If True, draw as colored sticker on black base
        """
        # Convert color
        r, g, b = self._hex_to_rgb(color)

        if is_sticker:
            # Draw black plastic base
            glColor3f(0.15, 0.15, 0.15)
            glBegin(GL_QUADS)
            for vertex in vertices:
                glVertex3fv(vertex)
            glEnd()

            # Calculate face center and normal (pointing outward)
            center = np.mean(vertices, axis=0)
            v1 = vertices[1] - vertices[0]
            v2 = vertices[2] - vertices[0]
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)

            # Make sticker smaller (inset from edges) - 88% of face size
            inset_vertices = center + (vertices - center) * 0.88

            # Raise sticker slightly above black plastic surface
            # This creates the 3D sticker effect
            sticker_vertices = inset_vertices + normal * 0.015

            # Draw colored sticker (slightly raised)
            glColor3f(r, g, b)
            glBegin(GL_QUADS)
            for vertex in sticker_vertices:
                glVertex3fv(vertex)
            glEnd()

            # Draw thin black border around sticker
            glDisable(GL_LIGHTING)
            glColor3f(0.0, 0.0, 0.0)
            glLineWidth(2.5)
            glBegin(GL_LINE_LOOP)
            for vertex in sticker_vertices:
                glVertex3fv(vertex)
            glEnd()
            glEnable(GL_LIGHTING)
        else:
            # Draw solid black plastic face (internal/hidden face)
            glColor3f(0.15, 0.15, 0.15)
            glBegin(GL_QUADS)
            for vertex in vertices:
                glVertex3fv(vertex)
            glEnd()

            # Draw darker edges for definition
            glDisable(GL_LIGHTING)
            glColor3f(0.05, 0.05, 0.05)
            glLineWidth(1.5)
            glBegin(GL_LINE_LOOP)
            for vertex in vertices:
                glVertex3fv(vertex)
            glEnd()
            glEnable(GL_LIGHTING)

    def _draw_cube_piece(self, piece: CubePiece):
        """
        Draw a single cube piece with all its faces (realistic solid cube)

        Args:
            piece: CubePiece object to render
        """
        vertices = piece.get_vertices()

        # Define faces with vertex indices and color indices
        # (vertex_indices, color_index)
        faces = [
            ([1, 5, 6, 2], 0),  # right (x+)
            ([4, 0, 3, 7], 1),  # left (x-)
            ([3, 2, 6, 7], 2),  # up (y+)
            ([0, 4, 5, 1], 3),  # down (y-)
            ([5, 4, 7, 6], 4),  # front (z+)
            ([0, 1, 2, 3], 5)   # back (z-)
        ]

        # Draw ALL faces to create a solid cube
        for indices, color_idx in faces:
            face_vertices = vertices[indices]
            color = piece.colors[color_idx]

            # Colored faces get sticker treatment, black faces are solid plastic
            is_sticker = (color != COLORS['BLACK'])
            self._draw_cube_face(face_vertices, color, is_sticker)

    def render(self, pieces: List[CubePiece]):
        """
        Render all cube pieces

        Args:
            pieces: List of CubePiece objects to render
        """
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset modelview matrix
        glLoadIdentity()

        # Position camera (static, looking at origin)
        gluLookAt(
            0, 0, self.camera_distance,  # Eye position
            0, 0, 0,                      # Look at point
            0, 1, 0                       # Up vector
        )

        # Apply cube rotations (rotate the entire cube visually)
        glRotatef(self.cube_rotation_x, 1, 0, 0)
        glRotatef(self.cube_rotation_y, 0, 1, 0)

        # Draw all pieces
        for piece in pieces:
            self._draw_cube_piece(piece)

        # Swap buffers
        pygame.display.flip()

    def handle_mouse_press(self, pos: Tuple[int, int]):
        """Handle mouse button press"""
        self.mouse_down = True
        self.last_mouse_pos = pos

    def handle_mouse_release(self):
        """Handle mouse button release"""
        self.mouse_down = False
        self.last_mouse_pos = None

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement for cube rotation"""
        if self.mouse_down and self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]

            # Update cube rotation (rotate the cube, not the camera)
            self.cube_rotation_y += dx * 0.5
            self.cube_rotation_x += dy * 0.5

            # Allow full 360° rotation (no clamping)
            # Keep rotations in 0-360 range for readability
            self.cube_rotation_x %= 360
            self.cube_rotation_y %= 360

            self.last_mouse_pos = pos

    def handle_mouse_wheel(self, direction: int):
        """Handle mouse wheel for zoom"""
        if direction > 0:  # Scroll up - zoom in
            self.camera_distance = max(3.0, self.camera_distance - 0.5)
        else:  # Scroll down - zoom out
            self.camera_distance = min(15.0, self.camera_distance + 0.5)

    def resize(self, width: int, height: int):
        """Handle window resize"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self._setup_perspective()

    def cleanup(self):
        """Cleanup resources"""
        pygame.quit()

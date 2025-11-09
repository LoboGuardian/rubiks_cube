"""
Rubik's Cube Model - Pure logic, no GUI dependencies
"""

import numpy as np
from typing import List, Dict
import random

# Constants
CUBE_SIZE = 0.90
CUBE_GAP = 0.12
GRID_SIZE = 3
ROTATION_ANGLE = np.pi / 2

# Colors
COLORS = {
    'RED': '#FF0000',
    'ORANGE': '#FF7F00',
    'BLUE': '#0000FF',
    'GREEN': '#00FF00',
    'WHITE': '#FFFFFF',
    'YELLOW': '#FFFF00',
    'BLACK': '#1A1A1A',
}

FACE_COLORS = [
    COLORS['RED'],     # front - index 0
    COLORS['ORANGE'],  # back - index 1
    COLORS['BLUE'],    # right - index 2
    COLORS['GREEN'],   # left - index 3
    COLORS['WHITE'],   # up - index 4
    COLORS['YELLOW']   # down - index 5
]

FACE_NAMES = ['F', 'B', 'R', 'L', 'U', 'D']


class Vector3:
    """3D Vector for position calculations"""

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

    def to_array(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array([self.x, self.y, self.z])

    def copy(self):
        return Vector3(self.x, self.y, self.z)


class GridPosition:
    """3D grid position (discrete coordinates)"""

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return GridPosition(self.x, self.y, self.z)

    def __repr__(self):
        return f"GridPos({self.x},{self.y},{self.z})"


class CubePiece:
    """Individual piece of the Rubik's cube"""

    def __init__(self, grid_position: GridPosition):
        self.grid_position = grid_position.copy()
        self.position = self._calculate_world_position()
        self.rotation_matrix = np.eye(3)
        self.id = f"{grid_position.x}-{grid_position.y}-{grid_position.z}"
        self.colors = self._initialize_colors()

    def _calculate_world_position(self) -> Vector3:
        """Calculate 3D world position from grid position"""
        offset = CUBE_SIZE + CUBE_GAP
        return Vector3(
            (self.grid_position.x - 1) * offset,
            (self.grid_position.y - 1) * offset,
            (self.grid_position.z - 1) * offset
        )

    def _initialize_colors(self) -> List[str]:
        """Initialize face colors based on position
        Returns colors in order: right, left, up, down, front, back
        """
        colors = []
        x, y, z = self.grid_position.x, self.grid_position.y, self.grid_position.z

        colors.append(FACE_COLORS[2] if x == 2 else COLORS['BLACK'])  # right
        colors.append(FACE_COLORS[3] if x == 0 else COLORS['BLACK'])  # left
        colors.append(FACE_COLORS[4] if y == 2 else COLORS['BLACK'])  # up
        colors.append(FACE_COLORS[5] if y == 0 else COLORS['BLACK'])  # down
        colors.append(FACE_COLORS[0] if z == 2 else COLORS['BLACK'])  # front
        colors.append(FACE_COLORS[1] if z == 0 else COLORS['BLACK'])  # back

        return colors

    def get_vertices(self) -> np.ndarray:
        """Get 8 vertices of this cube piece in 3D space"""
        size = CUBE_SIZE / 2
        vertices = np.array([
            [-size, -size, -size],  # 0
            [size, -size, -size],   # 1
            [size, size, -size],    # 2
            [-size, size, -size],   # 3
            [-size, -size, size],   # 4
            [size, -size, size],    # 5
            [size, size, size],     # 6
            [-size, size, size]     # 7
        ])

        # Apply rotation
        rotated = vertices @ self.rotation_matrix.T

        # Apply position
        pos = self.position.to_array()
        final_vertices = rotated + pos

        return final_vertices

    def update_position_from_world(self):
        """Update grid position based on world position"""
        offset = CUBE_SIZE + CUBE_GAP

        grid_x = round((self.position.x / offset) + 1)
        grid_y = round((self.position.y / offset) + 1)
        grid_z = round((self.position.z / offset) + 1)

        # Clamp to valid range
        grid_x = max(0, min(2, grid_x))
        grid_y = max(0, min(2, grid_y))
        grid_z = max(0, min(2, grid_z))

        self.grid_position = GridPosition(grid_x, grid_y, grid_z)


class RubiksCubeModel:
    """
    Rubik's Cube Model - Contains all logic and state
    No GUI dependencies - pure calculation and state management
    """

    def __init__(self):
        self.pieces: List[CubePiece] = []
        self._initialize_cube()

    def _initialize_cube(self):
        """Create all 27 cube pieces in solved state"""
        self.pieces = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                for z in range(GRID_SIZE):
                    piece = CubePiece(GridPosition(x, y, z))
                    self.pieces.append(piece)

    def get_face_pieces(self, face_name: str) -> List[CubePiece]:
        """Get all pieces that belong to a specific face"""
        face_pieces = []

        for piece in self.pieces:
            pos = piece.grid_position
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
                face_pieces.append(piece)

        return face_pieces

    def _get_rotation_axis(self, face_name: str) -> np.ndarray:
        """Get rotation axis for a face"""
        axes = {
            'F': np.array([0, 0, 1]),
            'B': np.array([0, 0, -1]),
            'R': np.array([1, 0, 0]),
            'L': np.array([-1, 0, 0]),
            'U': np.array([0, 1, 0]),
            'D': np.array([0, -1, 0])
        }
        return axes.get(face_name, np.array([0, 1, 0]))

    def _rotation_matrix_from_axis_angle(self, axis: np.ndarray, angle: float) -> np.ndarray:
        """Create rotation matrix using Rodrigues' formula"""
        axis = axis / np.linalg.norm(axis)
        a = np.cos(angle / 2)
        b, c, d = -axis * np.sin(angle / 2)

        return np.array([
            [a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
            [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
            [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]
        ])

    def rotate_face(self, face_name: str):
        """Rotate a face 90 degrees clockwise"""
        if face_name not in FACE_NAMES:
            raise ValueError(f"Invalid face name: {face_name}")

        face_pieces = self.get_face_pieces(face_name)
        axis = self._get_rotation_axis(face_name)
        angle = ROTATION_ANGLE

        rotation_matrix = self._rotation_matrix_from_axis_angle(axis, angle)

        for piece in face_pieces:
            # Update rotation matrix
            piece.rotation_matrix = rotation_matrix @ piece.rotation_matrix

            # Update position
            old_pos = piece.position.to_array()
            new_pos = rotation_matrix @ old_pos
            piece.position = Vector3(new_pos[0], new_pos[1], new_pos[2])

            # Update grid position
            piece.update_position_from_world()
            piece.colors = piece._initialize_colors()

    def scramble(self, moves: int = 20):
        """Scramble the cube with random moves"""
        for _ in range(moves):
            face = random.choice(FACE_NAMES)
            self.rotate_face(face)

    def reset(self):
        """Reset cube to solved state"""
        self._initialize_cube()

    def get_all_pieces(self) -> List[CubePiece]:
        """Get all cube pieces"""
        return self.pieces

    def get_state_summary(self) -> Dict:
        """Get summary of cube state for debugging"""
        return {
            'total_pieces': len(self.pieces),
            'piece_positions': [(p.grid_position.x, p.grid_position.y, p.grid_position.z)
                               for p in self.pieces]
        }

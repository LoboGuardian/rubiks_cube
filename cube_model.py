"""
Rubik's Cube Model - Pure logic, no GUI dependencies
"""

import numpy as np
from typing import List, Dict
import random

# Constants
CUBE_SIZE = 0.95  # Slightly larger pieces
CUBE_GAP = 0.05   # Smaller gap for realistic appearance
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

# Outward normal of each local face, in the order used by CubePiece.colors:
# right(+X), left(-X), up(+Y), down(-Y), front(+Z), back(-Z)
LOCAL_FACE_NORMALS = [
    np.array([1.0, 0.0, 0.0]),
    np.array([-1.0, 0.0, 0.0]),
    np.array([0.0, 1.0, 0.0]),
    np.array([0.0, -1.0, 0.0]),
    np.array([0.0, 0.0, 1.0]),
    np.array([0.0, 0.0, -1.0]),
]

# Basis for projecting the 3D state onto each face of the unfolded 2D net:
# (outward normal, screen-right vector, screen-up vector) in world space.
NET_FACE_BASIS = {
    'U': (np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, -1.0])),
    'D': (np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])),
    'F': (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])),
    'B': (np.array([0.0, 0.0, -1.0]), np.array([-1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])),
    'R': (np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, -1.0]), np.array([0.0, 1.0, 0.0])),
    'L': (np.array([-1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])),
}


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
        """
        Initialize face colors based on position in the cube.
        ONLY outer boundary faces get colored stickers.
        Returns colors in order: right, left, up, down, front, back

        Grid coordinates:
        - x: 0 (left), 1 (middle), 2 (right)
        - y: 0 (down), 1 (middle), 2 (up)
        - z: 0 (back), 1 (middle), 2 (front)
        """
        colors = []
        x, y, z = self.grid_position.x, self.grid_position.y, self.grid_position.z

        # RIGHT face (+X): Only pieces with x=2 get blue sticker on right face
        colors.append(FACE_COLORS[2] if x == 2 else COLORS['BLACK'])

        # LEFT face (-X): Only pieces with x=0 get green sticker on left face
        colors.append(FACE_COLORS[3] if x == 0 else COLORS['BLACK'])

        # UP face (+Y): Only pieces with y=2 get white sticker on top face
        colors.append(FACE_COLORS[4] if y == 2 else COLORS['BLACK'])

        # DOWN face (-Y): Only pieces with y=0 get yellow sticker on bottom face
        colors.append(FACE_COLORS[5] if y == 0 else COLORS['BLACK'])

        # FRONT face (+Z): Only pieces with z=2 get red sticker on front face
        colors.append(FACE_COLORS[0] if z == 2 else COLORS['BLACK'])

        # BACK face (-Z): Only pieces with z=0 get orange sticker on back face
        colors.append(FACE_COLORS[1] if z == 0 else COLORS['BLACK'])

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
        self.move_history: List[str] = []
        self._initialize_cube()

    @property
    def move_count(self) -> int:
        """Number of face turns since the last reset/scramble."""
        return len(self.move_history)

    @property
    def last_move(self) -> str:
        """Most recent face turn, or empty string if none."""
        return self.move_history[-1] if self.move_history else ""

    def is_solved(self) -> bool:
        """True when every outer face shows a single color.

        Works in any orientation: each sticker is mapped to a world face via
        its piece rotation matrix, then every face must be uniform.
        """
        faces: Dict[tuple, set] = {}
        for piece in self.pieces:
            for index, local_normal in enumerate(LOCAL_FACE_NORMALS):
                color = piece.colors[index]
                if color == COLORS['BLACK']:
                    continue
                world_normal = piece.rotation_matrix @ local_normal
                axis = int(np.argmax(np.abs(world_normal)))
                sign = 1 if world_normal[axis] > 0 else -1
                faces.setdefault((axis, sign), set()).add(color)
        return all(len(colors) == 1 for colors in faces.values())

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
            # Update rotation matrix. Stickers are indexed by the piece's
            # local face, so rotating the geometry carries the colors with
            # the piece automatically. Re-deriving colors from position here
            # would be wrong: it would "re-solve" the cube on every turn and
            # paint stickers onto faces that now point inward.
            piece.rotation_matrix = rotation_matrix @ piece.rotation_matrix

            # Update position
            old_pos = piece.position.to_array()
            new_pos = rotation_matrix @ old_pos
            piece.position = Vector3(new_pos[0], new_pos[1], new_pos[2])

            # Update grid position so future face selection works
            piece.update_position_from_world()

        self.move_history.append(face_name)

    def scramble(self, moves: int = 20):
        """Scramble the cube with random moves.

        Clears the history first so move_count reflects the scramble length.
        """
        self.move_history = []
        for _ in range(moves):
            face = random.choice(FACE_NAMES)
            self.rotate_face(face)

    def reset(self):
        """Reset cube to solved state"""
        self._initialize_cube()
        self.move_history = []

    def get_all_pieces(self) -> List[CubePiece]:
        """Get all cube pieces"""
        return self.pieces

    def get_facelets(self) -> Dict[str, List[List[str]]]:
        """Return the live sticker color of every facelet, per face.

        Maps each face name to a 3x3 grid (row-major, top-left first) of hex
        color strings, derived from the current 3D state so it reflects
        scrambles and turns. A solved cube yields six uniform grids.
        """
        result: Dict[str, List[List[str]]] = {}
        for face, (normal, right, up) in NET_FACE_BASIS.items():
            grid = [[COLORS['BLACK']] * GRID_SIZE for _ in range(GRID_SIZE)]
            for piece in self.pieces:
                pos = piece.position.to_array()
                if np.dot(pos, normal) < 0.5:
                    continue  # not on this outer layer
                col = int(round(np.dot(pos, right))) + 1
                row = 1 - int(round(np.dot(pos, up)))
                for index, local_normal in enumerate(LOCAL_FACE_NORMALS):
                    color = piece.colors[index]
                    if color == COLORS['BLACK']:
                        continue
                    if np.dot(piece.rotation_matrix @ local_normal, normal) > 0.9:
                        grid[row][col] = color
                        break
            result[face] = grid
        return result

    def get_state_summary(self) -> Dict:
        """Get summary of cube state for debugging"""
        return {
            'total_pieces': len(self.pieces),
            'piece_positions': [(p.grid_position.x, p.grid_position.y, p.grid_position.z)
                               for p in self.pieces]
        }

    def validate_colors(self) -> bool:
        """
        Validate sticker conservation: each of the six face colors must
        appear exactly 9 times across all pieces.

        This invariant holds in any state, solved or scrambled, because
        stickers travel with their piece. A position-based check (color X
        only on the X-face) is only valid in the solved state, so it cannot
        be used once the cube has been turned.

        Returns True if valid, False otherwise.
        """
        counts: Dict[str, int] = {}
        for piece in self.pieces:
            for color in piece.colors:
                if color != COLORS['BLACK']:
                    counts[color] = counts.get(color, 0) + 1

        for face_color in FACE_COLORS:
            found = counts.get(face_color, 0)
            if found != 9:
                print(f"ERROR: color {face_color} appears {found} times "
                      f"(expected 9)")
                return False

        return True


class FaceletState:
    """An editable six-face sticker grid for inputting an arbitrary state.

    This is the buffer behind the color picker. It is a plain copy of the
    facelet colors and is independent of the 3D piece model: painting a cell
    does not move any piece. It is intended as input for a future solver, so
    its only invariant is the count of each color.
    """

    def __init__(self, facelets: Dict[str, List[List[str]]]):
        self.faces: Dict[str, List[List[str]]] = {
            face: [list(row) for row in grid]
            for face, grid in facelets.items()
        }

    def paint(self, face: str, row: int, col: int, color: str) -> bool:
        """Set a single facelet, refusing to exceed nine of any color.

        Returns True if the cell now holds the color (including the no-op
        case where it already did), False if the paint was rejected because
        the color is already used nine times elsewhere.
        """
        current = self.faces[face][row][col]
        if color == current:
            return True
        if self.color_counts().get(color, 0) >= 9:
            return False
        self.faces[face][row][col] = color
        return True

    def clear(self):
        """Blank every facelet so the state can be painted from scratch."""
        for grid in self.faces.values():
            for row in grid:
                for index in range(len(row)):
                    row[index] = COLORS['BLACK']

    def color_counts(self) -> Dict[str, int]:
        """Count occurrences of each color across all facelets."""
        counts: Dict[str, int] = {}
        for grid in self.faces.values():
            for row in grid:
                for color in row:
                    counts[color] = counts.get(color, 0) + 1
        return counts

    def is_valid(self) -> bool:
        """True when each of the six face colors appears exactly 9 times."""
        counts = self.color_counts()
        return all(counts.get(color, 0) == 9 for color in FACE_COLORS)

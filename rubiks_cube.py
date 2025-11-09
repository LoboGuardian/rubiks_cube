import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from matplotlib.widgets import Button
from typing import List
import random

# Constants
CUBE_SIZE = 0.95
CUBE_GAP = 0.08
GRID_SIZE = 3
ANIMATION_FRAMES = 20
ROTATION_ANGLE = np.pi / 2

# Colors for Rubik's Cube faces
COLORS = {
    'RED': '#FF0000',
    'ORANGE': '#FF7F00',
    'BLUE': '#0000FF',
    'GREEN': '#00FF00',
    'WHITE': '#FFFFFF',
    'YELLOW': '#FFFF00',
    'BLACK': '#1A1A1A',
    'GRAY': '#808080'
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

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    def copy(self):
        return Vector3(self.x, self.y, self.z)

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
        self.rotation_matrix = np.eye(3)
        self.id = f"{grid_position.x}-{grid_position.y}-{grid_position.z}"
        self.colors = self.get_face_colors()

    def get_world_position(self) -> Vector3:
        offset = CUBE_SIZE + CUBE_GAP
        return Vector3(
            (self.grid_position.x - 1) * offset,
            (self.grid_position.y - 1) * offset,
            (self.grid_position.z - 1) * offset
        )

    def get_face_colors(self) -> List[str]:
        """Returns colors of faces in order: right, left, up, down, front, back"""
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
        """Returns the 8 vertices of the cube"""
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

class RubiksCube:
    def __init__(self):
        self.cubes: List[SmallCube] = []
        self.is_animating = False
        self.animation_progress = 0
        self.animating_cubes = []
        self.animation_axis = None
        self.animation_angle = 0
        self.initial_rotations = []
        self.initial_positions = []

        self.create_cubes()

    def create_cubes(self):
        """Creates all the small cubes of the Rubik's cube"""
        self.cubes = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                for z in range(GRID_SIZE):
                    cube = SmallCube(GridPosition(x, y, z))
                    self.cubes.append(cube)

    def get_face_cubes(self, face_name: str) -> List[SmallCube]:
        """Returns the cubes of a specific face"""
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

    def get_rotation_axis(self, face_name: str) -> np.ndarray:
        """Returns the rotation axis for a face"""
        axes = {
            'F': np.array([0, 0, 1]),
            'B': np.array([0, 0, -1]),
            'R': np.array([1, 0, 0]),
            'L': np.array([-1, 0, 0]),
            'U': np.array([0, 1, 0]),
            'D': np.array([0, -1, 0])
        }
        return axes.get(face_name, np.array([0, 1, 0]))

    def rotation_matrix_from_axis_angle(self, axis: np.ndarray, angle: float) -> np.ndarray:
        """Creates a rotation matrix from axis and angle using Rodrigues' formula"""
        axis = axis / np.linalg.norm(axis)
        a = np.cos(angle / 2)
        b, c, d = -axis * np.sin(angle / 2)

        return np.array([
            [a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
            [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
            [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]
        ])

    def rotate_face(self, face_name: str):
        """Rotates a face of the cube"""
        if self.is_animating:
            return

        face_cubes = self.get_face_cubes(face_name)
        axis = self.get_rotation_axis(face_name)
        angle = ROTATION_ANGLE

        rotation_matrix = self.rotation_matrix_from_axis_angle(axis, angle)

        for cube in face_cubes:
            # Update rotation matrix
            cube.rotation_matrix = rotation_matrix @ cube.rotation_matrix

            # Update position
            old_pos = cube.position.to_array()
            new_pos = rotation_matrix @ old_pos
            cube.position = Vector3(new_pos[0], new_pos[1], new_pos[2])

            # Update grid position
            self.update_cube_grid_position_from_world(cube)
            cube.colors = cube.get_face_colors()

    def update_cube_grid_position_from_world(self, cube: SmallCube):
        """Updates grid position based on world position"""
        offset = CUBE_SIZE + CUBE_GAP

        # Convert world position to grid coordinates
        grid_x = round((cube.position.x / offset) + 1)
        grid_y = round((cube.position.y / offset) + 1)
        grid_z = round((cube.position.z / offset) + 1)

        # Ensure they're in valid range
        grid_x = max(0, min(2, grid_x))
        grid_y = max(0, min(2, grid_y))
        grid_z = max(0, min(2, grid_z))

        cube.grid_position = GridPosition(grid_x, grid_y, grid_z)

    def scramble(self):
        """Scrambles the cube with random moves"""
        if self.is_animating:
            return

        moves = 20
        for i in range(moves):
            face = random.choice(FACE_NAMES)
            self.rotate_face(face)

    def solve(self):
        """Resets the cube to solved state"""
        if self.is_animating:
            return

        self.create_cubes()

    def get_all_faces_data(self):
        """Returns all faces for rendering"""
        all_faces = []

        # Define the 6 faces of a cube with vertex indices
        faces_indices = [
            ([1, 5, 6, 2], 0),  # right (x+)
            ([4, 0, 3, 7], 1),  # left (x-)
            ([3, 2, 6, 7], 2),  # up (y+)
            ([0, 4, 5, 1], 3),  # down (y-)
            ([5, 4, 7, 6], 4),  # front (z+)
            ([0, 1, 2, 3], 5)   # back (z-)
        ]

        for cube in self.cubes:
            vertices = cube.get_vertices()

            for indices, color_idx in faces_indices:
                face_verts = vertices[indices]
                color = cube.colors[color_idx]
                all_faces.append((face_verts, color))

        return all_faces

class RubiksCubeApp:
    def __init__(self):
        self.cube = RubiksCube()
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.patch.set_facecolor('#2A2A2A')

        # Main 3D axes
        self.ax = self.fig.add_subplot(121, projection='3d')
        self.ax.set_facecolor('#1A1A1A')

        # Setup axes
        limit = 2
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])
        self.ax.set_zlim([-limit, limit])
        self.ax.set_xlabel('X', color='white')
        self.ax.set_ylabel('Y', color='white')
        self.ax.set_zlabel('Z', color='white')
        self.ax.tick_params(colors='white')

        # Disable panes for cleaner look
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('#404040')
        self.ax.yaxis.pane.set_edgecolor('#404040')
        self.ax.zaxis.pane.set_edgecolor('#404040')

        # Set aspect ratio to equal for proper cube rendering
        self.ax.set_box_aspect([1, 1, 1])

        # Set initial view
        self.ax.view_init(elev=20, azim=45)

        # Control panel
        self.setup_controls()

        # Mouse interaction
        self.mouse_pressed = False
        self.last_mouse_pos = None

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)

        self.render()

    def setup_controls(self):
        """Setup control buttons"""
        # Create buttons for face rotations
        button_height = 0.04
        button_width = 0.08
        start_x = 0.55
        start_y = 0.75

        # Title
        self.fig.text(0.68, 0.92, "Rubik's Cube 3D",
                     ha='center', fontsize=16, weight='bold', color='white')
        self.fig.text(0.68, 0.88, "Interactive Control",
                     ha='center', fontsize=10, color='lightgray')

        # Face rotation buttons
        self.fig.text(start_x + 0.05, start_y + 0.05, "Face Rotations:",
                     fontsize=10, weight='bold', color='white')

        face_colors_ui = {
            'F': '#DC3C3C',
            'B': '#FF8C3C',
            'R': '#3C3CDC',
            'L': '#3CDC3C',
            'U': '#F0F0F0',
            'D': '#F0F03C'
        }

        self.face_buttons = {}
        for i, face in enumerate(FACE_NAMES):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + 0.02)
            y = start_y - row * (button_height + 0.01)

            ax_btn = plt.axes([x, y, button_width, button_height])
            btn = Button(ax_btn, face, color=face_colors_ui[face], hovercolor='lightgray')
            btn.label.set_fontsize(10)
            btn.label.set_weight('bold')
            btn.on_clicked(lambda event, f=face: self.rotate_face_callback(f))
            self.face_buttons[face] = btn

        # Action buttons
        action_y = start_y - 0.15
        self.fig.text(start_x + 0.05, action_y + 0.05, "Actions:",
                     fontsize=10, weight='bold', color='white')

        # Scramble button
        ax_scramble = plt.axes([start_x, action_y - 0.05, 0.26, button_height])
        self.btn_scramble = Button(ax_scramble, 'Scramble (S)',
                                   color='#C83C3C', hovercolor='#FF4C4C')
        self.btn_scramble.label.set_color('white')
        self.btn_scramble.label.set_fontsize(10)
        self.btn_scramble.on_clicked(self.scramble_callback)

        # Solve button
        ax_solve = plt.axes([start_x, action_y - 0.1, 0.26, button_height])
        self.btn_solve = Button(ax_solve, 'Solve (Space)',
                               color='#3CC83C', hovercolor='#4CFF4C')
        self.btn_solve.label.set_color('white')
        self.btn_solve.label.set_fontsize(10)
        self.btn_solve.on_clicked(self.solve_callback)

        # Instructions
        inst_y = action_y - 0.22
        self.fig.text(start_x + 0.05, inst_y, "Controls:",
                     fontsize=10, weight='bold', color='white')

        instructions = [
            "• Drag: Rotate view",
            "• Scroll: Zoom in/out",
            "• F/B: Front/Back",
            "• R/L: Right/Left",
            "• U/D: Up/Down",
            "• S: Scramble",
            "• Space: Solve",
            "• Q: Quit"
        ]

        for i, instruction in enumerate(instructions):
            self.fig.text(start_x + 0.02, inst_y - (i + 1) * 0.03,
                         instruction, fontsize=8, color='lightgray')

    def rotate_face_callback(self, face: str):
        """Callback for face rotation buttons"""
        self.cube.rotate_face(face)
        self.render()

    def scramble_callback(self, event):
        """Callback for scramble button"""
        self.cube.scramble()
        self.render()

    def solve_callback(self, event):
        """Callback for solve button"""
        self.cube.solve()
        self.render()

    def on_mouse_press(self, event):
        """Handle mouse press"""
        if event.inaxes == self.ax:
            self.mouse_pressed = True
            self.last_mouse_pos = (event.x, event.y)

    def on_mouse_release(self, event):
        """Handle mouse release"""
        self.mouse_pressed = False
        self.last_mouse_pos = None

    def on_mouse_move(self, event):
        """Handle mouse movement for rotation"""
        if self.mouse_pressed and event.inaxes == self.ax and self.last_mouse_pos:
            dx = event.x - self.last_mouse_pos[0]
            dy = event.y - self.last_mouse_pos[1]

            # Update view angles
            azim = self.ax.azim + dx * 0.5
            elev = self.ax.elev - dy * 0.5
            self.ax.view_init(elev=elev, azim=azim)

            self.last_mouse_pos = (event.x, event.y)
            self.fig.canvas.draw_idle()

    def on_scroll(self, event):
        """Handle scroll for zoom"""
        if event.inaxes == self.ax:
            # Get current limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            zlim = self.ax.get_zlim()

            # Calculate zoom factor
            if event.button == 'up':
                scale = 0.9
            else:
                scale = 1.1

            # Apply zoom
            xcenter = np.mean(xlim)
            ycenter = np.mean(ylim)
            zcenter = np.mean(zlim)

            xrange = (xlim[1] - xlim[0]) * scale / 2
            yrange = (ylim[1] - ylim[0]) * scale / 2
            zrange = (zlim[1] - zlim[0]) * scale / 2

            self.ax.set_xlim([xcenter - xrange, xcenter + xrange])
            self.ax.set_ylim([ycenter - yrange, ycenter + yrange])
            self.ax.set_zlim([zcenter - zrange, zcenter + zrange])

            self.fig.canvas.draw_idle()

    def on_key_press(self, event):
        """Handle keyboard input"""
        if event.key == 'f':
            self.cube.rotate_face('F')
            self.render()
        elif event.key == 'b':
            self.cube.rotate_face('B')
            self.render()
        elif event.key == 'r':
            self.cube.rotate_face('R')
            self.render()
        elif event.key == 'l':
            self.cube.rotate_face('L')
            self.render()
        elif event.key == 'u':
            self.cube.rotate_face('U')
            self.render()
        elif event.key == 'd':
            self.cube.rotate_face('D')
            self.render()
        elif event.key == 's':
            self.cube.scramble()
            self.render()
        elif event.key == ' ':
            self.cube.solve()
            self.render()
        elif event.key == 'q':
            plt.close(self.fig)

    def render(self):
        """Render the cube"""
        # Clear the axes
        self.ax.clear()

        # Reset limits and labels
        limit = 2
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])
        self.ax.set_zlim([-limit, limit])
        self.ax.set_xlabel('X', color='white')
        self.ax.set_ylabel('Y', color='white')
        self.ax.set_zlabel('Z', color='white')
        self.ax.tick_params(colors='white')

        # Restore pane settings (cleared by ax.clear())
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('#404040')
        self.ax.yaxis.pane.set_edgecolor('#404040')
        self.ax.zaxis.pane.set_edgecolor('#404040')

        # Restore aspect ratio (cleared by ax.clear())
        self.ax.set_box_aspect([1, 1, 1])

        # Set background color
        self.ax.set_facecolor('#1A1A1A')

        # Get all faces
        faces_data = self.cube.get_all_faces_data()

        # Separate visible and internal faces
        visible_faces = []
        visible_colors = []
        internal_faces = []

        for face_verts, color in faces_data:
            if color != COLORS['BLACK']:
                visible_faces.append(face_verts)
                visible_colors.append(color)
            else:
                internal_faces.append(face_verts)

        # Draw internal faces first (with lower z-order)
        if internal_faces:
            internal_poly = Poly3DCollection(internal_faces,
                                            alpha=0.2,
                                            facecolors='#2A2A2A',
                                            edgecolors='#1A1A1A',
                                            linewidths=0.5,
                                            antialiased=True,
                                            zorder=1)
            self.ax.add_collection3d(internal_poly)

        # Draw visible faces with proper colors
        if visible_faces:
            visible_poly = Poly3DCollection(visible_faces,
                                           alpha=1.0,
                                           facecolors=visible_colors,
                                           edgecolors='black',
                                           linewidths=2.0,
                                           antialiased=True,
                                           zorder=2)
            self.ax.add_collection3d(visible_poly)

        # Force redraw
        self.fig.canvas.draw_idle()

    def show(self):
        """Display the application"""
        plt.show()

def main():
    print("Starting Rubik's Cube 3D...")
    print("Controls:")
    print("  - Drag with mouse to rotate view")
    print("  - Scroll to zoom in/out")
    print("  - Press F/B/R/L/U/D to rotate faces")
    print("  - Press S to scramble")
    print("  - Press Space to solve")
    print("  - Press Q to quit")
    print()

    app = RubiksCubeApp()
    app.show()

if __name__ == "__main__":
    main()

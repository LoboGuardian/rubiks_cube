#!/usr/bin/env python3
"""
Rubik's Cube 3D - Interactive Visualization

High-performance implementation using hardware-accelerated OpenGL rendering
Smooth 60+ FPS with real-time lighting and shading

Architecture:
- Model: cube_model.py (logic and state)
- View: cube_renderer.py (OpenGL rendering)
- Controller: This file (user input and event handling)

Usage:
    python rubiks_cube.py
"""

import pygame
from pygame.locals import *
from cube_model import COLORS, FaceletState, RubiksCubeModel
from cube_renderer import OpenGLRenderer
import sys


class RubiksCubeApp:
    """
    Main application using OpenGL for high-performance rendering
    """

    def __init__(self):
        print("Initializing Rubik's Cube 3D...")

        # Initialize Model
        print("Creating cube model...")
        self.model = RubiksCubeModel()

        # Validate color assignment (colors only on outer faces)
        print("Validating color placement...")
        if self.model.validate_colors():
            print("Colors correctly placed on outer faces only")
        else:
            print("WARNING: Color placement validation failed!")

        # Initialize Renderer
        print("Creating renderer (hardware accelerated)...")
        self.renderer = OpenGLRenderer(width=1200, height=800)

        # Application state
        self.running = True
        self.clock = pygame.time.Clock()

        # Color-picker (edit) state
        self.edit_mode = False
        self.editor = None
        self.palette = [COLORS[k] for k in
                        ('RED', 'ORANGE', 'BLUE', 'GREEN', 'WHITE', 'YELLOW')]
        self.selected_color = self.palette[0]

        print("Initialization complete!")
        self._print_instructions()

    def _print_instructions(self):
        """Print usage instructions"""
        print("\n" + "="*60)
        print("RUBIK'S CUBE 3D - CONTROLS")
        print("="*60)
        print("\nPerformance:")
        print("  • Hardware-accelerated rendering")
        print("  • Smooth 60+ FPS")
        print("  • Real-time lighting")
        print("\nMouse Controls:")
        print("  • Left Drag: Rotate view")
        print("  • Mouse Wheel: Zoom in/out")
        print("\nKeyboard Controls:")
        print("  • F/B: Rotate Front/Back face")
        print("  • R/L: Rotate Right/Left face")
        print("  • U/D: Rotate Up/Down face")
        print("  • S: Scramble cube")
        print("  • Space: Solve (reset)")
        print("  • E: Edit mode (click a palette color, then paint cells)")
        print("  • ESC/Q: Quit")
        print("="*60 + "\n")

    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                self._handle_keypress(event.key)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.edit_mode:
                        self._handle_paint_click(event.pos)
                    else:
                        self.renderer.handle_mouse_press(event.pos)
                elif event.button == 4:  # Scroll up
                    self.renderer.handle_mouse_wheel(1)
                elif event.button == 5:  # Scroll down
                    self.renderer.handle_mouse_wheel(-1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.renderer.handle_mouse_release()

            elif event.type == MOUSEMOTION:
                self.renderer.handle_mouse_motion(event.pos)

            elif event.type == VIDEORESIZE:
                self.renderer.resize(event.w, event.h)

    def _handle_paint_click(self, pos):
        """In edit mode, a click selects a palette color or paints a cell"""
        color = self.renderer.palette_color_at(pos)
        if color is not None:
            self.selected_color = color
            return
        cell = self.renderer.cell_at(pos)
        if cell is not None:
            face, row, col = cell
            self.editor.paint(face, row, col, self.selected_color)

    def _toggle_edit_mode(self):
        """Enter/leave the color picker; entering snapshots the live state"""
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.editor = FaceletState(self.model.get_facelets())
            print("Edit mode ON - click a color then paint cells")
        else:
            print("Edit mode OFF")

    def _handle_keypress(self, key: int):
        """Handle keyboard input"""
        # Edit mode toggle is always available
        if key == K_e:
            self._toggle_edit_mode()
            return

        # Quit is always available
        if key == K_ESCAPE or key == K_q:
            self.running = False
            return

        # While painting, ignore cube-mutating keys to avoid desyncing the
        # editable net from the 3D cube.
        if self.edit_mode:
            return

        # Face rotations
        if key == K_f:
            self.model.rotate_face('F')
        elif key == K_b:
            self.model.rotate_face('B')
        elif key == K_r:
            self.model.rotate_face('R')
        elif key == K_l:
            self.model.rotate_face('L')
        elif key == K_u:
            self.model.rotate_face('U')
        elif key == K_d:
            self.model.rotate_face('D')

        # Actions
        elif key == K_s:
            print("Scrambling cube...")
            self.model.scramble()
            print("Cube scrambled!")
        elif key == K_SPACE:
            print("Solving cube...")
            self.model.reset()
            print("Cube solved!")

    def run(self):
        """Main application loop"""
        print("Starting main loop...")

        while self.running:
            # Handle events
            self.handle_events()

            # Render cube with live status for the HUD. In edit mode the net
            # shows the editable buffer; otherwise it mirrors the 3D cube.
            pieces = self.model.get_all_pieces()
            if self.edit_mode:
                facelets = self.editor.faces
                valid = self.editor.is_valid()
            else:
                facelets = self.model.get_facelets()
                valid = True
            status = {
                'fps': self.clock.get_fps(),
                'moves': self.model.move_count,
                'last_move': self.model.last_move,
                'solved': self.model.is_solved(),
                'facelets': facelets,
                'edit_mode': self.edit_mode,
                'palette': self.palette,
                'selected_color': self.selected_color,
                'valid': valid,
            }
            self.renderer.render(pieces, status)

            # Maintain 60 FPS
            self.clock.tick(60)

        # Cleanup
        self.renderer.cleanup()
        print("\nThanks for playing!")

    def print_performance_info(self):
        """Print performance information"""
        fps = self.clock.get_fps()
        print(f"\nPerformance: {fps:.1f} FPS")
        print(f"Camera Distance: {self.renderer.camera_distance:.1f}")
        print(f"Cube Rotation: X={self.renderer.cube_rotation_x:.1f}°, "
              f"Y={self.renderer.cube_rotation_y:.1f}°")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("RUBIK'S CUBE 3D - INTERACTIVE VISUALIZATION")
    print("="*60)
    print("\nFeatures:")
    print("  • Hardware-accelerated 3D rendering (OpenGL)")
    print("  • Smooth 60+ FPS performance")
    print("  • Real-time lighting and shading")
    print("  • Efficient face culling")
    print("  • Clean MVC architecture")
    print("="*60 + "\n")

    # Create and run application
    app = RubiksCubeApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        app.renderer.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()

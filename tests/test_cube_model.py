"""
Tests for the GUI-independent cube model.

These guard the core invariant that broke historically: stickers must
travel with their piece. A position-derived color scheme makes the cube
appear solved after every turn; these tests fail loudly if that returns.
"""

import numpy as np
import pytest

from cube_model import COLORS, FACE_NAMES, RubiksCubeModel

# Local outward normals for each face index in CubePiece.colors:
# right(+X), left(-X), up(+Y), down(-Y), front(+Z), back(-Z)
LOCAL_NORMALS = [
    np.array([1.0, 0, 0]),
    np.array([-1.0, 0, 0]),
    np.array([0, 1.0, 0]),
    np.array([0, -1.0, 0]),
    np.array([0, 0, 1.0]),
    np.array([0, 0, -1.0]),
]

WORLD_DIRS = {
    "R": np.array([1.0, 0, 0]),
    "L": np.array([-1.0, 0, 0]),
    "U": np.array([0, 1.0, 0]),
    "D": np.array([0, -1.0, 0]),
    "F": np.array([0, 0, 1.0]),
    "B": np.array([0, 0, -1.0]),
}


def outer_face_colors(model):
    """Map each outer face to the set of sticker colors currently visible.

    A sticker is visible on face ``f`` when its piece's rotated local normal
    points along that face's world direction.
    """
    faces = {name: set() for name in WORLD_DIRS}
    for piece in model.pieces:
        for index, local_normal in enumerate(LOCAL_NORMALS):
            color = piece.colors[index]
            if color == COLORS["BLACK"]:
                continue
            world_normal = piece.rotation_matrix @ local_normal
            for name, world_dir in WORLD_DIRS.items():
                if np.dot(world_normal, world_dir) > 0.9:
                    faces[name].add(color)
    return faces


def test_solved_cube_has_27_pieces():
    model = RubiksCubeModel()
    assert len(model.pieces) == 27


def test_solved_cube_is_color_valid():
    model = RubiksCubeModel()
    assert model.validate_colors() is True


def test_each_face_is_uniform_when_solved():
    model = RubiksCubeModel()
    for name, colors in outer_face_colors(model).items():
        assert len(colors) == 1, f"face {name} not uniform when solved"


def test_scramble_actually_mixes_the_faces():
    """Regression: stickers must move with pieces, not be re-derived from
    position. If they were re-derived, every face would stay uniform."""
    model = RubiksCubeModel()
    model.scramble(30)
    counts = {name: len(c) for name, c in outer_face_colors(model).items()}
    assert any(n > 1 for n in counts.values()), (
        f"scrambled cube still looks solved: {counts}"
    )


def test_color_conservation_after_scramble():
    model = RubiksCubeModel()
    model.scramble(50)
    assert model.validate_colors() is True


def test_four_quarter_turns_restore_positions():
    for face in FACE_NAMES:
        model = RubiksCubeModel()
        before = [
            (p.grid_position.x, p.grid_position.y, p.grid_position.z)
            for p in model.pieces
        ]
        for _ in range(4):
            model.rotate_face(face)
        after = [
            (p.grid_position.x, p.grid_position.y, p.grid_position.z)
            for p in model.pieces
        ]
        assert before == after, f"{face}*4 did not restore positions"


def test_reset_returns_to_solved_state():
    model = RubiksCubeModel()
    model.scramble(20)
    model.reset()
    for name, colors in outer_face_colors(model).items():
        assert len(colors) == 1, f"face {name} not uniform after reset"


def test_invalid_face_name_raises():
    model = RubiksCubeModel()
    with pytest.raises(ValueError):
        model.rotate_face("X")


def test_is_solved_tracks_state():
    model = RubiksCubeModel()
    assert model.is_solved() is True
    model.rotate_face("R")
    assert model.is_solved() is False
    model.reset()
    assert model.is_solved() is True


def test_move_history_counts_and_records_turns():
    model = RubiksCubeModel()
    assert model.move_count == 0
    assert model.last_move == ""
    model.rotate_face("F")
    model.rotate_face("U")
    assert model.move_count == 2
    assert model.last_move == "U"


def test_reset_clears_history():
    model = RubiksCubeModel()
    model.scramble(10)
    assert model.move_count == 10
    model.reset()
    assert model.move_count == 0
    assert model.last_move == ""


def test_scramble_resets_move_count_to_scramble_length():
    model = RubiksCubeModel()
    model.rotate_face("R")
    model.scramble(15)
    assert model.move_count == 15

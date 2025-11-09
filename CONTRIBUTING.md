# Contributing to Rubik's Cube 3D

Thank you for your interest in contributing! This document provides guidelines for both human developers and AI assistants.

## For AI Assistants (Claude Code, etc.)

**Important**: Read [`.clinerules`](.clinerules) for detailed AI assistant instructions.

Key points:
- This project uses **MVC architecture** - never violate layer boundaries
- Always use `poetry run` for all Python commands
- Model must remain GUI-independent (no OpenGL/pygame imports)
- Cube must look realistic (solid pieces, raised stickers, black borders)

## For Human Developers

### Quick Start

```bash
# Clone the repository
git clone https://github.com/LoboGuardian/rubiks_cube
cd rubiks_cube

# Install dependencies with Poetry
poetry install

# Run the application
poetry run python rubiks_cube.py
```

### Development Setup

**Prerequisites:**
- Python 3.14+
- Poetry (for dependency management)
- OpenGL-compatible graphics card

**Install Poetry** (if not installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Project Structure

```
rubiks_cube/
├── cube_model.py       # Business logic (Model)
├── cube_renderer.py    # OpenGL rendering (View)
├── rubiks_cube.py      # Event handling (Controller)
├── pyproject.toml      # Dependencies
├── .clinerules         # AI assistant instructions
├── README.md           # Project documentation
└── CONTRIBUTING.md     # This file
```

### Architecture Guidelines

This project follows **MVC (Model-View-Controller)** pattern:

1. **Model** (`cube_model.py`)
   - Pure Python + NumPy only
   - No GUI dependencies
   - Testable without rendering
   - Contains all cube logic

2. **View** (`cube_renderer.py`)
   - OpenGL rendering only
   - No business logic
   - Receives data, displays it

3. **Controller** (`rubiks_cube.py`)
   - User input handling
   - Coordinates Model ↔ View
   - Main event loop

**Golden Rule**: Never mix layers! Model should never import OpenGL/pygame.

### Making Changes

#### Adding a New Feature

1. **Determine the layer**:
   - Logic change? → Update Model
   - Visual change? → Update View
   - New controls? → Update Controller

2. **Follow MVC boundaries**:
   ```python
   # ✅ Good - Model is pure
   class RubiksCubeModel:
       def rotate_face(self, face: str):
           # Pure logic, no rendering

   # ❌ Bad - Model imports GUI
   import pygame  # NEVER do this in cube_model.py
   ```

3. **Test your changes**:
   ```bash
   poetry run python rubiks_cube.py
   ```

#### Code Style

- Use **type hints** on all functions
- Add **docstrings** to public methods
- Follow **PEP 8** style guide
- Use **snake_case** for functions/variables
- Use **PascalCase** for classes
- Use **UPPER_SNAKE_CASE** for constants

Example:
```python
def rotate_face(self, face_name: str) -> None:
    """
    Rotate a face 90 degrees clockwise

    Args:
        face_name: One of 'F', 'B', 'R', 'L', 'U', 'D'
    """
    # Implementation
```

### Testing

#### Manual Testing Checklist

Before submitting changes, verify:

- [ ] All face rotations work (F, B, R, L, U, D)
- [ ] Mouse drag rotates view smoothly
- [ ] Mouse wheel zooms in/out
- [ ] Scramble function works (press S)
- [ ] Reset function works (press Space)
- [ ] Cube looks solid (not transparent)
- [ ] Stickers are on outside of cube
- [ ] 60 FPS performance maintained
- [ ] No console errors

#### Running Tests

```bash
# Test imports
poetry run python -c "from cube_model import RubiksCubeModel; print('OK')"

# Run the application
poetry run python rubiks_cube.py
```

### Performance Requirements

- **FPS**: 60+ at all times
- **Frame Time**: <16ms
- **Startup**: <2 seconds
- **CPU Usage**: <10% (GPU renders)

If performance degrades:
1. Check backface culling is enabled
2. Verify depth testing is on
3. Profile with: `poetry run python -m cProfile rubiks_cube.py`

### Visual Guidelines

The cube must look **realistic** like a physical Rubik's Cube:

✅ **Correct**:
- Solid black plastic pieces
- Colored stickers on outer faces only
- Stickers raised above plastic surface
- Black borders visible between stickers
- Tight gaps between pieces

❌ **Incorrect**:
- Transparent/hollow pieces
- Stickers on inside surfaces
- Flat stickers (no 3D depth)
- No borders between pieces
- Large gaps making cube look separated

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following guidelines above

4. **Test thoroughly**:
   ```bash
   poetry run python rubiks_cube.py
   ```

5. **Commit with conventional format**:
   ```bash
   git commit -m "feat(model): add double-layer rotations"
   ```

6. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation changes
- `style`: Code style changes
- `perf`: Performance improvements
- `test`: Adding tests

**Examples**:
```
feat(model): add support for 4x4 cube
fix(renderer): correct sticker placement on rotated pieces
refactor(controller): simplify event handling
docs(readme): update installation instructions
perf(renderer): optimize face culling algorithm
```

## Common Issues

### "Module not found" errors
**Solution**: Use `poetry run` prefix:
```bash
poetry run python rubiks_cube.py
```

### Cube looks transparent
**Solution**: Ensure all 6 faces are drawn in `_draw_cube_piece()`

### Stickers on wrong side
**Solution**: Check normal vector calculation in `_draw_cube_face()`

### Poor performance
**Solution**: Verify OpenGL settings (depth test, culling, etc.)

## Feature Requests

Want to add a feature? Great! Consider:

1. **Solver Algorithm**: Implement CFOP, Kociemba, or A*
2. **Animation**: Smooth rotation transitions
3. **Move History**: Undo/redo functionality
4. **Timer**: Speedsolving timer with stats
5. **Themes**: Custom color schemes
6. **VR Support**: Render to VR headsets

**Before starting**, open an issue to discuss the approach.

## Code Review Guidelines

Pull requests should:

- ✅ Maintain MVC separation
- ✅ Include type hints
- ✅ Have docstrings
- ✅ Pass manual testing checklist
- ✅ Maintain 60 FPS performance
- ✅ Follow code style guidelines
- ✅ Have descriptive commit messages

## Resources

- [OpenGL Documentation](https://www.opengl.org/documentation/)
- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/documentation/index.html)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Rubik's Cube Notation](https://ruwix.com/the-rubiks-cube/notation/)
- [Poetry Documentation](https://python-poetry.org/docs/)

## Questions?

- Open an issue for bugs or questions
- Email: loboguardian.dev@gmail.com
- GitHub: [@LoboGuardian](https://github.com/LoboGuardian)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎲✨

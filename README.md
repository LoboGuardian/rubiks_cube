# 🎲 Cubo de Rubik 3D en Python

¡Un cubo de Rubik 3D completamente funcional implementado en Python puro! Esta implementación usa `pygame` y matemáticas 3D sin dependencias externas complejas.

![Cubo de Rubik 3D](https://img.shields.io/badge/Python-3D_Rubik's_Cube-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green?style=flat-square)
![Numpy](https://img.shields.io/badge/NumPy-Compatible-orange?style=flat-square)

## 🚀 Características Principales

### 🎮 Funcionalidades del Cubo
- **Renderizado 3D completo** con proyección perspectiva
- **Rotación interactiva** arrastrando con el mouse
- **Animaciones suaves** para las rotaciones de caras
- **Sistema de colores** realista del cubo de Rubik
- **Detección de caras visibles** (backface culling)
- **Botones clickeables** en la interfaz de usuario
- **Función de mezcla mejorada** con rotaciones inmediatas

### 🎯 Controles

#### 🖱️ Mouse
- **Arrastrar**: Rotar el cubo completo en 3D

#### ⌨️ Teclado
| Tecla | Acción |
|-------|--------|
| `F` | Rotar cara frontal |
| `B` | Rotar cara trasera |
| `R` | Rotar cara derecha |
| `L` | Rotar cara izquierda |
| `U` | Rotar cara superior |
| `D` | Rotar cara inferior |
| `S` | Mezclar el cubo |
| `Espacio` | Resolver (resetear) |
| `ESC` | Salir del programa |

#### 🖱️ Interfaz UI
- **Botones de caras**: Click en F, B, R, L, U, D
- **Botón Scramble**: Mezcla automática del cubo
- **Botón Solve**: Restaura el cubo al estado resuelto

## 🛠️ Instalación y Ejecución

### 📋 Requisitos
```bash
Python 3.7+
pygame 2.0+
numpy
```

### 🔧 Instalación
1. **Clona o descarga el proyecto**
```bash
git clone https://github.com/LoboGuardian/rubiks_cube
cd rubiks-cube-3d
```

2. **Instala las dependencias**
```bash
pip install pygame numpy
```
o
```bash
pipenv install
```

3. **Ejecuta el programa**
```bash
python rubiks_cube.py
```
o
```bash
pipenv run python rubiks_cube.py
```

## 🏗️ Arquitectura del Código

### 📦 Clases Principales

| Clase | Descripción |
|-------|-------------|
| `Vector3` | Matemáticas de vectores 3D (suma, resta, producto punto, etc.) |
| `Matrix4` | Matrices 4x4 para transformaciones 3D y rotaciones |
| `GridPosition` | Posición de grid de cada cubito en el cubo 3x3x3 |
| `SmallCube` | Representa cada cubito individual con posición y colores |
| `Camera` | Sistema de cámara con proyección perspectiva |
| `RubiksCube` | Lógica principal del cubo, animaciones y rotaciones |
| `Game` | Loop principal, manejo de eventos e interfaz |

### 🎨 Características Técnicas
- **Matemáticas 3D puras**: Implementación completa de vectores y matrices
- **Sistema de animación**: Easing cúbico para movimientos suaves
- **Renderizado por profundidad**: Los cubitos se dibujan en orden correcto
- **Proyección perspectiva**: Cámara 3D realista
- **Interfaz intuitiva**: Panel de control lateral
- **60 FPS**: Renderizado fluido y responsivo

## 🎯 Funcionalidades Avanzadas

### ✨ Sistema de Animaciones
- **Duración configurable**: 500ms por defecto
- **Easing función**: Ease-out cúbico para transiciones naturales
- **Estado de animación**: Previene múltiples rotaciones simultáneas
- **Rotaciones por eje**: Cada cara rota en su eje correspondiente

### 🎨 Sistema de Renderizado
- **Backface culling**: Solo renderiza caras visibles
- **Z-sorting**: Ordena cubitos por distancia a la cámara
- **Proyección perspectiva**: Conversión 3D a 2D realista
- **Colores dinámicos**: Caras externas coloreadas, internas negras

## 🚀 Posibles Mejoras y Extensiones

### 🎮 Gameplay
- [ ] **Algoritmos de resolución** (CFOP, Roux, Petrus)
- [ ] **Temporizador** para medir tiempo de resolución
- [ ] **Contador de movimientos** y estadísticas
- [ ] **Historial de movimientos** con función de deshacer
- [ ] **Diferentes tamaños** de cubo (2x2, 4x4, 5x5)
- [ ] **Modos de dificultad** y challenges

### 🎨 Visuales
- [ ] **Iluminación mejorada** con sombras dinámicas
- [ ] **Texturas realistas** en lugar de colores sólidos
- [ ] **Efectos de partículas** durante las rotaciones
- [ ] **Temas visuales** (neón, retro, minimalista)
- [ ] **Modo wireframe** para debugging
- [ ] **Antialiasing** y suavizado de bordes

### 🔧 Técnicas
- [ ] **Optimización del renderizado** con Z-buffer
- [ ] **Rotaciones inversas** (Shift + tecla)
- [ ] **Rotaciones de capas medias** (M, E, S moves)
- [ ] **Notación de algoritmos** estándar
- [ ] **Guardado/carga** de estados del cubo
- [ ] **Rotaciones de doble capa** (r, u, f moves)

### 📱 Interfaz
- [ ] **Menú principal** con opciones y configuración
- [ ] **Tutorial interactivo** para principiantes
- [ ] **Estadísticas detalladas** de resolución
- [ ] **Configuración de controles** personalizable
- [ ] **Modo pantalla completa** y redimensionable
- [ ] **Múltiples idiomas**

### 🤖 IA y Algoritmos
- [ ] **Solver automático** con algoritmos conocidos
- [ ] **Generación de scrambles** óptimos
- [ ] **Análisis de patrones** y reconocimiento
- [ ] **IA para aprendizaje** de resolución
- [ ] **Optimización de movimientos** para speed-solving

## 🎓 Conceptos de Programación Demostrados

- **Programación Orientada a Objetos**: Clases bien estructuradas
- **Matemáticas 3D**: Vectores, matrices, rotaciones
- **Algoritmos de renderizado**: Proyección, culling, sorting
- **Manejo de eventos**: Mouse, teclado, UI
- **Animaciones**: Interpolación y easing
- **Arquitectura de juegos**: Game loop, estados, rendering pipeline

## 🐛 Debugging y Desarrollo

### 🔍 Características de Debug
- Coordenadas de grid visibles en userData
- Sistema de logging para rotaciones
- Validación de posiciones después de rotaciones
- Estado de animación claramente definido

### 🧪 Testing
Para probar diferentes funcionalidades:
```python
# Rotar cara específica
cube.rotate_face('R')

# Aplicar rotación inmediata (para testing)
cube.apply_face_rotation_immediately('U')

# Verificar posiciones de grid
for cube in rubiks_cube.cubes:
    print(f"Cube {cube.id}: Grid({cube.grid_position.x}, {cube.grid_position.y}, {cube.grid_position.z})")
```

## 📝 Notas de Implementación

### ⚠️ Limitaciones Actuales
- **Rotaciones de grid**: Simplificadas, podrían necesitar mejoras para rotaciones complejas
- **Detección de estado resuelto**: No implementada automáticamente
- **Algoritmos de resolución**: No incluidos en versión base
- **Persistencia**: No guarda estado entre sesiones

### 🔧 Optimizaciones Posibles
- **Frustum culling**: No renderizar objetos fuera de vista
- **Level of detail**: Reducir detalle en objetos distantes
- **Batch rendering**: Agrupar operaciones de renderizado
- **Multithreading**: Separar lógica de renderizado

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Algunas áreas donde puedes ayudar:

1. **Algoritmos de resolución**: Implementar CFOP, Roux, etc.
2. **Mejoras visuales**: Texturas, iluminación, efectos
3. **Optimización**: Rendimiento y fluidez
4. **UI/UX**: Interfaz más intuitiva y atractiva
5. **Testing**: Casos de prueba y validación
6. **Documentación**: Comentarios **y** guías

## 📜 Licencia

Este proyecto está bajo licencia MIT. Siéntete libre de usar, modificar y distribuir el código.

## 🎉 Créditos

Desarrollado como demostración de programación 3D en Python puro, inspirado en el clásico cubo de Rubik inventado por Ernő Rubik en 1974.

---

**¡Disfruta resolviendo el cubo! 🎲✨**
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

# Vertex Shader and Fragment Shader code (GLSL)
VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 position;
void main()
{
    gl_Position = vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 color;
void main()
{
    color = vec4(1.0, 0.0, 0.0, 1.0); // Red Color
}
"""

# Initialize Pygame and set up OpenGL context
pygame.init()
pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption('Pygame + PyOpenGL: Shader Example')

# Compile and link shaders
shader = compileProgram(
    compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
    compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
)
glUseProgram(shader)

# Define the vertices of a triangle (in normalized device coordinates)
vertices = np.array([
    [-0.5, -0.5, 0.0],  # Bottom left
    [ 0.5, -0.5, 0.0],  # Bottom right
    [ 0.0,  0.5, 0.0]   # Top
], dtype=np.float32)

# Generate a Vertex Array Object (VAO) and Vertex Buffer Object (VBO)
VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)

# Bind VAO and VBO, upload the vertex data
glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# Specify the layout of the vertex data (position attribute)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))

# Unbind the VAO (optional)
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Bind the VAO and draw the triangle
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)

    # Swap buffers
    pygame.display.flip()

# Cleanup
glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO])
pygame.quit()

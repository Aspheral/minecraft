#ifndef SOLAR_FULLSCREEN_VERTEX_GLSL
#define SOLAR_FULLSCREEN_VERTEX_GLSL

out vec2 texcoord;

void main() {
    gl_Position = ftransform();
    texcoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
}

#endif

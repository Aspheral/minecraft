#ifndef SOLAR_DEFERRED_FRAGMENT_GLSL
#define SOLAR_DEFERRED_FRAGMENT_GLSL

#include "/lib/core/buffers.glsl"

uniform sampler2D colortex0;

in vec2 texcoord;

layout(location = 0) out vec4 sceneColor;

void main() {
    sceneColor = texture(colortex0, texcoord);
}

#endif

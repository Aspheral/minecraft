#ifndef SOLAR_FINAL_FRAGMENT_GLSL
#define SOLAR_FINAL_FRAGMENT_GLSL

#include "/lib/core/color.glsl"

uniform sampler2D colortex0;

in vec2 texcoord;
layout(location = 0) out vec4 color;

void main() {
    vec3 displayColor = solarToDisplayApprox(texture(colortex0, texcoord).rgb);
    color = vec4(displayColor, 1.0);
}

#endif

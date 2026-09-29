#ifndef SOLAR_GBUFFER_VERTEX_GLSL
#define SOLAR_GBUFFER_VERTEX_GLSL

#include "/lib/core/space.glsl"
#include "/lib/core/encoding.glsl"

out vec2 solarTexcoord;
out vec2 solarLightcoord;
out vec4 solarVertexColor;
out vec3 solarViewNormal;

void main() {
    gl_Position = ftransform();
    solarTexcoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    solarLightcoord = solarNormalizeLightmapCoord(
        (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy
    );
    solarVertexColor = gl_Color;
    solarViewNormal = solarSafeNormalize(gl_NormalMatrix * gl_Normal);
}

#endif

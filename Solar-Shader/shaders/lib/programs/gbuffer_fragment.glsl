#ifndef SOLAR_GBUFFER_FRAGMENT_GLSL
#define SOLAR_GBUFFER_FRAGMENT_GLSL

#include "/lib/core/buffers.glsl"
#include "/lib/core/color.glsl"
#include "/lib/surface/surface_encode.glsl"

uniform sampler2D gtexture;
uniform float alphaTestRef = 0.1;

in vec2 solarTexcoord;
in vec2 solarLightcoord;
in vec4 solarVertexColor;
in vec3 solarViewNormal;

/* RENDERTARGETS: 0,1 */
layout(location = 0) out vec4 sceneColor;
layout(location = 1) out vec4 surfaceTarget;

void main() {
    vec4 sourceColor = texture(gtexture, solarTexcoord) * solarVertexColor;
    if (sourceColor.a < alphaTestRef) {
        discard;
    }

    sceneColor = vec4(solarToLinearApprox(sourceColor.rgb), 1.0);

    SurfaceData surface;
    surface.normal = solarSafeNormalize(solarViewNormal);
    surface.blockLight = solarLightcoord.x;
    surface.skyLight = solarLightcoord.y;
#ifdef SOLAR_PROGRAM_TERRAIN_CUTOUT
    surface.surfaceClass = 2;
#else
    surface.surfaceClass = 1;
#endif
    surfaceTarget = solarEncodeSurface(surface);
}

#endif

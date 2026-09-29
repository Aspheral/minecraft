#ifndef SOLAR_GBUFFER_FRAGMENT_GLSL
#define SOLAR_GBUFFER_FRAGMENT_GLSL

#include "/lib/core/buffers.glsl"
#include "/lib/core/color.glsl"
#include "/lib/surface/surface_encode.glsl"

#if defined(SOLAR_PROGRAM_TEXTURED_LIT) || defined(SOLAR_PROGRAM_TERRAIN) || defined(SOLAR_PROGRAM_TERRAIN_SOLID) || defined(SOLAR_PROGRAM_TERRAIN_CUTOUT) || defined(SOLAR_PROGRAM_ENTITIES) || defined(SOLAR_PROGRAM_BLOCK)
#define SOLAR_ROLE_METADATA
#endif

#if defined(SOLAR_PROGRAM_BASIC) || defined(SOLAR_PROGRAM_SKY_BASIC)
#define SOLAR_ROLE_UNTEXTURED
#endif

#if defined(SOLAR_PROGRAM_PARTICLES) || defined(SOLAR_PROGRAM_SKY_TEXTURED) || defined(SOLAR_PROGRAM_HAND_WATER) || defined(SOLAR_PROGRAM_WATER) || defined(SOLAR_PROGRAM_WEATHER) || defined(SOLAR_PROGRAM_ENTITIES_TRANSLUCENT) || defined(SOLAR_PROGRAM_BLOCK_TRANSLUCENT) || defined(SOLAR_PROGRAM_LIGHTNING)
#define SOLAR_ROLE_PRESERVE_ALPHA
#endif

uniform sampler2D gtexture;
uniform float alphaTestRef = 0.1;

in vec2 solarTexcoord;
in vec2 solarLightcoord;
in vec4 solarVertexColor;
in vec3 solarViewNormal;

layout(location = 0) out vec4 sceneColor;

#ifdef SOLAR_ROLE_METADATA
layout(location = 1) out vec4 surfaceTarget;
#endif

void main() {
#ifdef SOLAR_ROLE_UNTEXTURED
    vec4 sourceColor = solarVertexColor;
#else
    vec4 sourceColor = texture(gtexture, solarTexcoord) * solarVertexColor;
#endif

#ifndef SOLAR_ROLE_PRESERVE_ALPHA
    if (sourceColor.a < alphaTestRef) {
        discard;
    }
#endif

#ifdef SOLAR_ROLE_METADATA
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
#else
    sceneColor = vec4(solarToLinearApprox(sourceColor.rgb), sourceColor.a);
#endif
}

#endif

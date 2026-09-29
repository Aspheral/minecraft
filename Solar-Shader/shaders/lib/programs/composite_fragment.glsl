#ifndef SOLAR_COMPOSITE_FRAGMENT_GLSL
#define SOLAR_COMPOSITE_FRAGMENT_GLSL

#include "/lib/config.glsl"
#include "/lib/core/buffers.glsl"
#include "/lib/core/space.glsl"
#include "/lib/surface/surface_decode.glsl"
#include "/lib/debug/debug_view.glsl"

uniform sampler2D colortex0;
uniform sampler2D colortex1;
uniform sampler2D depthtex1;
uniform mat4 gbufferProjectionInverse;
uniform float far;

in vec2 texcoord;

layout(location = 0) out vec4 sceneColor;

void main() {
#if DEBUG_VIEW == 0
    sceneColor = texture(colortex0, texcoord);
#endif

#if DEBUG_VIEW == 1
    SurfaceData surface = solarDecodeSurface(texture(colortex1, texcoord));
    sceneColor = vec4(
        surface.surfaceClass == 0 ? vec3(0.0) : solarDebugNormal(surface),
        1.0
    );
#endif

#if DEBUG_VIEW == 2
    float depth = texture(depthtex1, texcoord).r;
    vec3 viewPosition = solarReconstructViewPosition(
        texcoord,
        depth,
        gbufferProjectionInverse
    );
    sceneColor = vec4(solarDebugPosition(viewPosition, far), 1.0);
#endif

#if DEBUG_VIEW == 3
    SurfaceData surface = solarDecodeSurface(texture(colortex1, texcoord));
    sceneColor = vec4(
        surface.surfaceClass == 0 ? vec3(0.0) : solarDebugLight(surface),
        1.0
    );
#endif

#if DEBUG_VIEW == 4
    SurfaceData surface = solarDecodeSurface(texture(colortex1, texcoord));
    sceneColor = vec4(solarDebugSurfaceClass(surface), 1.0);
#endif
}

#endif

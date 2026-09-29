#ifndef SOLAR_SURFACE_DECODE_GLSL
#define SOLAR_SURFACE_DECODE_GLSL

#include "/lib/surface/surface_data.glsl"
#include "/lib/core/encoding.glsl"

SurfaceData solarDecodeSurface(vec4 packed) {
    vec2 lights = solarUnpackLights(packed.b);
    return SurfaceData(
        solarOctDecode(packed.rg),
        lights.y,
        lights.x,
        solarDecodeSurfaceClass(packed.a)
    );
}

#endif

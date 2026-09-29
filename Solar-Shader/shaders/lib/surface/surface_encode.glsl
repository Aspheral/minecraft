#ifndef SOLAR_SURFACE_ENCODE_GLSL
#define SOLAR_SURFACE_ENCODE_GLSL

#include "/lib/surface/surface_data.glsl"
#include "/lib/core/encoding.glsl"

vec4 solarEncodeSurface(SurfaceData surface) {
    vec2 encodedNormal = solarOctEncode(surface.normal);
    float encodedLights = solarPackLights(surface.blockLight, surface.skyLight);
    float encodedClass = solarEncodeSurfaceClass(surface.surfaceClass);
    return vec4(encodedNormal, encodedLights, encodedClass);
}

#endif

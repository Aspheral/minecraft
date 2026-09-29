#ifndef SOLAR_DEBUG_VIEW_GLSL
#define SOLAR_DEBUG_VIEW_GLSL

#include "/lib/surface/surface_data.glsl"

vec3 solarDebugNormal(SurfaceData surface) {
    return surface.normal * 0.5 + 0.5;
}

vec3 solarDebugPosition(vec3 viewPosition, float farPlane) {
    float normalizedDistance = clamp(
        length(viewPosition) / max(farPlane, 1e-4),
        0.0,
        1.0
    );
    return vec3(normalizedDistance);
}

vec3 solarDebugLight(SurfaceData surface) {
    return vec3(surface.blockLight, surface.skyLight, 0.0);
}

vec3 solarDebugSurfaceClass(SurfaceData surface) {
    if (surface.surfaceClass == 1) {
        return vec3(1.0);
    }
    if (surface.surfaceClass == 2) {
        return vec3(0.0, 1.0, 0.0);
    }
    if (surface.surfaceClass == 3) {
        return vec3(1.0, 0.0, 1.0);
    }
    return vec3(0.0);
}

#endif

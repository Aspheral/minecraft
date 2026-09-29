#ifndef SOLAR_SURFACE_DATA_GLSL
#define SOLAR_SURFACE_DATA_GLSL

struct SurfaceData {
    vec3 normal;
    float skyLight;
    float blockLight;
    int surfaceClass;
};

#endif

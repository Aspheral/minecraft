#ifndef SOLAR_SPACE_GLSL
#define SOLAR_SPACE_GLSL

vec2 solarNormalizeLightmapCoord(vec2 rawLightmapUV) {
    return clamp(
        rawLightmapUV / (30.0 / 32.0) - vec2(1.0 / 32.0),
        vec2(0.0),
        vec2(1.0)
    );
}

vec3 solarReconstructViewPosition(vec2 uv, float depth, mat4 projectionInverse) {
    vec4 clipPosition = vec4(
        uv * 2.0 - 1.0,
        depth * 2.0 - 1.0,
        1.0
    );
    vec4 viewPosition = projectionInverse * clipPosition;
    return viewPosition.xyz / viewPosition.w;
}

#endif

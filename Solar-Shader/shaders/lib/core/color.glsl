#ifndef SOLAR_COLOR_GLSL
#define SOLAR_COLOR_GLSL

vec3 solarToLinearApprox(vec3 encodedColor) {
    return pow(max(encodedColor, vec3(0.0)), vec3(2.2));
}

vec3 solarToDisplayApprox(vec3 linearColor) {
    return pow(max(linearColor, vec3(0.0)), vec3(1.0 / 2.2));
}

#endif

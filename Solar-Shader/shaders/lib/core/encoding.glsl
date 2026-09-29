#ifndef SOLAR_ENCODING_GLSL
#define SOLAR_ENCODING_GLSL

vec3 solarSafeNormalize(vec3 value) {
    float lengthSquared = dot(value, value);
    if (lengthSquared <= 1e-12) {
        return vec3(0.0, 1.0, 0.0);
    }
    return value * inversesqrt(lengthSquared);
}

vec2 solarSignNotZero(vec2 value) {
    return vec2(
        value.x < 0.0 ? -1.0 : 1.0,
        value.y < 0.0 ? -1.0 : 1.0
    );
}

vec2 solarOctEncode(vec3 normal) {
    vec3 n = solarSafeNormalize(normal);
    n /= abs(n.x) + abs(n.y) + abs(n.z);
    if (n.z < 0.0) {
        n.xy = (1.0 - abs(n.yx)) * solarSignNotZero(n.xy);
    }
    return clamp(n.xy * 0.5 + 0.5, 0.0, 1.0);
}

vec3 solarOctDecode(vec2 encoded) {
    vec2 f = clamp(encoded, 0.0, 1.0) * 2.0 - 1.0;
    vec3 n = vec3(f, 1.0 - abs(f.x) - abs(f.y));
    float t = clamp(-n.z, 0.0, 1.0);
    n.xy += vec2(
        n.x >= 0.0 ? -t : t,
        n.y >= 0.0 ? -t : t
    );
    return solarSafeNormalize(n);
}

float solarPackLights(float blockLight, float skyLight) {
    uint blockCode = uint(floor(clamp(blockLight, 0.0, 1.0) * 31.0 + 0.5));
    uint skyCode = uint(floor(clamp(skyLight, 0.0, 1.0) * 31.0 + 0.5));
    uint packed = blockCode | (skyCode << 5u);
    return float(packed) / 1023.0;
}

vec2 solarUnpackLights(float encoded) {
    uint packed = uint(floor(clamp(encoded, 0.0, 1.0) * 1023.0 + 0.5));
    float blockLight = float(packed & 31u) / 31.0;
    float skyLight = float((packed >> 5u) & 31u) / 31.0;
    return vec2(blockLight, skyLight);
}

float solarEncodeSurfaceClass(int surfaceClass) {
    int value = min(max(surfaceClass, 0), 3);
    return float(value) / 3.0;
}

int solarDecodeSurfaceClass(float encoded) {
    int value = int(floor(clamp(encoded, 0.0, 1.0) * 3.0 + 0.5));
    return min(max(value, 0), 3);
}

#endif

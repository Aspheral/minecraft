#ifndef SOLAR_QUALITY_GLSL
#define SOLAR_QUALITY_GLSL

struct SolarQuality {
    float global;
    float atmosphere;
    float clouds;
    float shadows;
    float reflections;
    float indirectLight;
    float postProcessing;
};

SolarQuality solarGetQuality() {
    return SolarQuality(
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
    );
}

#endif

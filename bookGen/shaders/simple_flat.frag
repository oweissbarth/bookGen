in vec3 vLighting;
in vec3 vNormal;
layout(location = 0) out vec4 fragColor;
uniform vec3 color;

void main()
{
    fragColor = vec4(color * vLighting, 1.0);
}

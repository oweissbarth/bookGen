void main() {
    vec3 ambientLight = vec3(0.5, 0.5, 0.5);
    vec3 directionalLightColor = vec3(0.3, 0.3, 0.3);
    vec3 directionalVector = vec3(0.612, 0.57, 0.54);

    vec4 transformedNormal = normal_mat * vec4(nrm, 1.0);

    float directional = max(dot(transformedNormal.xyz, directionalVector), 0.0);

    vLighting = ambientLight + (directionalLightColor * directional);
    vNormal = transformedNormal.xyz;

    gl_Position = modelviewprojection_mat * vec4(pos, 1.0);

}

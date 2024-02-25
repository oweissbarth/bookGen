void main()
{
    v_ArcLength = arcLength;
    gl_Position = u_ViewProjectionMatrix * vec4(pos, 1.0f);
}
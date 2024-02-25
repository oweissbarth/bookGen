void main()
{
    if (step(sin(v_ArcLength * u_Scale), 0.5) == 1) discard;
    fragColor = vec4(1.0);
}
/*
 * Simple ambient light with ambient occlusion support.
 */


light envlight (
   float intensity = 1;
   color lightcolor = 1;
   string filename = "occlmap.sm";
   float samples = 8;
   float blur = 0.01;
   float bias = 0.01;
   color shadowcolor = color(0,0,0);
)
{
   float  o = occlusion (filename, Ps, Ns, 0,
                    "blur", blur,
                    "samples", samples,
                    "bias", bias);
   Cl = intensity * mix(lightcolor, shadowcolor, o);
}

surface bakelightmap (
                    string bakefilename = "sss.bake";
                    string texturename = "";
                    )
{
color Ct;
if (texturename != "")
       Ct = color texture (texturename);
else Ct = 1;
  
normal Nf = faceforward (normalize(N),I);
color sss = Ct * diffuse(Nf);
bake (bakefilename, s, t, sss); 
}

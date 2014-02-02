
//(c) MakeHuman team 2007-2010 - www.makehuman.org
//Photorealistic skin shader for renderman engine (tested on Aqsis)

color
wrappeddiffuse( normal N; float wrappedangle )
{
	color C = 0;
	normal Nn;
    vector Ln;
    extern point P;
    float wrapper;
	Nn = normalize(N);
	illuminance( P, Nn, PI ) {
		Ln = normalize(L);
        wrapper = 1 - acos(Ln.Nn) / wrappedangle;
        if ( wrapper >= 0){
		    C += Cl * wrapper;
            }
        }
	return C;
}


color screen(color F; color B)
    {
       color W = (1,1,1);
	   color R = W - (W - F)*(W - B);
	   return R;
    }

surface skin(
			string skintexture = "";
            string refltexture = "";
			float Ks = .5;
            float Ka = .5;
            float Kd = .8;
			float roughness = .1;
            float Value = 1.0

            )
{
    normal Nf;
    vector V;
	color Cflat;
    color Crefl;

    color Cscatt1 = color(1.0,.81,.23);
    color Cscatt2 = color(.6,.4,.4);
    color Cscatt3 = color(.83,.69,.63);

	if (skintexture != ""){
        Cflat = color texture (skintexture);
        Oi = float texture (skintexture[3], "fill", 1);        
        }
    else Cflat = 1;
    
    if (refltexture != ""){
        Crefl = color texture (refltexture);          
        }
    else Crefl = 1;

	Nf = faceforward (normalize(N),I);
    V = -normalize(I);
    
	float angle_ramp = max(0,(1-( V.Nf)));
	float  noise3D = float noise(P*100);
    float skin_matte = comp(diffuse(Nf), 0);
    color glancing_highlight = angle_ramp*skin_matte;

    color layer1 = max(0,min(wrappeddiffuse(Nf, 1.6)*Cscatt1,0.2));
    color layer2 = max(0,min(wrappeddiffuse(Nf, 1.65)*Cscatt2,0.2));
    color layer3 = Ks*Crefl*noise3D*specular(Nf,V,roughness);
    color layer4 = angle_ramp * max(0,min(wrappeddiffuse(Nf, 1.65),0.3));
    color layer5 = color(1,1,1) + pow((1.0 - skin_matte),6)*color(1,0,0);

    Ci = screen(layer1,layer2);
    Ci = screen(Ci,layer3);
    Ci = screen(Ci,layer4) * 2 * layer5;

    float desaturate_factor = max(0,pow(skin_matte,3)*50*noise3D);
    color desaturate_tone = color(comp(Ci, 0),comp(Ci, 0),comp(Ci, 0));

    Ci = mix(Ci,desaturate_tone,desaturate_factor)+glancing_highlight;

    Ci = Cflat*Oi*(ambient()+(Kd*Ci)*(Cs*color(1,0.5,0.1)*Value));
    //Ci = Oi*(ambient()+Cflat*Ci);
    
    float R = comp(Ci,0);
    float G = comp(Ci,1);
    float B = comp(Ci,2);
    
    color desat = (R+G+B)/3;
    Ci = mix(Ci,desat,desat);

}

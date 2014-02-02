






surface
cornea ( float Ks = 1.8;
         float roughness = .035;
	     color specularcolor = 1;
         color opacity = 0.01;
     )
{    
    normal Nf = faceforward (normalize(N),I); 
    vector V = -normalize(I);
    vector caustic_vector = vector(-1, -1, -1);
    
    float angle_ramp = (max(0,(1-( V.Nf))))/4;

    //Fake caustic
    color C = 0;
    illuminance( P, Nf, PI/2 ){
    float Lx = float xcomp(L);
    float Ly = float ycomp(L);
    float Lz = float zcomp(L);    
    vector causticVector = vector(-Lx, Ly, Lz);    
    C += Cl * specularbrdf (normalize(causticVector), Nf, V, roughness*3);
    }
    
       
    color Spec = Ks*specular(Nf,-normalize(I),roughness);
    
    Oi = opacity+Spec;
    Ci = angle_ramp+ C + specularcolor * Spec;
}

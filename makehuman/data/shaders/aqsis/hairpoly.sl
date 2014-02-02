//UNDER GPL LICENSE
//(c) Makehuman team 2006

surface hairpoly( 
            string colortexture = "";             
            float Kd = 1;
            float Ks = 1;             		
            float Ka = 1;      	
			  ) 
   {	  
    

    color Ct;
    normal Nf = faceforward (normalize(N),I);
	
	if (colortexture != "")
	    Ct = color texture (colortexture);
        Oi = float texture (colortexture[3], "fill", 1);  
        
   
    Ci = Oi * (Ct * Cs * (Ka*ambient() + Kd*diffuse(Nf)));




}

//UNDER GPL LICENSE
//(c) Makehuman team 2006

surface skin2( 
            string colortexture = "";  
            string roughtexture = "";  			
            string spectexture = ""; 
            string ssstexture = ""; 
            string aotexture = "";            
			float poresdensity = 1000;
			float sweat = .25;
            float Kd = 3;
            float Ks = 0.001;             		
            float Ka = 1;
            float melanin = 1;
            float Ksss = 0;	            	
			  ) 
   {	
   
    //Precalculated Ambient Occlusion values
    float ambientOcclusion = 1;
    
   
    //AMBIENT OCCLUSION TEXTURES
	if (aotexture != "")
	ambientOcclusion = float texture(aotexture);   
    

	float roughness = 1;
  	float specularity = 1;

	normal Nn = faceforward(normalize(N), I);
	vector Vf = -normalize(I);
	float ill = 0;
	Oi = Os;
	//float f = (float noise((poresdensity)*P));
	float f2 = 1+(float noise(poresdensity*P))/2;
    float f3 = 1+(float noise(poresdensity*P))/6;
	
	//SHADOWS
	float dark_side = 0;	
    float dark_side2 = 0;    
	float is_under_light = comp(diffuse(Nn),1);	
	
	//COLORS 
	color skin_color = Cs;
	color final_skin_color = skin_color;
	color ssslight= 0;
    
	
	//RAMP COLORS
	float angle_ramp = (max(0,(1-( Vf.Nn))))/4;//POSSIBILE PARAMETRO QUI.
	float angle_ramp2 = max(0,(1-( Vf.Nn)));//POSSIBILE PARAMETRO QUI.
	color glancing_highlight = max(0,((1-(( Vf.Nn)/0.6))*is_under_light))*0.1;//POSSIBILE PARAMETRO QUI.	

	//TEXTURES
	if (roughtexture != "")
	roughness = float texture(roughtexture);	
	
	if (spectexture != "")
	     specularity = f2 * float texture (spectexture);	 
	
	if (colortexture != "")
	    skin_color = color texture (colortexture);
        Oi = float texture (colortexture[3], "fill", 1);  
        
    if (ssstexture != ""){
	    ssslight= color texture (ssstexture)*3;        
        }
	

	//LIGHT MODEL
    illuminance (P, Nn, PI){
    ill = normalize (L). normalize(Nn);	       
    dark_side += pow(3,(ill-1))*comp(Cl,0);	
    dark_side2 += pow(100,(ill-1))*comp(Cl,0);			
	}


	final_skin_color = skin_color * Ka * ambientOcclusion; //ambient();		
	float CiR, CiG, CiB;
	CiR = comp(final_skin_color, 0);
	CiG = comp(final_skin_color, 1);
	CiB = comp(final_skin_color, 2);
	
	CiR = CiR - (angle_ramp*0.05*is_under_light*2);
	CiG = CiG -(angle_ramp*0.07*is_under_light*2);
	CiB = CiB- (angle_ramp*0.1*is_under_light*2);

	
	setcomp (final_skin_color, 0, CiR);
	setcomp (final_skin_color, 1, CiG);
	setcomp (final_skin_color, 2, CiB);
	
	final_skin_color *= dark_side;	
	final_skin_color *= skin_color*Ka/2;
	final_skin_color += glancing_highlight * f2;	
	
	final_skin_color += specularity  * Ks*specular(Nn,-normalize(I),roughness)* angle_ramp2;	
	final_skin_color = final_skin_color * Kd;
		
    //DESATURATE THE HIGHTLIGHTS
	float CiR2, CiG2, CiB2;
	CiR2 = comp(final_skin_color, 0);
	CiG2 = comp(final_skin_color, 1);
	CiB2 = comp(final_skin_color, 2);
	
	float maxVal = max(CiR2,CiG2,CiB2);
	
	CiR2 = ((clamp((dark_side2),0.1,0.6))*(maxVal - CiR2)) + CiR2;
	CiG2 = ((clamp((dark_side2),0.1,0.6))*(maxVal - CiG2)) + CiG2;
	CiB2 = ((clamp((dark_side2),0.1,0.6))*(maxVal - CiB2)) + CiB2;	
	
	setcomp (final_skin_color, 0, CiR2);
	setcomp (final_skin_color, 1, CiG2);
	setcomp (final_skin_color, 2, CiB2);
    
    final_skin_color = final_skin_color*Kd;
	
    //SWEAT    
    final_skin_color += specularity  * Ks*specular(Nn,-normalize(I),0.08)* dark_side2 * 0.05;
    final_skin_color += specularity  * Ks*specular(Nn,-normalize(I),0.8)* dark_side2 * 0.01;	

    Ci = final_skin_color * (1/(melanin+1))*f3;
    Ci = mix(Ci,ssslight,Ksss);
    
    Ci = Ci + specularity * sweat * specular(Nn,-normalize(I),0.1);
	

	
Ci *= Oi;




}

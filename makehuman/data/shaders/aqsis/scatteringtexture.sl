//(c) MakeHuman team 2009 - www.makehuman.org
surface scatteringtexture (
			float scattering = 1;
            float Kr = 0.003;
            float Kg = 0.002;
            float Kb = 0.001;
            string texturename = "";
            ) 
{		
	float Red = 1;
	float Green = 1;
	float Blue = 1;
    float Red1 = 1;
	float Green1 = 1;
	float Blue1 = 1;
    float Red2 = 1;
	float Green2 = 1;
	float Blue2 = 1;
	if (texturename != ""){		
        Red1 = comp(color texture (texturename, "blur", scattering*Kr),0);
		Green1 = comp(color texture (texturename, "blur", scattering*Kg),1);
		Blue1 = comp(color texture (texturename, "blur", scattering*Kb),2);
        
        Red2 = comp(color texture (texturename, "blur", scattering*Kr*5),0);
		Green2 = comp(color texture (texturename, "blur", scattering*Kg*5),1);
		Blue2 = comp(color texture (texturename, "blur", scattering*Kb*5),2);
		}   
    Red = mix(Red1,Red2,0.5);
    Green = mix(Green1,Green2,0.25);
    Blue = mix(Blue1,Blue2,0.35);
    
	setcomp(Ci,0,Red);
	setcomp(Ci,1,Green);
	setcomp(Ci,2,Blue);	
}

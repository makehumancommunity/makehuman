//(c) MakeHuman team 2007 - www.makehuman.org




displacement
skinbump(
	float Km = 0.1;
	string bumptexture = "";
    float truedisp = 0;)
{
	if( bumptexture != "" ){
        float amp = Km * float texture(bumptexture, s, t );
        if (truedisp == 1){
            P += amp * normalize(N);
            N = calculatenormal(P);
            }
        else{            
            N = calculatenormal(P + (normalize(N) * amp));
            }		
        }
}
 




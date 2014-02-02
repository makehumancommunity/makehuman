surface mixer(float tValues[54] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
                    string textures[54] = {"","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""};
)
{
float count;
float tVal = 0;
color mix = color(0,0,0);

for (count = 0; count < 54; count=count+1)
  {
  tVal = tValues[count];
  if (tVal > 0)
    {    
    string texturename = textures[count];    
    mix = mix + color texture(texturename)*tVal;
    }  
  }
Ci = mix;
} 



#ifndef (%%name%%_Material)

#declare %%name%%_Texture =
    texture {
        pigment {rgb 1}
        finish {
            specular 0
            roughness 1
            ambient %%ambient%%
            diffuse %%diffuse%%
        }
    }
    texture {
        pigment {rgbf 1}
        %%normal%%
        finish {
            specular %%specular%%*(1-%%moist%%)
            roughness 2*%%roughness%%
            ambient 0
            diffuse 0
        }
    }
    texture {
        %%pigmentf1%%
        %%normal%%
        finish { 
            specular %%specular%%*%%moist%%
            roughness %%roughness%%
            ambient 0
            diffuse 0
        }
    }

#declare %%name%%_Material = material {
    texture {
        uv_mapping
        pigment_pattern {%%alpha%%}
        texture_map {
            [0 pigment {color transmit 1.0}]
            [1 %%name%%_Texture]
        }
    }
}

#end


#ifndef (%%name%%_Material)

#declare %%name%%_hairtex0 =
    texture {
        %%pigment%%          
        finish {
            specular 0
            ambient %%ambient%%
            diffuse %%diffuse%% - %%specular%%
        }
    }

#declare %%name%%_hairtex1 =
    texture {
        pigment {rgb 1}
        %%normal%%
        finish {
            specular %%specular%%
            roughness 2*%%roughness%%
            ambient %%ambient%%
            diffuse %%diffuse%% - %%specular%%
        }
    }
    texture {
        %%pigmentf1%%         
        %%normal%%
        finish {
            specular %%specular%%
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
            [0 %%name%%_hairtex0]
            [1 %%name%%_hairtex1]    
        }
    }
}
#end   

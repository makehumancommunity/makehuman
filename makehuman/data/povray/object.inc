#ifndef (%%name%%_Material)
#declare %%name%%_Texture =
    texture {
        %%pigment%%
        %%normal%%
        finish {
            specular %%specular%%
            roughness %%roughness%% 
            ambient %%ambient%%
            diffuse %%diffuse%%
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


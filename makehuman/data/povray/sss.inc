
// Create the skin material.
// This texture implements a SubSurface Scattering method
// using premade lightmaps.  
#ifndef (%%name%%_Material)                            

#declare TexMultiply_2x =
texture { // 2x multiplier layer.
        pigment { rgbf <2,2,2,1> }
        finish {
            specular 0
            ambient 0
            diffuse 0
        }
    }

#declare %%name%%_Texture =
    texture { // Red diffusion remover.
         pigment {image_map {png "%%name%%_sss_redlmap.png" interpolate 2}}
         finish {
            specular 0
            ambient -2
            diffuse 2
         }
    }
    texture { // Green diffusion remover.
         pigment {image_map {png "%%name%%_sss_greenlmap.png" interpolate 2 transmit all 1/2}}
         finish {
            specular 0
            ambient -2
            diffuse 2
         }
    }
    texture {TexMultiply_2x}    
    texture { // Blue diffusion remover.
         pigment {image_map {png "%%name%%_sss_bluelmap.png" interpolate 2 transmit all 1/2}}
         finish {
            specular 0
            ambient -2
            diffuse 2
         }
    }    
    texture { // Inverter.
        pigment { rgbf <-1,-1,-1,1> }
        finish {
            specular 0
            ambient 0
            diffuse 0
        }
    }
    texture {TexMultiply_2x} 
    texture { // Red SSS channel. High blur.
        pigment { image_map {png "%%name%%_sss_redlmap.png" interpolate 2 transmit all 1/2} }
        %%rednormal%%
        finish { 
            specular 0
            ambient 0
            diffuse 2
        }
    }
    texture {TexMultiply_2x}
    texture { // Green SSS channel. Medium blur.
        pigment { image_map {png "%%name%%_sss_greenlmap.png" interpolate 2 transmit all 1/2} }
        %%greennormal%%
        finish { 
            specular 6*%%specular%%*(1-%%moist%%)  // EpiDermal Specularity Scattering.
            roughness 2*%%roughness%%
            ambient 0
            diffuse 2
        }
    }
    texture {TexMultiply_2x}
    texture { // Blue SSS channel. No blur.
        pigment { image_map {png "%%name%%_sss_bluelmap.png" interpolate 2 transmit all 1/2} }
        %%bluenormal%%
        finish { 
            specular 0
            ambient 0
            diffuse 2
        }
    }
    texture {TexMultiply_2x}
    texture { // Ambience.
        pigment {rgbt <1, 1, 1, 1/2>}
        finish {
            specular 0
            ambient %%2xambient%%
            diffuse 0
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

#declare %%name%%_DiffuseTex =
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
            [1
                pigment_pattern {image_map {png "%%name%%_sss_alpha.png" interpolate 2}}
                texture_map {
                [0 %%name%%_DiffuseTex]
                [1 %%name%%_Texture]
                }
            ]
        }
    }
}

#end


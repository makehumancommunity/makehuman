// xxFileNamexx.pov
// xxUnderScoresxx

// This scene file illustrates the use of an include file generated from the
// MakeHuman application using the POV-Ray export functionality.
// It contains 3 examples of how to render the human figure. 
//
// This file is licensed under the terms of the CC-LGPL. 
// This license permits you to use, modify and redistribute the content.
// 
// Typical render time 1 minute (at 800x600 AA 0.3).
// The default object is about 16 POV-Ray units high and is centred at the 
// origin. 
// 
// The include file contains 3 models that can be rendered separately
// or in any combination. The models and the options available are 
// detailed in the file MakeHuman.html.  

// This file contains a series of separate examples, controlled using the 
// 'Example' variable. They typically take a few seconds to render:
//
//   Example = 0 renders the mesh2 object using the camera settings as they
//               were in the MakeHuman application when this file was generated.
//   Example = 1 renders the mesh2 object and overlays the sphere-based object  
//               and cylinder-based object.
//   Example = 2 renders the mesh2 object, the sphere-based object and the 
//               cylinder-based object, translating them so that they are 
//               each separately visible.
//   Example = 3 illustrates the use of generated mesh2 sub-surfaces and 
//               provides some experimental textures to scatter light between 
//               those surfaces.
//   Example = 4 illustrates the MakeHuman_XRayTexture texture  which provides 
//               a crude simulation of an x-ray using the POV-Ray slope pattern. 
//   Example = 5 illustrates the use of the MakeHuman_SelectedGroups array setting. 
//
//   Example = 101 gradually rotates the model through 360 degrees, given 
//                 appropriate animation options (eg. +kfi0 +kff29 +kc).
//                              
// You can use the POV-Ray animation feature to cycle through all of the above examples 
// using command-line options +kfi0 +kff4 and by using the 'frame_number' identifier as 
// follows:
//             
// #declare Example = frame_number;              

#declare Example = 0;

#include "xxLowercaseFileNamexx.inc"  
#if (file_exists("makehuman_hair.inc")) #include "makehuman_hair.inc" #end  

//
// The simplest example uses the predefined camera, the mesh object 
// and the predefined texture.
//
#if (Example=0)
  camera {MakeHuman_Camera}
  light_source {MakeHuman_LightSource}
  object {
    MakeHuman_Mesh(0)
   rotate <0,0,MakeHuman_RotateZ> 
   rotate <0,MakeHuman_RotateY,0>
   rotate <MakeHuman_RotateX,0,0>
   translate <MakeHuman_TranslateX, MakeHuman_TranslateY, MakeHuman_TranslateZ> 
    material { MakeHuman_Material} //texture {MakeHuman_Texture}
  } 
#end


//
// This example overlays the mesh object, the spheres object and the 
// cylinder object.
//
#if (Example=1)
  camera {location <-6,10,20> look_at 9*y }
  light_source {<-10,20,50>, rgb 1}
  object {
    MakeHuman_Mesh(0)
    texture {MakeHuman_Texture}
    translate -y*MakeHuman_MinExtent
  }
  object {
    MakeHuman_Spheres(0)
    pigment {rgb <2,0,0>}
    translate -y*MakeHuman_MinExtent
  }
  object {
    MakeHuman_Cylinders(0)
    pigment {rgb <2,2,0>}
    translate -y*MakeHuman_MinExtent
  }
  // Add a plane
  plane {y,0
    pigment {rgb 0.3}
    normal  {ripples 0.2 scale 5}
    finish  {reflection 0.8}
  }
#end

//
// This example displays 3 separate objects, one showing the mesh, one made with 
// spheres and the other with cylinders.
//
#if (Example=2)
  camera {location <-6,10,20> look_at 9*y }
  light_source {<-10,20,50>, rgb 1}
  // Add a mesh on its own behind the original
  object {
    MakeHuman_Mesh(0)
    texture {MakeHuman_Texture}
    translate <0,-MakeHuman_MinExtent.y,-10>
    translate -z*5
  }
  
  // Add a spheres-based copy on the left
  object {
    MakeHuman_Spheres(0)
    pigment {rgb <2,0,0>}
    translate <0,-MakeHuman_MinExtent.y,-10>
    rotate y*80
    translate -z*5
  }
  
  // Add a cylinder-based copy on the left
  object {
    MakeHuman_Cylinders(0)
    pigment {rgb <0,2,0>}
    translate <0,-MakeHuman_MinExtent.y,-10>
    rotate -y*80
    translate -z*5
  } 
  
  // Add a plane
  plane {y,0
    pigment {rgb 0.3}
    normal  {ripples 0.2 scale 5}
    finish  {reflection 0.8}
  }
#end 

// This example illustrates the use of generated sub-surfaces and provides
// some experimental textures to scatter light between those surfaces.
#if (Example=3)
  camera {location <-2.5,7.5,14> look_at 6*y }
  light_source {<-.5,1,.2>*100000, rgb 0.5 rotate y*90}
  light_source {<-10,20,50>, rgb 1}
  
  global_settings{
    photons{count 1000000/3 jitter .875}
  }
  
  #default{ finish{ambient 0 }}
    
  // Base copy using the MH image map
  object {
    MakeHuman_Mesh(-0.003)
    texture {
      pigment {
        image_map {
          tga "texture.tga"
        }
      }
      finish {specular 0 diffuse 0.5 roughness .5 reflection 0}
      normal {agate 0.15 scale 0.01}
    }
  }
  
  // A middle surface with a crackle for blood vessels
  object {
    MakeHuman_Mesh(0)
    no_shadow
    texture {
      pigment{rgbf <1,.85,.8,0.995>}
    }
    texture {
      pigment {crackle turbulence 0.5 scale 0.07
        color_map {
          [0   color rgbf <1,0.6,0.75,0.7>]
          [0.1 color rgbf <1,1,1,1>]
          [1   color rgbf <1,1,1,1>]
        }
      }
      normal {crackle turbulence 0.5 scale 0.1}
      finish{ roughness .05}
    }
    interior{ ior 10.3 } 
    photons{ target refraction on }
  }
  
  // The outer surface layer
  object {
    MakeHuman_Mesh(0.003) 
    no_shadow
    double_illuminate
    texture {
      pigment{ rgbf<0.9,.7,.58,1> }
      finish{ specular .1 roughness .05 reflection 0}
    }
   // exaggerated ior
    interior{ ior 10.3 } 
    photons{ target refraction on }
  }
  
  // Add a plane
  plane {y,0.4
    pigment {rgb 0.002}
    normal  {wrinkles 0.5 scale 1}
    finish  {reflection 0.8 phong 0.5}
  }
  
  // Position a white sphere in the sky to get some reflection on the plane
  sphere {<150,120,-150>,10 pigment {rgb 2}}
#end

// This example illustrates the use of the MakeHuman_XRayTexture texture setting
#if (Example=4)
  camera {location <-3,7.3,1> look_at 7.3*y }
  object {
    MakeHuman_Mesh(0)
    texture {MakeHuman_XRayTexture}
  }
#end 

// This example illustrates the use of the hair functions.
// It requires the optional makehuman_hair.inc file. 
#if (Example=5)
  #if (file_exists("makehuman_hair.inc"))
    #include "makehuman_groupings.inc"
    #include "hair.inc"
    #include "rand.inc"
  
//    #declare MakeHuman_BaseObject = MakeHuman_Mesh(0) 
    #declare HairObject = object {Hair("")}
    #declare S = seed(1);
    union {
      
      object {HairObject}
      
//      object {Hair_HairlineAndMarkers pigment {rgb <1,1,0>}} 
      object {Hair_HairlineObject pigment {rgb <1,1,0>}} 
      
//      object {MakeHuman_Mesh(0) texture {MakeHuman_Texture}}
//      object {MakeHuman_BaseObject texture {MakeHuman_Texture}}
      scale 10 
    }
//    camera {location MakeHuman_HairCentre + <0,2.5,-2> look_at MakeHuman_HairCentre }
    camera {location (Hair_Centre + <0,0,3>)*10 look_at (Hair_Centre)*10}
    light_source {<-10,20,50>*10, rgb 1}
    light_source {<-10,-20,50>*10, rgb 1} 
  #else
    #debug "Error reading 'makehuman_hair.inc'."
    #debug "Note: This is a separately downloadable file that you don't seem to have in your include path.\n" 
  #end
#end


// This example rotates the model through 360 degrees (given appropriate animation options).
#if (Example=101)         
  background {color rgb <0,1,0>}
  camera {location <0,5.6,20> look_at 0.5*y}
  light_source {<-10,30,25>  rgb 1 
    spotlight point_at 2*y
    radius 3
    falloff 20
  } 
  light_source {< 10,50,25>, rgb <1,0.5,0.2>} 
  object {
    MakeHuman_Mesh(0) 
    texture {MakeHuman_Texture} 
    rotate -clock*360*y
  }
  cylinder {y*MakeHuman_MinExtent.y,y*(MakeHuman_MinExtent.y-0.3),3 
    pigment {rgb 0.7}
    finish {reflection 0.3}
    normal {bozo scale 0.1}
    rotate -clock*360*y
  }
  plane {y,(MakeHuman_MinExtent.y-0.35) pigment {rgb <0,1,0>}} 
  plane {z,(MakeHuman_MinExtent.x-0.35) pigment {rgb <0,1,0>}} 
#end

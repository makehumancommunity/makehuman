// makehuman_hair.inc
// ------------------

// Include file that adds hair to a model built from the MakeHuman POV-Ray 
// export include files. 
// 
// This file is licensed under the terms of the CC-LGPL. 
// This license permits you to use, modify and redistribute the content.
// 
                                        
#include "math.inc"
#include "functions.inc"

#macro MakeHuman_Hair() 
  #declare MakeHuman_HairLineAndMarkers = union {MakeHuman_CreateHairline()}
  union { 
//    object {MakeHuman_HairLineAndMarkers}
    MakeHuman_CreateHair()
  }
#end


#macro MakeHuman_CreateHair() 
  #ifndef (MakeHuman_HairRandomisationSeed) #declare MakeHuman_HairRandomisationSeed = seed(1); #end
  #ifndef (MakeHuman_HairNumber)            #declare MakeHuman_HairNumber = 100000;                #end
  #ifndef (MakeHuman_SimpleHairColor)       #declare MakeHuman_SimpleHairColor = 1;                #end 
  #ifndef (MakeHuman_HairBaseColor)         #declare MakeHuman_HairBaseColor = <1,0.6,0.3>*0.6;    #end 
  #if (!MakeHuman_SimpleHairColor)
    #ifndef(MakeHuman_HairRootPigment) 
      #declare MakeHuman_HairRootPigment = pigment {crackle 
        color_map {
          [0.0  color MakeHuman_HairBaseColor*0.33]
          [0.8  color MakeHuman_HairBaseColor*0.33]
          [1.0  color MakeHuman_HairBaseColor*1]
        }
        scale 0.15  
      }
    #end 
    #local MakeHuman_HairRootPigmentFunction = function {pigment {MakeHuman_HairRootPigment}}
  #end

  // We need to evenly position hairs at random around the hairline object, by assuming it's roughly spherical.
  // In fact we assume it's like a sphere with a cone cut out of the bottom (so we don't have to throw away too many guesses).
  #local MakeHuman_ConeAngle = 55;
  #local MakeHuman_CutDepth = cosd(MakeHuman_ConeAngle);  
  
  // Loop through finding a random position for each hair root. Thanks to Mel Siegel for a straight-forward 
  // explanation for finding a random point on a sphere at http://www.cs.cmu.edu/~mws/rpos.html
  #local MakeHuman_I = 0;
  #while (MakeHuman_I<MakeHuman_HairNumber)
    // Get a random number in the range that we need to cover a sphere with a cone cut out of it.
    // This represents the height above the centre of the sphere (assuming a unit radius) and will  
    // range from +1 to -d where 'd' is the depth that the cone cuts into the base of the sphere.
    #local MakeHuman_RH = 1-(1+MakeHuman_CutDepth)*rand(MakeHuman_HairRandomisationSeed);
    // Work out the latitude at this height and add 90 to get a rotation from the vertical.
    #local MakeHuman_RA = 90-asind(MakeHuman_RH);
    // Calculate the direction of a hair root, oriented to fit the hairline object
    #local MakeHuman_HairRootDir = vaxis_rotate(MakeHuman_HairAxis,MakeHuman_HeadLRVector,MakeHuman_RA);
    #local MakeHuman_HairRootDir = vaxis_rotate(MakeHuman_HairRootDir,MakeHuman_HairAxis,360*rand(MakeHuman_HairRandomisationSeed));

    // Trace a line out from the centre and see if it hits the hairline object
    #local MakeHuman_Normal = <0,0,0>;
    #local MakeHuman_Position = trace(MakeHuman_HairLineObject,MakeHuman_HairCentre,MakeHuman_HairRootDir,MakeHuman_Normal);
    #if (vlength(MakeHuman_Normal)!=0)
      // If the normal is pointing inwards, point it outwards (Shouldn't usually happen if mesh correctly defined).
      #if (vlength(MakeHuman_Position-MakeHuman_HairCentre+MakeHuman_Normal) < vlength(MakeHuman_Position-MakeHuman_HairCentre))
        #local MakeHuman_Normal = -MakeHuman_Normal;
      #end
      #if (MakeHuman_SimpleHairColor)
        #local MakeHuman_ThisHairColor = rgb MakeHuman_HairBaseColor*0.4;
      #else
        #local MakeHuman_ThisHairColor = MakeHuman_HairRootPigmentFunction(MakeHuman_Position.x, MakeHuman_Position.y, MakeHuman_Position.z);
      #end
      cylinder {MakeHuman_Position,MakeHuman_Position+0.05*MakeHuman_Normal,0.002 
        pigment {MakeHuman_ThisHairColor}
      }
    #end
    #local MakeHuman_I = MakeHuman_I + 1;
  #end           

#end

                                 
// This macro uses the MakeHuman_Hairline set of face groups and trims it to form a hairline object.
#macro MakeHuman_CreateHairline()
  
  // The head could be in virtually any position at more or less any orientation, so we pick use three joint 
  // positions (the centre of the head and of each eye) to locate it in 3D space.
  // 'Forward' Vector - from the 'head' joint to the midpoint between the two eyes (points slightly up from z axis in default pose).
  #declare MakeHuman_HeadFwVector = vnormalize((MakeHuman_joint_l_eye+MakeHuman_joint_r_eye)/2-MakeHuman_joint_head);
  // Left-Right Vector - from one eye to the other - ( should usually be at right angles to MakeHuman_HeadFwVector).
  #declare MakeHuman_HeadLRVector = vnormalize(MakeHuman_joint_r_eye-MakeHuman_joint_l_eye);
  // Parietal Vector - A vector at right angles to the other two, pointing up through the back of the cranium.
  #declare MakeHuman_HeadPaVector = VPerp_To_Plane(MakeHuman_HeadFwVector, MakeHuman_HeadLRVector);        
  // The physical dimensions of the head could vary, so define a 'standard' unit of measure.
  #declare MakeHuman_Units        = vlength((MakeHuman_joint_l_eye+MakeHuman_joint_r_eye)/2-MakeHuman_joint_head);
  // Estimate a centre point to get an even spread of hairs around the head
  #declare MakeHuman_HairCentre   = MakeHuman_joint_head + MakeHuman_Units*( MakeHuman_HeadPaVector*0.42 + MakeHuman_HeadFwVector*0.42);
  // We need an axis around which to randomise the hair distribution. This sticks out the centre of the back of the cranium
  #declare MakeHuman_HairAxis = vaxis_rotate(MakeHuman_HeadPaVector,MakeHuman_HeadLRVector,-21);
  
  // Set to '1' to show the 3 head vectors
  #if (1)  
    cylinder {0,MakeHuman_HeadFwVector*2,0.03 translate MakeHuman_joint_head pigment {rgb <1,0,1>}}
    cylinder {0,-MakeHuman_HeadLRVector*2,0.03 translate MakeHuman_joint_head pigment {rgb <0,1,1>}}
    cylinder {0,MakeHuman_HeadPaVector*2,0.03 translate MakeHuman_joint_head pigment {rgb <0,0,1>}}
  #end 
   
  // Calculate a number of locations in and around the head to orient and position cutting surfaces relative
  // to known points.
  // Two lateral cylinders trim the front of the sideburns and the bit behind the ears.
  #local MakeHuman_HLC1  = MakeHuman_joint_head + MakeHuman_Units*( MakeHuman_HeadPaVector*0.11 + MakeHuman_HeadFwVector*0.94); // Temple Centre
  #local MakeHuman_HLC2  = MakeHuman_joint_head + MakeHuman_Units*(-MakeHuman_HeadPaVector*0.63 + MakeHuman_HeadFwVector*0.066); // Neck Centre
  // Front Cone Locations
  #local MakeHuman_HLC3  = MakeHuman_joint_head + MakeHuman_Units* MakeHuman_HeadPaVector*0.38;                                // Centre
  #local MakeHuman_HLE3  = MakeHuman_joint_head + MakeHuman_Units*(MakeHuman_HeadPaVector*0.35 + MakeHuman_HeadFwVector*1.31);     // Extreme Centre
  #local MakeHuman_HLE3L = MakeHuman_HLE3 - MakeHuman_Units*MakeHuman_HeadLRVector*0.35;                                        // Extreme Left
  #local MakeHuman_HLE3R = MakeHuman_HLE3 + MakeHuman_Units*MakeHuman_HeadLRVector*0.28;                                       // Extreme Right
  // Rear Cone Locations
  #local MakeHuman_HLC4  = MakeHuman_joint_head - MakeHuman_HeadPaVector*0.625 + MakeHuman_HeadFwVector*0.025; // Centre
  #local MakeHuman_HLE4  = MakeHuman_joint_head - MakeHuman_HeadPaVector*0.2 - MakeHuman_HeadFwVector*0.8;     // Extreme Centre
  #local MakeHuman_HLE4L = MakeHuman_HLE4 - MakeHuman_HeadLRVector*0.9;                                        // Extreme Left
  #local MakeHuman_HLE4R = MakeHuman_HLE4 + MakeHuman_HeadLRVector*0.9;                                        // Extreme Right

  // Set to '1' to show a line of your choice.
  #if (1) cylinder {MakeHuman_HairCentre,MakeHuman_HairCentre-2*x,0.03  pigment {rgb <0,2,0>}} #end 
  #if (1) cylinder {MakeHuman_HairCentre,MakeHuman_HairCentre+MakeHuman_HairAxis*2,0.03  pigment {rgb <0,2,0>}} #end 
  
  // Return a CSG object comprising the hairline mesh, trimmed to shape.
  #declare MakeHuman_SelectedGroups = MakeHuman_Hairline;
  #declare MakeHuman_HairLineObject = difference {
    object {
      MakeHuman_Mesh(0)
      pigment {rgb <1,0,0>}
    }
    // Cut away everything below a certain level
    plane {MakeHuman_HeadPaVector,0 translate MakeHuman_joint_head-MakeHuman_HeadPaVector*0.25}
    // Overlap two cones to make a cusp above the brow
    cone {MakeHuman_HLC3,0.175*MakeHuman_Units,MakeHuman_HLE3L,0.37*MakeHuman_Units} // Left Brow                      
    cone {MakeHuman_HLC3,0.175*MakeHuman_Units,MakeHuman_HLE3R,0.37*MakeHuman_Units} // Right Brow 
    // Flatten off the cusp and clear away remnants around the nose                     
    cone {MakeHuman_HLC3,0.175*MakeHuman_Units,MakeHuman_HLE3-MakeHuman_HeadPaVector*0.3,0.52*MakeHuman_Units}                     
    // Cut lateral cylindrical curves in front of and behind the ears
    cylinder {-x*MakeHuman_Units,x*MakeHuman_Units,0.328*MakeHuman_Units translate MakeHuman_HLC1}                     // Temple
    cylinder {-x*MakeHuman_Units,x*MakeHuman_Units,0.44*MakeHuman_Units scale <1,1.5,1.075 > translate MakeHuman_HLC2} // Neck
    // Create a little cusp at the back of the neck
    cone {MakeHuman_HLC4,0.2*MakeHuman_Units,MakeHuman_HLE4L,0.45*MakeHuman_Units} // Left Nape                      
    cone {MakeHuman_HLC4,0.2*MakeHuman_Units,MakeHuman_HLE4R,0.45*MakeHuman_Units} // Right Nape                      
  }
  object {MakeHuman_HairLineObject}                    
#end

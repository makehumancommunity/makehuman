//
// Create a camera definition based on the MakeHuman camera settings when this 
// file was generated. We need to convert between the OpenGL vertical FOV and 
// the horizontal POV-Ray camera angle. We also need to account for the way 
// OpenGL reports its camera data, translating before rotating, which further 
// moves the camera. The x-axis is also reversed to the standard POV-Ray settings.
#declare MakeHuman_Camera = camera {
  perspective
  location <MakeHuman_EyeX, MakeHuman_EyeY, MakeHuman_EyeZ>
  look_at <MakeHuman_FocusX, MakeHuman_FocusY, MakeHuman_FocusZ>
  angle 30
}

// Create a standard light definition based on MakeHuman settings.
#declare MakeHuman_LightSource = light_source {
    <MakeHuman_LightX, MakeHuman_LightY, MakeHuman_LightZ>
    color rgb 1
    spotlight
    radius 1000
    falloff 1000
    tightness 1
    point_at < MakeHuman_TranslateX, MakeHuman_TranslateY, MakeHuman_TranslateZ>
}

// Assign default values.
// This texture uses the standard pigment map as a uv-mapped pigment and adds a
// little disruption to the surface normals.  
#ifndef (MakeHuman_Material)

  #declare DIFFUSE = pigment { 
        image_map { tiff "texture.tif"}
        }

#declare NORMAL = normal {
        wrinkles 0.23 scale 0.0002
        }
 
#declare FINISH = finish { 
        specular 0            // Max highlight intensity: 0 -> 1
        roughness 0.02203444  // surface roughness: 0.0005 -> 1
        phong 0 phong_size 0  // Phong specular disabled

        ambient 0.01 // rgb <0.00,0.00,0.00>
        diffuse 0.6
        reflection{0 } conserve_energy
        subsurface {translucency 0.6} //0.8}
        }

// material
#declare MakeHuman_Material = material {
        texture { uv_mapping
                pigment { DIFFUSE }
                normal  { NORMAL }
                finish  { FINISH }
        }
        
        interior{ior 1.33}
}
  
#end

// This texture attempts to simulate a simple X-Ray texture.  
#ifndef (MakeHuman_XRayTexture)
  #declare MakeHuman_XRayTexture = texture{
    pigment {
      slope {
      <-3,0,1>
      }
      color_map {
        [0.00 color rgbt <1,1,1,0> ]
        [0.10 color rgbt <1,1,1,0> ]
        [0.15 color rgbt <1,1,1,0.8> ]
        [0.65 color rgbt <1,1,1,1> ]
        [1.00 color rgbt <1,1,1,1> ]
      }
    }
    finish{ ambient 10 }
  }
#end


// This utility macro appends array elements from one array to the end of another.
// The MakeHuman_TargetCounter variable must be set to the next index to write into
// the target before this macro is called. 
// 
// This macro is used to assemble different groupings and is not likely to be of value to the
// average user. 
//
#macro MakeHuman_AppendGroup(MakeHuman_SourceArray, MakeHuman_TargetArray)
  #local MakeHuman_I = 0;
  #while (MakeHuman_I<dimension_size(MakeHuman_SourceArray,1))
    #local MakeHuman_TargetArray[MakeHuman_TargetCounter] = MakeHuman_SourceArray[MakeHuman_I]; 
    #declare MakeHuman_TargetCounter = MakeHuman_TargetCounter + 1; 
    #local MakeHuman_I = MakeHuman_I + 1; 
  #end
#end


// This utility macro checks whether a specific face is part of one of the face groups named 
// in the MakeHuman_SelectedGroups array. It returns a '1' if the face is in one of the listed
// face groups or '0' if the face is not found to be in one of the listed face groups. 
// If the MakeHuman_SelectedGroups array is not defined it returns '1' for any face.
// 
// This macro is not intended to be invoked directly by the casual user, but is automatically invoked
// by the other macros in this file as required. 
//
#macro MakeHuman_SelectFace(MakeHuman_ThisFace)
  #ifdef(MakeHuman_SelectedGroups)
    #local MakeHuman_FaceSelected = 0;      
    // Check whether this face is in one of the listed face groups. 
    // Try shortcutting the string comparisons by first comparing with the previous decision.
    #local MakeHuman_FaceGroupIndex = MakeHuman_FaceGroupIndexArray[MakeHuman_ThisFace]; 
    #local MakeHuman_FaceGroupName  = MakeHuman_FaceGroupArray[MakeHuman_FaceGroupIndex];
    #ifndef(MakeHuman_PreviousFaceGroupIndex) #declare MakeHuman_PreviousFaceGroupIndex = -1; #end
    #ifndef(MakeHuman_PreviousFaceSelected)   #declare MakeHuman_PreviousFaceSelected   = 0;  #end
    #if (MakeHuman_FaceGroupIndex=MakeHuman_PreviousFaceGroupIndex)
      #local MakeHuman_FaceSelected = MakeHuman_PreviousFaceSelected; 
    #else  
      #local MakeHuman_GroupIndex = 0;
      #while (MakeHuman_GroupIndex<dimension_size(MakeHuman_SelectedGroups,1) & !MakeHuman_FaceSelected)
        #if (strcmp(MakeHuman_FaceGroupName,MakeHuman_SelectedGroups[MakeHuman_GroupIndex])=0)
          #local MakeHuman_FaceSelected = 1;
        #end
        #local MakeHuman_GroupIndex = MakeHuman_GroupIndex + 1;
      #end 
    #end
    #declare MakeHuman_PreviousFaceGroupIndex = MakeHuman_FaceGroupIndex;
    #declare MakeHuman_PreviousFaceSelected   = MakeHuman_FaceSelected;
  #else 
    #local MakeHuman_FaceSelected = 1;
  #end 
  MakeHuman_FaceSelected              
#end


// This macro returns a union of cylinders, with one cylinder along each edge of each 
// face of the mesh described by the points in the MakeHuman_VertexArray array.
// Because most edges are shared by two faces you actually get 2 cylinders for 
// each edge of the equivalent mesh2 object.
// 
// A subset of faces can be used by setting the MakeHuman_SelectedGroups array to contain the
// names of the required face groups.
//  
// If a non-zero displacement is specified on the macro call, the vertex positions are displaced
// by the specified amount along the direction of the surface normals for the vertices. Note that 
// this is not the same as scaling the union which should be done in your scene file following
// generation. 
//
#macro  MakeHuman_Cylinders(MakeHuman_Displacement)
  #ifdef(MakeHuman_PreviousFaceGroupIndex) #undef MakeHuman_PreviousFaceGroupIndex #end
  #ifdef(MakeHuman_PreviousFaceSelected  ) #undef MakeHuman_PreviousFaceSelected   #end

  #local MakeHuman_CylinderCount = 0;
  #ifndef (MakeHuman_Cylinder_Radius) #declare MakeHuman_Cylinder_Radius = 0.005; #end   
  union {
    #local MakeHuman_I = 0;
    #while (MakeHuman_I<dimension_size(MakeHuman_FaceArray,1)) 
      #if (MakeHuman_SelectFace(MakeHuman_I)) 
        #local MakeHuman_Vertex1 = MakeHuman_VertexArray[MakeHuman_FaceArray[MakeHuman_I][0]]
          + MakeHuman_NormalArray[MakeHuman_FaceArray[MakeHuman_I][0]]*MakeHuman_Displacement;
        #local MakeHuman_Vertex2 = MakeHuman_VertexArray[MakeHuman_FaceArray[MakeHuman_I][1]]
          + MakeHuman_NormalArray[MakeHuman_FaceArray[MakeHuman_I][1]]*MakeHuman_Displacement;
        #local MakeHuman_Vertex3 = MakeHuman_VertexArray[MakeHuman_FaceArray[MakeHuman_I][2]]
          + MakeHuman_NormalArray[MakeHuman_FaceArray[MakeHuman_I][2]]*MakeHuman_Displacement;
        cylinder {MakeHuman_Vertex1,MakeHuman_Vertex2,MakeHuman_Cylinder_Radius}
        cylinder {MakeHuman_Vertex2,MakeHuman_Vertex3,MakeHuman_Cylinder_Radius}
        cylinder {MakeHuman_Vertex3,MakeHuman_Vertex1,MakeHuman_Cylinder_Radius} 
        #local MakeHuman_CylinderCount = MakeHuman_CylinderCount + 3;
      #end
      #local MakeHuman_I = MakeHuman_I + 1;
    #end     
  }
  #if (MakeHuman_CylinderCount)
    #debug concat("The MakeHuman_Cylinders macro generated ",str(MakeHuman_CylinderCount,3,0)," cylinders.\n")
  #else 
    #ifdef(MakeHuman_SelectedGroups)
      #warning  "The MakeHuman_Cylinders macro found no vertices that match the selection criteria.\nCheck your MakeHuman_SelectedGroups setting.\n"
    #else
      #warning  "The MakeHuman_Cylinders macro found no vertices.\n"
    #end
  #end
#end   


// This macro returns a union of spheres, with ideally one sphere at each vertex of the 
// mesh described by the points in the MakeHuman_VertexArray array.
//
// A subset of faces can be used by setting the MakeHuman_SelectedGroups array to contain the
// names of the required face groups, but in this case a more time consuming algorithm needs to
// be used that processes the mesh face by face and duplicate vertices are likely to be generated.
// 
// If a non-zero displacement is specified on the macro call, the vertex positions are displaced
// by the specified amount along the direction of the surface normals for the vertices. Note that 
// this is not the same as scaling the union which should be done in your scene file following
// generation. 
//
#macro MakeHuman_Spheres(MakeHuman_Displacement)
  #ifdef(MakeHuman_PreviousFaceGroupIndex) #undef MakeHuman_PreviousFaceGroupIndex #end
  #ifdef(MakeHuman_PreviousFaceSelected  ) #undef MakeHuman_PreviousFaceSelected   #end

  #ifndef (MakeHuman_Sphere_Radius)   #declare MakeHuman_Sphere_Radius   = 0.02;  #end   
  #local MakeHuman_SphereCount = 0;
  union {
    // If we need to check the Selected Groups list we need to process vertices face by face. 
    #ifdef(MakeHuman_SelectedGroups)
      #local MakeHuman_I = 0;
      #while (MakeHuman_I<dimension_size(MakeHuman_FaceArray,1))
        // If this face is in one of the face groups listed, add a sphere for each of its 3 vertices
        #if (MakeHuman_SelectFace(MakeHuman_I)) 
          #local MakeHuman_J = 0; 
          #while (MakeHuman_J<3)
            #local MakeHuman_Vertex = MakeHuman_VertexArray[MakeHuman_FaceArray[MakeHuman_I][MakeHuman_J]]
              + MakeHuman_NormalArray[MakeHuman_FaceArray[MakeHuman_I][MakeHuman_J]]*MakeHuman_Displacement;
            sphere {MakeHuman_Vertex, MakeHuman_Sphere_Radius}
            #local MakeHuman_SphereCount = MakeHuman_SphereCount + 1;
            #local MakeHuman_J = MakeHuman_J + 1;
          #end
        #end
        #local MakeHuman_I = MakeHuman_I + 1;
      #end
    // If we don't need to check the Selected Groups list we can simply process all vertices. 
    #else
      #local MakeHuman_I = 0;
      #while (MakeHuman_I<dimension_size(MakeHuman_VertexArray,1)) 
        sphere {
          MakeHuman_VertexArray[MakeHuman_I]+MakeHuman_NormalArray[MakeHuman_I]*MakeHuman_Displacement, 
          MakeHuman_Sphere_Radius
        }
        #local MakeHuman_SphereCount = MakeHuman_SphereCount + 1;
        #local MakeHuman_I = MakeHuman_I + 1;
      #end
    #end
  }
  #if (MakeHuman_SphereCount)
    #debug concat("The MakeHuman_Spheres macro generated ",str(MakeHuman_SphereCount,3,0)," spheres.\n")
  #else 
    #ifdef(MakeHuman_SelectedGroups)
      #warning  "The MakeHuman_Spheres macro found no vertices that match the selection criteria.\nCheck your MakeHuman_SelectedGroups setting.\n"
    #else
      #warning  "The MakeHuman_Spheres macro found no vertices.\n"
    #end
  #end
#end     

// This macro generates a POV-Ray mesh2 object from the coordinates, normals, faces and uv-data
// specified above. These arrays are generated by the MakeHuman POV-Ray export function. 
//
// A subset of faces can be used by setting the MakeHuman_SelectedGroups array to contain the
// names of the required face groups, which is a little slower than generating the full mesh2
// object because additional processing is required to work out which faces to include. 
// 
// If a non-zero displacement is specified on the macro call, the vertex positions are displaced
// by the specified amount along the direction of the surface normals for the vertices. Note that 
// this is not the same as scaling the object which should be done in your scene file following
// generation.
//
// The macro supports a displacement parameter that is normally 0, but can be a
// small positive or negative value (e.g. -0.001) to displace all of the vertices
// a short distance along the normals. A sub-surface mesh2 object generated in 
// this way can be used along with a conventional instance of the surface to 
// support sub-surface scattering (SSS).
//
#macro MakeHuman_Mesh(MakeHuman_Displacement)
  #ifdef(MakeHuman_PreviousFaceGroupIndex) #undef MakeHuman_PreviousFaceGroupIndex #end
  #ifdef(MakeHuman_PreviousFaceSelected  ) #undef MakeHuman_PreviousFaceSelected   #end

  // Work out which faces are required and which indices are used for those faces.
  #local MakeHuman_SelectedVertices = array [dimension_size(MakeHuman_VertexArray,1)];
  
  #ifdef(MakeHuman_SelectedGroups)
    #declare MakeHuman_SelectedGroupLocations = array [dimension_size(MakeHuman_SelectedGroups,1)];
    #local MakeHuman_FaceCount = 0;
    #local MakeHuman_SelectedFaceArray = array [dimension_size(MakeHuman_FaceArray,1)];
    #local MakeHuman_I = 0;
    #while (MakeHuman_I<dimension_size(MakeHuman_FaceArray,1))
      // If this face is in one of the face groups listed, take a copy of the face data 
      #if (MakeHuman_SelectFace(MakeHuman_I)) 
        #local MakeHuman_SelectedFaceArray[MakeHuman_FaceCount] = MakeHuman_I; 
        // Set a flag for each vertex used to construct this face
        #local MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][0]]=-1;
        #local MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][1]]=-1;
        #local MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][2]]=-1;
        #local MakeHuman_FaceCount = MakeHuman_FaceCount + 1;
      #end
      #local MakeHuman_I = MakeHuman_I + 1;
    #end
    // Loop through the vertices creating a lookup table of the new vertex indices
    // required to reference just the selected faces/vertices. 
    #local MakeHuman_SelectedVerticesCount = 0;
    #local MakeHuman_I = 0;
    #while (MakeHuman_I<dimension_size(MakeHuman_VertexArray,1))
      #ifdef(MakeHuman_SelectedVertices[MakeHuman_I]) 
        #local MakeHuman_SelectedVertices[MakeHuman_I] = MakeHuman_SelectedVerticesCount;
        #local MakeHuman_SelectedVerticesCount = MakeHuman_SelectedVerticesCount + 1;
      #end
      #local MakeHuman_I = MakeHuman_I + 1;
    #end
  #else
    #local MakeHuman_FaceCount             = dimension_size(MakeHuman_FaceArray  ,1);
    #local MakeHuman_SelectedVerticesCount = dimension_size(MakeHuman_VertexArray,1);
  #end 

  // Generate the mesh2 object
  mesh2 {
    vertex_vectors {
      MakeHuman_SelectedVerticesCount
      #local MakeHuman_I = 0;
      #while (MakeHuman_I<dimension_size(MakeHuman_VertexArray,1))
        #ifdef(MakeHuman_SelectedGroups)
          #ifdef(MakeHuman_SelectedVertices[MakeHuman_I]) 
            MakeHuman_VertexArray[MakeHuman_I]+MakeHuman_NormalArray[MakeHuman_I]*MakeHuman_Displacement,
          #end
        #else 
          MakeHuman_VertexArray[MakeHuman_I]+MakeHuman_NormalArray[MakeHuman_I]*MakeHuman_Displacement,
        #end
        #local MakeHuman_I = MakeHuman_I + 1; 
      #end     
    }
    normal_vectors {
      MakeHuman_SelectedVerticesCount
      #local MakeHuman_I = 0;
      #while (MakeHuman_I<dimension_size(MakeHuman_NormalArray,1))
        #ifdef(MakeHuman_SelectedGroups)
          #ifdef(MakeHuman_SelectedVertices[MakeHuman_I]) 
            MakeHuman_NormalArray[MakeHuman_I],
          #end 
        #else 
          MakeHuman_NormalArray[MakeHuman_I],
        #end
        #local MakeHuman_I = MakeHuman_I + 1;
      #end     
    }
    uv_vectors {
      dimension_size(MakeHuman_UVArray,1)
      #local MakeHuman_I = 0;
      #while (MakeHuman_I<dimension_size(MakeHuman_UVArray,1))
        MakeHuman_UVArray[MakeHuman_I],
        #local MakeHuman_I = MakeHuman_I + 1;
      #end     
    }
    face_indices {
      #ifdef(MakeHuman_SelectedGroups)
        MakeHuman_FaceCount
        #local MakeHuman_J = 0;
        #while (MakeHuman_J<MakeHuman_FaceCount)                        
          // Take the face index from the selected face array.
          #local MakeHuman_I = MakeHuman_SelectedFaceArray[MakeHuman_J];
          // Use the original vertex indices to look up the selected vertex indices. 
          < MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][0]],
            MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][1]],
            MakeHuman_SelectedVertices[MakeHuman_FaceArray[MakeHuman_I][2]]>
          
          
//          <MakeHuman_FaceArray[MakeHuman_I][0],MakeHuman_FaceArray[MakeHuman_I][1],MakeHuman_FaceArray[MakeHuman_I][2]>,
          #local MakeHuman_J = MakeHuman_J + 1;
        #end     
      #else 
        dimension_size(MakeHuman_FaceArray,1)
        #local MakeHuman_I = 0;
        #while (MakeHuman_I<dimension_size(MakeHuman_FaceArray,1))
          <MakeHuman_FaceArray[MakeHuman_I][0],MakeHuman_FaceArray[MakeHuman_I][1],MakeHuman_FaceArray[MakeHuman_I][2]>,
          #local MakeHuman_I = MakeHuman_I + 1;
        #end     
      #end
    }
    uv_indices  {
      #ifdef(MakeHuman_SelectedGroups)
        MakeHuman_FaceCount
        #local MakeHuman_J = 0;
        #while (MakeHuman_J<MakeHuman_FaceCount)
          #local MakeHuman_I = MakeHuman_SelectedFaceArray[MakeHuman_J];
          <MakeHuman_UVIndexArray[MakeHuman_I][0],MakeHuman_UVIndexArray[MakeHuman_I][1],MakeHuman_UVIndexArray[MakeHuman_I][2]>,
          #local MakeHuman_J = MakeHuman_J + 1;
        #end     
      #else 
        dimension_size(MakeHuman_UVIndexArray,1)
        #local MakeHuman_I = 0;
        #while (MakeHuman_I<dimension_size(MakeHuman_UVIndexArray,1))
          <MakeHuman_UVIndexArray[MakeHuman_I][0],MakeHuman_UVIndexArray[MakeHuman_I][1],MakeHuman_UVIndexArray[MakeHuman_I][2]>,
          #local MakeHuman_I = MakeHuman_I + 1;
        #end     
      #end
    }
    
    uv_mapping
  }
  #if (MakeHuman_FaceCount)
    #debug concat("The MakeHuman_Mesh macro generated ",str(MakeHuman_FaceCount,3,0)," faces.\n")
  #else 
    #ifdef(MakeHuman_SelectedGroups)
      #warning  "The MakeHuman_Mesh macro found no faces that match the selection criteria.\nCheck your MakeHuman_SelectedGroups setting.\n"
    #else
      #warning  "The MakeHuman_Mesh macro found no faces.\n"
    #end
  #end
#end



                                                                                 
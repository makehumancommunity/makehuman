// makehuman_groupings.inc
// -----------------------

// This include file provides face group groupings taht can be used
// in conjunction with the other include files generated from the
// MakeHuman application using the POV-Ray export functionality.
//
// This file is licensed under the terms of the CC-LGPL. 
// This license permits you to use, modify and redistribute the content.
// 

#declare MakeHuman_JointsArray = array[81] {
  "joint-head",
  "joint-l-ankle",
  "joint-l-clavicle",
  "joint-l-elbow",
  "joint-l-eye",
  "joint-l-finger-1-1",
  "joint-l-finger-1-2",
  "joint-l-finger-1-3",
  "joint-l-finger-2-1",
  "joint-l-finger-2-2",
  "joint-l-finger-2-3",
  "joint-l-finger-3-1",
  "joint-l-finger-3-2",
  "joint-l-finger-3-3",
  "joint-l-finger-4-1",
  "joint-l-finger-4-2",
  "joint-l-finger-4-3",
  "joint-l-finger-5-1",
  "joint-l-finger-5-2",
  "joint-l-finger-5-3",
  "joint-l-toe-1-1",    // Was "joint-l-foot-finger-1-1",
  "joint-l-toe-1-2",    // Was "joint-l-foot-finger-1-2",
  "joint-l-toe-2-1",    // Was "joint-l-foot-finger-2-1",
  "joint-l-toe-2-2",    // Was "joint-l-foot-finger-2-2",
  "joint-l-toe-2-3",    // Was "joint-l-foot-finger-2-3",
  "joint-l-toe-3-1",    // Was "joint-l-foot-finger-3-1",
  "joint-l-toe-3-2",    // Was "joint-l-foot-finger-3-2",
  "joint-l-toe-3-3",    // New
  "joint-l-toe-4-1",    // Was "joint-l-foot-finger-4-1",
  "joint-l-toe-4-2",    // Was "joint-l-foot-finger-4-2",
  "joint-l-toe-4-3",    // New
  "joint-l-toe-5-1",    // Was "joint-l-foot-finger-5-1",
  "joint-l-toe-5-2",    // Was "joint-l-foot-finger-5-2",
  "joint-l-toe-5-3",    // New
  "joint-l-hand",
  "joint-l-knee",
  "joint-l-shoulder",
  "joint-l-upper-leg",
  "joint-mouth",
  "joint-neck",
  "joint-pelvis",
  "joint-r-ankle",
  "joint-r-clavicle",
  "joint-r-elbow",
  "joint-r-eye",
  "joint-r-finger-1-1",
  "joint-r-finger-1-2",
  "joint-r-finger-1-3",
  "joint-r-finger-2-1",
  "joint-r-finger-2-2",
  "joint-r-finger-2-3",
  "joint-r-finger-3-1",
  "joint-r-finger-3-2",
  "joint-r-finger-3-3",
  "joint-r-finger-4-1",
  "joint-r-finger-4-2",
  "joint-r-finger-4-3",
  "joint-r-finger-5-1",
  "joint-r-finger-5-2",
  "joint-r-finger-5-3",
  "joint-r-toe-1-1",    // Was "joint-r-foot-finger-1-1", 
  "joint-r-toe-1-2",    // Was "joint-r-foot-finger-1-2", 
  "joint-r-toe-2-1",    // Was "joint-r-foot-finger-2-1", 
  "joint-r-toe-2-2",    // Was "joint-r-foot-finger-2-2", 
  "joint-r-toe-2-3",    // Was "joint-r-foot-finger-2-3", 
  "joint-r-toe-3-1",    // Was "joint-r-foot-finger-3-1", 
  "joint-r-toe-3-2",    // Was "joint-r-foot-finger-3-2", 
  "joint-r-toe-3-3",    // New 
  "joint-r-toe-4-1",    // Was "joint-r-foot-finger-4-1", 
  "joint-r-toe-4-2",    // Was "joint-r-foot-finger-4-2", 
  "joint-r-toe-4-3",    // New 
  "joint-r-toe-5-1",    // Was "joint-r-foot-finger-5-1", 
  "joint-r-toe-5-2",    // Was "joint-r-foot-finger-5-2", 
  "joint-r-toe-5-3",    // New 
  "joint-r-hand",
  "joint-r-knee",
  "joint-r-shoulder",
  "joint-r-upper-leg",
  "joint-spine-1",
  "joint-spine-2",
  "joint-spine-3",
}

#declare MakeHuman_LeftFingerGroup = array[15] {
  "l-hand-finger-1-1",
  "l-hand-finger-1-2",
  "l-hand-finger-1-3",
  "l-hand-finger-2-1",
  "l-hand-finger-2-2",
  "l-hand-finger-2-3",
  "l-hand-finger-3-1",
  "l-hand-finger-3-2",
  "l-hand-finger-3-3",
  "l-hand-finger-4-1",
  "l-hand-finger-4-2",
  "l-hand-finger-4-3",
  "l-hand-finger-5-1",
  "l-hand-finger-5-2",
  "l-hand-finger-5-3",
}

#declare MakeHuman_RightFingerGroup = array[15] {
  "r-hand-finger-1-1",
  "r-hand-finger-1-2",
  "r-hand-finger-1-3",
  "r-hand-finger-2-1",
  "r-hand-finger-2-2",
  "r-hand-finger-2-3",
  "r-hand-finger-3-1",
  "r-hand-finger-3-2",
  "r-hand-finger-3-3",
  "r-hand-finger-4-1",
  "r-hand-finger-4-2",
  "r-hand-finger-4-3",
  "r-hand-finger-5-1",
  "r-hand-finger-5-2",
  "r-hand-finger-5-3",
}

#declare MakeHuman_LeftToeGroup = array[14] {
  "l-foot-toe-1-1",      // Was "l-foot-finger-1-1",
  "l-foot-toe-1-2",      // Was "l-foot-finger-1-2",
                         // Was "l-foot-finger-1-3",
  "l-foot-toe-2-1",      // Was "l-foot-finger-2-1",
  "l-foot-toe-2-2",      // Was "l-foot-finger-2-2",
  "l-foot-toe-2-3",      // Was "l-foot-finger-2-3",
  "l-foot-toe-3-1",      // Was "l-foot-finger-3-1",
  "l-foot-toe-3-2",      // Was "l-foot-finger-3-2",
  "l-foot-toe-3-3",      // Was "l-foot-finger-3-3",
  "l-foot-toe-4-1",      // Was "l-foot-finger-4-1",
  "l-foot-toe-4-2",      // Was "l-foot-finger-4-2",
  "l-foot-toe-4-3",      // Was "l-foot-finger-4-3",
  "l-foot-toe-5-1",      // Was "l-foot-finger-5-1",
  "l-foot-toe-5-2",      // Was "l-foot-finger-5-2",
  "l-foot-toe-5-3",      // Was "l-foot-finger-5-3",
} 

#declare MakeHuman_RightToeGroup = array[14] {
  "r-foot-toe-1-1",    // Was "r-foot-finger-1-1",
  "r-foot-toe-1-2",    // Was "r-foot-finger-1-2",
                       // Was "r-foot-finger-1-3",
  "r-foot-toe-2-1",    // Was "r-finger-2-1",           
  "r-foot-toe-2-2",    // Was "r-foot-finger-2-2",
  "r-foot-toe-2-3",    // Was "r-foot-finger-2-3",
  "r-foot-toe-3-1",    // Was "r-foot-finger-3-1",
  "r-foot-toe-3-2",    // Was "r-foot-finger-3-2",
  "r-foot-toe-3-3",    // Was "r-foot-finger-3-3",
  "r-foot-toe-4-1",    // Was "r-foot-finger-4-1",
  "r-foot-toe-4-2",    // Was "r-foot-finger-4-2",
  "r-foot-toe-4-3",    // Was "r-foot-finger-4-3",
  "r-foot-toe-5-1",    // Was "r-foot-finger-5-1",
  "r-foot-toe-5-2",    // Was "r-foot-finger-5-2",
  "r-foot-toe-5-3",    // Was "r-foot-finger-5-3",
} 

#declare MakeHuman_LeftToeNailGroup = array[5] {
  "l-foot-nail1",
  "l-foot-nail2",
  "l-foot-nail3",
  "l-foot-nail4",
  "l-foot-nail5",
} 

#declare MakeHuman_RightToeNailGroup = array[5] {
  "r-foot-nail1",
  "r-foot-nail2",
  "r-foot-nail3",
  "r-foot-nail4",
  "r-foot-nail5",
} 

#declare MakeHuman_LeftFingerNailGroup = array[5] {
  "l-hand-nail1",
  "l-hand-nail2",
  "l-hand-nail3",
  "l-hand-nail4",
  "l-hand-nail5",
} 

#declare MakeHuman_RightFingerNailGroup = array[5] {
  "r-hand-nail1",
  "r-hand-nail2",
  "r-hand-nail3",
  "r-hand-nail4",
  "r-hand-nail5",
} 


#declare MakeHuman_LeftHandGroup = array [
    1
  + dimension_size(MakeHuman_LeftFingerGroup     ,1)
  + dimension_size(MakeHuman_LeftFingerNailGroup ,1)
];
#declare MakeHuman_LeftHandGroup[0] = "l-hand-palm";
#declare MakeHuman_TargetCounter = 1;
MakeHuman_AppendGroup(MakeHuman_LeftFingerGroup     ,MakeHuman_LeftHandGroup)
MakeHuman_AppendGroup(MakeHuman_LeftFingerNailGroup ,MakeHuman_LeftHandGroup)


#declare MakeHuman_RightHandGroup = array [
    1
  + dimension_size(MakeHuman_RightFingerGroup     ,1)
  + dimension_size(MakeHuman_RightFingerNailGroup ,1)
];
#declare MakeHuman_RightHandGroup[0] = "r-hand-palm";
#declare MakeHuman_TargetCounter = 1;
MakeHuman_AppendGroup(MakeHuman_RightFingerGroup     ,MakeHuman_RightHandGroup)
MakeHuman_AppendGroup(MakeHuman_RightFingerNailGroup ,MakeHuman_RightHandGroup)


#declare MakeHuman_LeftArmGroup = array [
    4
  + dimension_size(MakeHuman_LeftHandGroup     ,1)
];
#declare MakeHuman_LeftArmGroup[0] = "l-lowerarm";
#declare MakeHuman_LeftArmGroup[1] = "l-biceps";
#declare MakeHuman_LeftArmGroup[2] = "l-triceps";
#declare MakeHuman_LeftArmGroup[3] = "l-upper-shoulder";
#declare MakeHuman_TargetCounter = 4;
MakeHuman_AppendGroup(MakeHuman_LeftHandGroup     ,MakeHuman_LeftArmGroup)


#declare MakeHuman_RightArmGroup = array [
    4
  + dimension_size(MakeHuman_RightHandGroup     ,1)
];
#declare MakeHuman_RightArmGroup[0] = "r-lowerarm";
#declare MakeHuman_RightArmGroup[1] = "r-biceps";
#declare MakeHuman_RightArmGroup[2] = "r-triceps";
#declare MakeHuman_RightArmGroup[3] = "r-upper-shoulder";
#declare MakeHuman_TargetCounter = 4;
MakeHuman_AppendGroup(MakeHuman_RightHandGroup     ,MakeHuman_RightArmGroup)


#declare MakeHuman_LeftFootGroup = array [
    2
  + dimension_size(MakeHuman_LeftToeGroup     ,1)
  + dimension_size(MakeHuman_LeftToeNailGroup ,1)
];
#declare MakeHuman_LeftFootGroup[0] = "l-foot-heel";
#declare MakeHuman_LeftFootGroup[1] = "l-foot-core";      // Was "l-foot-centr" and  "l-foot";
#declare MakeHuman_TargetCounter = 2;
MakeHuman_AppendGroup(MakeHuman_LeftToeGroup     ,MakeHuman_LeftFootGroup)
MakeHuman_AppendGroup(MakeHuman_LeftToeNailGroup ,MakeHuman_LeftFootGroup)


#declare MakeHuman_LeftLegGroup = array [
    6
  + dimension_size(MakeHuman_LeftFootGroup     ,1)
];
#declare MakeHuman_LeftLegGroup[0] = "l-frontal-thigh";     // Was "l-frontal-thig";
#declare MakeHuman_LeftLegGroup[1] = "l-thigh-back";
#declare MakeHuman_LeftLegGroup[2] = "l-calf";
#declare MakeHuman_LeftLegGroup[3] = "l-knee";
#declare MakeHuman_LeftLegGroup[4] = "l-lower-leg";
#declare MakeHuman_LeftLegGroup[5] = "l-ankle";
#declare MakeHuman_TargetCounter = 6;
MakeHuman_AppendGroup(MakeHuman_LeftFootGroup     ,MakeHuman_LeftLegGroup)


#declare MakeHuman_RightFootGroup = array [
    2
  + dimension_size(MakeHuman_RightToeGroup     ,1)
  + dimension_size(MakeHuman_RightToeNailGroup ,1)
];
#declare MakeHuman_RightFootGroup[0] = "r-foot-heel";
#declare MakeHuman_RightFootGroup[1] = "r-foot-core";      // Was "r-foot-centr" and "r-foot";
#declare MakeHuman_TargetCounter = 2;
MakeHuman_AppendGroup(MakeHuman_RightToeGroup     ,MakeHuman_RightFootGroup)
MakeHuman_AppendGroup(MakeHuman_RightToeNailGroup ,MakeHuman_RightFootGroup)


#declare MakeHuman_RightLegGroup = array [
    6
  + dimension_size(MakeHuman_RightFootGroup     ,1)
];
#declare MakeHuman_RightLegGroup[0] = "r-frontal-thigh";     // Was "r-frontal-thig";
#declare MakeHuman_RightLegGroup[1] = "r-thigh-back";
#declare MakeHuman_RightLegGroup[2] = "r-calf";
#declare MakeHuman_RightLegGroup[3] = "r-knee";
#declare MakeHuman_RightLegGroup[4] = "r-lower-leg";
#declare MakeHuman_RightLegGroup[5] = "r-ankle";
#declare MakeHuman_TargetCounter = 6;
MakeHuman_AppendGroup(MakeHuman_RightFootGroup     ,MakeHuman_RightLegGroup)


#declare MakeHuman_NeckGroup = array[3] {
  "lower-neck",
  "upper-neck",
  "neck-adam-apple",
} 


#declare MakeHuman_BodyGroup = array[45] {
  "l-trapezius",
  "l-back-shoulder",
  "l-upper-shoulder",
  "l-front-shoulder",
  "l-clavicle",
  "l-upper-pectoralis",      // Was "l-upper-pecto", 
  "l-inner-pectoralis",      // Was "l-inner-pecto", 
  "l-middle-pectoralis",     // Was "l-middle-pecto",
  "l-outer-pectoralis",      // Was "l-outer-pecto", 
  "l-lower-pectoralis",      // Was "l-lower-pecto", 
  "l-nipple",                
  "l-axilla",                // Was "l-torso",
  "l-back-scapula",
  "l-ribs",
  "l-upper-abdomen",         // Was "l-upper-abdom", 
  "l-middle-abdomen",        // Was "l-middle-abdom",  
  "l-lower-abdomen",         // Was "l-lower-abdom",   
  "l-hip",                   
  "l-gluteus",
  "l-lower-back",            // New
  "l-upper-middle-back",     // New
  "r-trapezius",
  "r-back-shoulder",
  "r-upper-shoulder",
  "r-front-shoulder",
  "r-clavicle",
  "r-upper-pectoralis",      // Was "r-upper-pecto",  
  "r-inner-pectoralis",      // Was "r-inner-pecto",  
  "r-middle-pectoralis",     // Was "r-middle-pecto", 
  "r-outer-pectoralis",      // Was "r-outer-pecto",  
  "r-lower-pectoralis",      // Was "r-lower-pecto",  
  "r-nipple",
  "r-axilla",                // Was "r-torso",
  "r-back-scapula",
  "r-ribs",
  "r-upper-abdomen",                // Was  "r-upper-abdom",  
  "r-middle-abdomen",               // Was  "r-middle-abdom", 
  "r-lower-abdomen",                // Was  "r-lower-abdom",  
  "r-hip",
  "r-gluteus",
  "r-lower-back",                   // New
  "r-upper-middle-back",            // New
  "spine",                          // New
  "navel",
                                    // Was "lower-back",
                                    // Was "torso-back", 
  "genital-area",
} 

#declare MakeHuman_NoseGroup = array [7] {
  "nose-bridge",
  "nose-glabella",
  "nose-philtrum",
  "nose-tip",      // Was "nose-point",
  "nose-sellion"
  "l-nostril",
  "r-nostril",
}

#declare MakeHuman_LeftEyeGroup = array [14] {
  "l-eye-ball",
  "l-pupil",
  "l-upper-inner-lid",
  "l-upper-middle-lid",
  "l-upper-outer-lid",    
  "l-lower-inner-lid",
  "l-lower-middle-lid",
  "l-lower-outer-lid",
  "l-upper-inner-orbital",
  "l-upper-middle-orbital",
  "l-upper-outer-orbital", 
  "l-lower-inner-orbital",
  "l-lower-middle-orbital",
  "l-lower-outer-orbital",
} 

#declare MakeHuman_RightEyeGroup = array [14] {
  "r-eye-ball",
  "r-pupil",
  "r-upper-inner-lid",
  "r-upper-middle-lid",
  "r-upper-outer-lid",   
  "r-lower-inner-lid",
  "r-lower-middle-lid",
  "r-lower-outer-lid",
  "r-upper-inner-orbital",
  "r-upper-middle-orbital",
  "r-upper-outer-orbital", 
  "r-lower-inner-orbital",
  "r-lower-middle-orbital",
  "r-lower-outer-orbital",
}

#declare MakeHuman_EyeLashGroup = array [4] {
  "l-lower-lash",
  "r-lower-lash",
  "l-upper-lash",
  "r-upper-lash",
}

#declare MakeHuman_MouthGroup = array [10] {
  "l-upper-lip",
  "upper-middle-lip",
  "r-upper-lip",
  "l-lower-lip",
  "lower-middle-lip",
  "r-lower-lip",
  "l-lower-mouth",
  "r-lower-mouth",       
  "inner-mouth",
  "tongue",
}

#declare MakeHuman_LowerTeethGroup = array [16] {   
  "l-lower-central-incisor",
  "l-lower-lateral-incisor",
  "l-lower-cuspid",
  "l-lower-first-bicuspid",
  "l-lower-second-bicuspid",
  "l-lower-first-molar",
  "l-lower-second-molar",
  "l-lower-third-molar",
  "r-lower-central-incisor",
  "r-lower-lateral-incisor",
  "r-lower-cuspid",
  "r-lower-first-bicuspid",
  "r-lower-second-bicuspid",
  "r-lower-first-molar",
  "r-lower-second-molar",
  "r-lower-third-molar",
}

#declare MakeHuman_UpperTeethGroup = array [16] {  
  "l-upper-central-incisor",
  "l-upper-lateral-incisor",
  "l-upper-cuspid",
  "l-upper-first-bicuspid",
  "l-upper-second-bicuspid",
  "l-upper-first-molar",
  "l-upper-second-molar",
  "l-upper-third-molar",
  "r-upper-central-incisor", 
  "r-upper-lateral-incisor", 
  "r-upper-cuspid",          
  "r-upper-first-bicuspid",    // Was  "r-upper-first-biscupid",
  "r-upper-second-bicuspid", 
  "r-upper-first-molar",     
  "r-upper-second-molar",    
  "r-upper-third-molar",     
} 

#declare MakeHuman_LeftFaceGroup = array [11] {
  "l-temple",                // Was "l-temporal",
  "l-jaw",
  "l-outer-chin",           
  "l-cheek",
  "l-cheek-arc",
  "l-eyebrow",
  "l-inner-brow-ridge",
  "l-middle-brow-ridge",
  "l-outer-brow-ridge",      // Was "l-outer-brown-ridge",
  "l-zygoma",                // Was "l-zygom"
  "l-maxilla",
}

#declare MakeHuman_RightFaceGroup = array [11] {
  "r-temple",                // Was "r-temporal",
  "r-jaw",
  "r-outer-chin",          
  "r-cheek",
  "r-cheek-arc",
  "r-eyebrow",
  "r-inner-brow-ridge",
  "r-middle-brow-ridge",
  "r-outer-brow-ridge",
  "r-zygoma",                // Was "r-zygom"
  "r-maxilla",
}

#declare MakeHuman_ChinGroup = array [2] {
  "head-chin",
  "lower-chin",
}

#declare MakeHuman_ScalpGroup = array [3] {
  "head-back-skull",
  "head-brow",                // was "head-brown"
  "head-upper-skull",
}

#declare MakeHuman_EarGroup = array [8] {
  "l-ear-helix",
  "l-ear-inner",          
  "l-ear-lobe",
  "l-ear-tubercle",
  "r-ear-helix",
  "r-ear-inner",
  "r-ear-lobe",
  "r-ear-tubercle",
}

#declare MakeHuman_FaceGroup = array [
    dimension_size(MakeHuman_LeftFaceGroup  ,1)
  + dimension_size(MakeHuman_RightFaceGroup ,1)
  + dimension_size(MakeHuman_ChinGroup      ,1)
];
#declare MakeHuman_TargetCounter = 0;
MakeHuman_AppendGroup(MakeHuman_LeftFaceGroup  ,MakeHuman_FaceGroup)
MakeHuman_AppendGroup(MakeHuman_RightFaceGroup ,MakeHuman_FaceGroup)
MakeHuman_AppendGroup(MakeHuman_ChinGroup      ,MakeHuman_FaceGroup)


#declare MakeHuman_EyeGroup = array [
    dimension_size(MakeHuman_LeftEyeGroup  ,1)
  + dimension_size(MakeHuman_RightEyeGroup ,1)
];
#declare MakeHuman_TargetCounter = 0;
MakeHuman_AppendGroup(MakeHuman_LeftEyeGroup  ,MakeHuman_EyeGroup)
MakeHuman_AppendGroup(MakeHuman_RightEyeGroup ,MakeHuman_EyeGroup)
  


#declare MakeHuman_HeadGroup = array [
    dimension_size(MakeHuman_EarGroup    ,1)
  + dimension_size(MakeHuman_FaceGroup   ,1)
  + dimension_size(MakeHuman_NoseGroup   ,1)
  + dimension_size(MakeHuman_EyeGroup    ,1)
  + dimension_size(MakeHuman_MouthGroup  ,1)
  + dimension_size(MakeHuman_ScalpGroup  ,1)
];
#declare MakeHuman_TargetCounter = 0;
MakeHuman_AppendGroup(MakeHuman_EarGroup  ,MakeHuman_HeadGroup)
MakeHuman_AppendGroup(MakeHuman_FaceGroup ,MakeHuman_HeadGroup)
MakeHuman_AppendGroup(MakeHuman_NoseGroup ,MakeHuman_HeadGroup)
MakeHuman_AppendGroup(MakeHuman_EyeGroup  ,MakeHuman_HeadGroup)
MakeHuman_AppendGroup(MakeHuman_MouthGroup,MakeHuman_HeadGroup)
MakeHuman_AppendGroup(MakeHuman_ScalpGroup,MakeHuman_HeadGroup)
    


#declare MakeHuman_WholeAnatomyGroup = array [
    dimension_size(MakeHuman_HeadGroup     ,1)
  + dimension_size(MakeHuman_EyeLashGroup  ,1)
  + dimension_size(MakeHuman_LeftLegGroup  ,1)
  + dimension_size(MakeHuman_RightLegGroup ,1)
  + dimension_size(MakeHuman_LeftArmGroup  ,1)
  + dimension_size(MakeHuman_RightArmGroup ,1)
  + dimension_size(MakeHuman_BodyGroup     ,1)
  + dimension_size(MakeHuman_NeckGroup     ,1)
//  + dimension_size(MakeHuman_JointsArray  ,1)
];
#declare MakeHuman_TargetCounter = 0;
MakeHuman_AppendGroup(MakeHuman_HeadGroup     ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_EyeLashGroup  ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_LeftLegGroup  ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_RightLegGroup ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_LeftArmGroup  ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_RightArmGroup ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_BodyGroup     ,MakeHuman_WholeAnatomyGroup)
MakeHuman_AppendGroup(MakeHuman_NeckGroup     ,MakeHuman_WholeAnatomyGroup)
//MakeHuman_AppendGroup(MakeHuman_JointsArray  ,MakeHuman_WholeAnatomyGroup)   


#declare MakeHuman_Hairline = array [6] {
  "upper-neck",
  "head-back-skull",
  "head-brow",  
  "head-upper-skull",
  "l-temple",
  "r-temple",
}




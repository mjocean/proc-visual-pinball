proc-visual-pinball
===================
An updated/maintained version of register_vpcom for Visual Pinball emulation support for P-ROC-less and pinball-machine-less pyprocgame simulation and testing. 

-- MOcean


All credit goes to destruk, Gerry Stellenberg and Adam Premble 
 
Changes: 
-----
* Added another (overloaded) SetMech method with three args so fewer VP tables need to be editted before running
* Some hacks are in the code with very alpha support for Mechs in T2 (which are supported in the simulator files (t2.cpp) in PinMame);  Check setMech and getMech
* Separate initilization path that detects Cactus Canyon Continued so that CCC doesn't need a re-write and VP can emulate the current version

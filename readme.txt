1. The code can be initialized by runnining the file "AVL_analysis.py"

2. Once initialized, 
	-To analyze and modify the aircraft, double clik on "A320(aircraft)" in the product tree. 
	-To analyze and modify the AVL module, double click on "AVLroot" in the product tree.


3. Type of wing airfoil in "A320 (aircraft)" can be changed by changing the "TYPE_wing_airfoil" input slot.
	- "TYPE_wing_airfoil" = 1 represents supercritical airfoil
	- "TYPE_wing_airfoil" = 2 represents NACA-6 series
	- "TYPE_wing_airfoil" = 3 represents conventional type

4. Type of winglet in "A320 (aircraft)" can be changed by changing the "TYPE_winglet" input slot.
	- "TYPE_winglet" = 0 represents Canted winglet
	- "TYPE_winglet" = 1 represents Wingtip Fence
	- "TYPE_winglet" = 2 represents Raked Wingtip
	- "TYPE_winglet" = 3 represents Sharklet

	****NOTE: AVL analysis cannot be done for "TYPE_winglet" = 3" i.e. Sharklet because it is a blended surface.****

5. To perform the analysis of wing alone (i.e. no winglets attached) enter False in the input slot named winglet_ON, in the "A320(aircraft)" in the product tree.

6. Different geometry and trefftz plots can be analyzed in "AVLroot" by changing the geometry of the wing and the winglet in "A320(aircraft).

7. Dynamic pressure can be noted in the Attribute slot of the "AVLroot" 
	-It can be changed by changing the mach cruise number in "A320(aircraft) and for changing the altitude in "AVLroot".
	- Altitude can be changed by changing the altitude input slot.

8. Root bending moment (in Nm) can be noted in the Attribute slot of the "AVLroot"

9. Trefftz plots analyzes 2 cases:
	- case 1: fixed (angle of attact) AOA = 3 degree
	- case 2: fixed (coefficient of lift) cl = 0.5

10. Output files:
	- As the parameters are changed in the GUI, they are recorded in a .txt file named output in the same directory as the code. the parameters recorded 
	in the exact order are:
	wing airfoil type, winglet type, M_cruise, wing quarter chord sweep, altitude, dynamic pressure, root bending moment(fixed AoA), root bending moment (fixed Cl)
	- The user can choose to plot the change in root bending moment with 'sweep' or 'altitude' by setting the corresponding input(plot_which) and then clicking the plot_root_bending_moment.
	- From "A320(aircraft)" in the product tree, the user can write a .stp file to export geometry models to CAD systems.

temp1. To use EMWET, dat files of the airfoils used must be stored in the EMWET folder
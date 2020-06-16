from __future__ import division
from math import sqrt
from Geometry.wing import *
from Geometry.fuselage import *
from Function.help_fucntions import *


class VerticalTail(GeomBase):
    name = Input()  # Specifies name of the part
    vtp_root_airfoil = Input()  # Vertical tail root airfoil NACA input
    vtp_tip_airfoil = Input()  # Vertical tail tip airfoil NACA input
    vtp_aspect_ratio = Input()  # Vertical tail aspect ratio
    vtp_sweep = Input()  # Vertical tail sweep input
    vtp_area = Input()  # Vertical tail area
    htp_area = Input()  # Horizontal tail area calculated in the class HorizontalTail. Used here for calculations
    lh = Input()  # Horizontal tail, arm length calculated in class HorizontalTail. Used here for calculations
    Vh = Input()  # Horizontal tail volume coefficient. Calculated in class HorizontalTail. Used here for calculations
    MAC_chord_length = Input()  # Wing mach length
    starting_point_mac = Input()  # Starting position of the wing MAC line w.r.t (0,0,0)
    cabin_d = Input()  # Cabin diameter taken from class Fuselage
    wing_span = Input()  # Wing span taken from class Wing.

    # ******************* Fixed values *******************

    # This input value has been set to a fixed value because according to the reference material:
    # For a commercial jet transport, typical value for the tail volume
    # coefficient is around 0.083  for the vertical tail.
    @Attribute
    def Vv(self):
        return 0.083

    # For a typical jet transport, according to the reference material:
    # the taper ratio for must be 0.3 for a vertical tail with low set horizontal tail
    @Attribute
    def vtp_taper(self):
        return 0.3

    # Calculating the span of the vertical tail
    @Attribute
    def vtp_span(self):
        return sqrt(self.aspect_vtp * self.area_vtp)

    # Calculating the length of root chord of the vertical tail
    @Attribute
    def vtp_c_root(self):
        return (2. * self.vtp_span) / (self.aspect_vtp * (1 + self.vtp_taper))

    # Calculating the tip chord length of the vertical tail
    @Attribute
    def vtp_c_tip(self):
        return self.vtp_c_root * self.vtp_taper

    # Calculating the tail arm (lv)
    @Attribute
    def vtp_tailarm(self):
        return (self.Vv * self.htp_area * self.lh * self.wing_span) / (self.Vh * self.MAC_chord_length * self.area_vtp)

        #########################################################################################

    @Attribute
    def chords(self):
        return [self.vtp_c_root, self.vtp_c_tip]

    @Attribute
    def airfoils(self):
        return [self.vtp_root_airfoil, self.vtp_tip_airfoil]

    @Attribute(in_tree=True)
    def section_positions(self):
        vtp_root_pos = translate(self.position,
                                 'x', (self.starting_point_mac + 0.25 * self.MAC_chord_length + self.vtp_tailarm -
                                       (tan(radians(self.sweep_vtp)) * self.mac_y_pos_vtp) -
                                       (0.25 * self.MAC_length_vtp)))
        vtp_tip_pos = translate(self.position,
                                'x', (self.starting_point_mac + 0.25 * self.MAC_chord_length + self.vtp_tailarm -
                                      (tan(radians(self.sweep_vtp)) * self.mac_y_pos_vtp) - (
                                              0.25 * self.MAC_length_vtp)) +
                                (self.vtp_span * tan(radians(self.sweep_vtp))),
                                'y', self.vtp_span)
        return [vtp_root_pos, vtp_tip_pos]

    @Attribute
    def end_pos_vtp(self):
        vtp_root_pos = self.section_positions[0]
        return vtp_root_pos.x + self.chords[0]

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       position=self.section_positions[child.index],
                       chord=self.chords[child.index])

    @Part
    def solid(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True,
                           mesh_deflection=0.0001)

    # *********************************************************************************
    # Calculating MAC length and the aerodynamic center for the vertical tail
    # *********************************************************************************

    # Calculates the spanwise position of the MAC
    @Attribute
    def mac_y_pos_vtp(self):
        return (self.vtp_span / 3) * ((1 + (2 * self.vtp_taper)) / (1 + self.vtp_taper))

    # Calculated the MAC length
    @Attribute
    def MAC_length_vtp(self):
        return (2. / 3.) * self.vtp_c_root * (1. + self.vtp_taper + self.vtp_taper ** 2.) / (1 + self.vtp_taper)

    # Calculates the starting coordinate (position) of the MAC line for the vertical tail
    @Attribute
    def starting_pt_mac_vtp(self):
        x_start_mac_vtp = (self.starting_point_mac + (0.25 * self.MAC_chord_length)) + self.vtp_tailarm - (
                0.25 * self.MAC_length_vtp)
        return x_start_mac_vtp

    # Creates the line representing the MAC of the vertical tail
    @Part
    def mac_line_vtp(self):
        return LineSegment(Point(self.starting_pt_mac_vtp, 1, (0.48 * self.cabin_d + (self.mac_y_pos_vtp))),
                           Point((self.starting_pt_mac_vtp + self.MAC_length_vtp), 1,
                                 (0.5 * self.cabin_d + (self.mac_y_pos_vtp))),
                           line_thickness=5,
                           color="orange")

    # States the  aerodynamic center of the vertical tail
    @Attribute
    def ac_pt_vtp(self):
        x = (self.starting_pt_mac_vtp + (0.25 * self.MAC_length_vtp))
        y = 1
        z = (self.mac_y_pos_vtp + (0.5 * self.cabin_d))
        return Point(x, y, z)

    # Marks the aerodynamic center of the vertical tail
    @Part
    def vtp_ac(self):
        return Sphere(radius=0.2,
                      position=Position(self.ac_pt_vtp),
                      color="green")

    # ***************************************** Warnings************************************************
    popup_gui = Input(True)

    @Attribute
    def sweep_vtp(self):
        if self.vtp_sweep < 35 or self.vtp_sweep > 40:
            msg = "The vertical tail sweep should be between 35 and 40 degrees"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: vtp_sweep value changed", msg)
            return 35
        else:
            return self.vtp_sweep

    @Attribute
    def aspect_vtp(self):
        if self.vtp_aspect_ratio < 1.7 or self.vtp_aspect_ratio > 1.95:
            msg = "Aspect ratio of vertical tail must be between 1.7 and 1.95"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: Vtp_aspect_ratio value changed", msg)
            return 1.82
        else:
            return self.vtp_aspect_ratio

    @Attribute
    def area_vtp(self):
        if self.vtp_area < 21.5 or self.vtp_area > 26.5:
            msg = "Vertical tail area must be in the range 21.5 and 26.5"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: vtp_area value changed", msg)
            return 21.5
        else:
            return self.vtp_area


def generate_warning(warning_header, msg):
    from tkinter import Tk, messagebox

    # initialization
    window = Tk()
    window.withdraw()

    # generates the message box
    messagebox.showwarning(warning_header, msg)

    # kills the GUI
    window.deiconify()
    window.destroy()
    window.quit()


''' 
if__name__ == '__main__':
    from parapy.gui import display
    obj = VerticalTail(name="verticaltail",
                       vtp_root_airfoil="NACA0012",
                       vtp_tip_airfoil="NACA0012",
                       vtp_aspect_ratio=1.82,
                       vtp_sweep=35,
                       vtp_taper=0.303,
                       vtp_area=21.5,
                       Vv=0.083)
    display(obj)'''

import kbeutils.avl as avl
from math import *
from parapy.geom import *
from parapy.core import *
from Function.help_fucntions import *
from Geometry.section import Section
import warnings


# This class generates a wing shaped profile

class Wing(GeomBase):
    name = Input("Wing")  # name of the part generated
    # supercritical: 1, NACA-6: 2, Conventional: 3.
    TYPE_airfoil = Input()  # This lets the user switch between the type of airfoil thus changing the mach technology factor
    airfoil_root = Input()  # Wing root airfoil NACA input
    airfoil_kink = Input()  # # Wing kink airfoil NACA input
    airfoil_tip = Input()  # Wing tip airfoil NACA input
    wing_span = Input()  # Wing span as input
    M_cruise = Input()  # cruise mach number
    wing_c_root = Input()  # length of the wing root chord as input
    incidence = Input()  # wing incidence angle
    twist = Input()  # wing twist
    wing_taper_ratio_inboard = Input()  # inboard wing taper ratio
    cabin_l = Input()  # cabin length adapted from Fuselage class

    @Attribute
    # Drag divergence Mach number
    def M_dd(self):
        return self.cruise_mach + 0.03

    @Input
    # technology factor
    def M_tech_factor(self):
        if self.TYPE_airfoil == 1:
            return 0.935
        elif self.TYPE_airfoil == 2:
            return 0.87
        else:
            return 1

    @Attribute(settable=True)
    # quarter chord wing sweep
    def wing_sweep_025c(self):
        if (0.75 * self.M_tech_factor / self.M_dd) < 1:
            return degrees(acos(0.75 * self.M_tech_factor / self.M_dd))
        else:
            return 0

    @Attribute
    # taper ratio of the whole wing, i.e considering just the root and tip chord
    def full_wing_taper_ratio(self):
        return 0.156 * (2 - (self.wing_sweep_025c * pi / 180))

    # ACCORDING TO THE REFERENCE MATERIAL:
    # Default: 3 degrees for unswept wings at mid-wing location.
    # For every 10 degrees of quarter-chord sweep angle, reduce dihedral angle by 1 degree*
    # For low-wing aircraft: add 2 degrees
    @Attribute
    def wing_dihedral(self):
        reduction_dihedral = (self.wing_sweep_025c - (self.wing_sweep_025c % 10.)) / 10.
        return 5. - reduction_dihedral

    @Attribute
    # spanwise position of the kink is 40% of the wing semi-span
    def kink_span(self):
        return 0.4 * self.span_wing / 2

    # area of the inboard wing
    @Attribute
    def wing_area_inboard(self):
        return 0.5 * (self.chord_wingroot + self.wing_c_kink) * 2 * self.kink_span

    # area of the outboard wing
    @Attribute
    def wing_area_outboard(self):
        return 0.5 * (self.wing_c_kink + self.wing_c_tip) * (self.span_wing - (2 * self.kink_span))

    # addition of the inboard and outboard wing gives the total wing area
    @Attribute
    def wing_area_total(self):
        return self.wing_area_outboard + self.wing_area_inboard

    # calculates the wing aspect ratio
    @Attribute
    def wing_aspect_ratio(self):
        return (2 * self.span_wing) / \
               (self.chord_wingroot * (((1 - self.full_wing_taper_ratio) * (2 * self.kink_span / self.span_wing)) +
                                       (self.inboard_taper + self.full_wing_taper_ratio)))

    # calculates the length of the wing tip chord
    @Attribute
    def wing_c_tip(self):
        return self.full_wing_taper_ratio * self.chord_wingroot

    # calculates the length of the kink
    @Attribute
    def wing_c_kink(self):
        return self.chord_wingroot * self.inboard_taper

    # calculates the taper ratio of the outboard wing i.e considering just the kink and tip chord
    @Attribute
    def wing_taper_ratio_outboard(self):
        return self.wing_c_tip / self.wing_c_kink

    ##------------------------------------------##
    # Calculating chord length of the MAC of the wing
    ##------------------------------------------##

    # calculates the MAC of the inboard wing
    @Attribute
    def mac_in(self):
        return (2 * self.chord_wingroot / 3) * \
               ((1 + self.inboard_taper + self.inboard_taper ** 2) /
                (1 + self.inboard_taper))

    # calculates the MAC of the outboard wing
    @Attribute
    def mac_out(self):
        return (2 * self.wing_c_kink / 3) * (
                (1 + self.wing_taper_ratio_outboard + self.wing_taper_ratio_outboard ** 2) / (
                1 + self.wing_taper_ratio_outboard))

    # calculates the MAC of the whole wing by averaging
    @Attribute
    def MAC_chord_length(self):
        return (self.mac_in * self.wing_area_inboard + self.mac_out * self.wing_area_outboard) / self.wing_area_total

    ##--------------------------------------------------##
    # Calculating spanwise position of the MAC of the wing
    ##--------------------------------------------------##

    @Attribute
    # spanwise MAC position of the inboard wing.
    def y_mac_in(self):
        return (self.span_wing / 15) * (
                (self.chord_wingroot + (2 * self.wing_c_kink)) / (self.chord_wingroot + self.wing_c_kink))

    @Attribute
    # calcualte the spanwise position of the MAC of the outboard wing.
    def y_mac_out(self):
        return ((self.span_wing / 13500) *
                ((1330 * self.wing_c_tip - 117 * self.wing_c_kink) / (
                        self.wing_c_kink + self.wing_c_tip))) + self.kink_span

    # calculates the spanwise position of the MAc of the whole wing by averaging
    @Attribute
    def y_mac(self):
        return (self.y_mac_in * self.wing_area_inboard + self.y_mac_out * self.wing_area_outboard) / (
            self.wing_area_total)

    ##------------------------------------##
    # Positioning of the MAC
    ##-----------------------------------##

    # calculates the starting point of the MAC of the wing
    @Attribute
    def starting_point_mac(self):
        x_start_mac = (self.y_mac * tan(radians(self.wing_sweep_025c)) -
                       (0.25 * self.MAC_chord_length) + 0.25 * self.chord_wingroot)  # + (0.48 * self.cabin_l)
        return x_start_mac

    @Part
    # Draw the MAC line on the wing
    def mac_line(self):
        return LineSegment(Point(self.starting_point_mac, self.y_mac, 0),
                           Point((self.starting_point_mac + self.MAC_chord_length), self.y_mac, 0),
                           line_thickness=5,
                           color="red")

    # gives the coordinates of the aerodynamic center of the wing
    @Attribute
    def ac_pnt_wing(self):
        x1 = (self.starting_point_mac + (0.25 * self.MAC_chord_length))
        y1 = self.y_mac
        z1 = (self.y_mac * (tan(radians(self.wing_dihedral))))
        return Point(x1, y1, z1)

    # marks the aerodynamic center
    @Part
    def wing_ac(self):
        return Sphere(radius=0.2,
                      position=Position(self.ac_pnt_wing),
                      color="green")

    @Attribute
    def chords(self):
        return [self.chord_wingroot, self.wing_c_kink, self.wing_c_tip]

    @Attribute
    def airfoils(self):
        return [self.airfoil_root, self.airfoil_kink, self.airfoil_tip]

    # gives the longitudinal placement of the kink chord
    @Attribute
    def kink_x_pos(self):
        return (0.25 * self.chord_wingroot) + (
                (tan(radians(self.wing_sweep_025c))) * self.kink_span) - 0.25 * self.wing_c_kink

    # gives the longitudinal placement of the tip chord
    @Attribute
    def tip_x_pos(self):
        return (0.25 * self.chord_wingroot) + \
               ((tan(radians(self.wing_sweep_025c))) * (self.span_wing / 2)) - 0.25 * self.wing_c_tip

    @Attribute(in_tree=True)
    def section_positions(self):
        root_pos = self.position.rotate('y', radians(self.wing_incidence))
        kink_pos = rotate(self.position.translate('x', self.kink_x_pos,
                                                  'y', self.kink_span,
                                                  'z', (self.kink_span * tan(radians(self.wing_dihedral)))),
                          'y', ((self.wing_twist * self.kink_span) / (self.span_wing / 2)) + self.wing_incidence,
                          deg=True)
        tip_pos = rotate(self.position.translate('x', self.tip_x_pos,
                                                 'y', self.span_wing / 2,
                                                 'z', (self.span_wing / 2 * tan(radians(self.wing_dihedral)))),
                         'y', self.wing_twist + self.wing_incidence, deg=True)
        return [root_pos, kink_pos, tip_pos]

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       position=self.section_positions[child.index],
                       chord=self.chords[child.index])

    @Part
    def solid(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True)

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.position.point[1],
                           sections=[section.avl_section
                                     for section in self.sections])

#************************************Warnings************************************

    popup_gui = Input(True)

    @Attribute
    def cruise_mach(self):
        if self.M_cruise < 0.68 or self.M_cruise > 0.92:
            msg = "Invalid mach number. Accepted values between 0.68 - 0.92"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: M_cruise Value changed", msg)
            return 0.756
        else:
            return self.M_cruise

    @Attribute
    def wing_twist(self):
        if self.twist < -5 or self.twist > 0:
            msg = "Invalid wing twist value. it must range from -5 to 0"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: twist value of wing is changed", msg)
            return -5
        else:
            return self.twist

    @Attribute
    def wing_incidence(self):
        if self.incidence < 0 or self.incidence > 5:
            msg = "Invalid wing incidence. it must range from 0 to 5"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: incidence value of wing is changed", msg)
            return 3
        else:
            return self.incidence

    @Attribute
    def span_wing(self):
        if self.wing_span < 32 or self.wing_span > 34.5:
            msg = "invalid wing span. It must range from 32 - 34.5"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: wing_span value changed", msg)
            return 34
        else:
            return self.wing_span

    @Attribute
    def inboard_taper(self):
        if self.wing_taper_ratio_inboard < 0.38 or self.wing_taper_ratio_inboard > 0.48:
            msg = "invalid inboard wing taper ratio. Must be between 0.38 - 0.48"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: wing_taper_ratio_inboard value changed", msg)
            return 0.48
        else:
            return self.wing_taper_ratio_inboard

    @Attribute
    def chord_wingroot(self):
        if self.wing_c_root < 6.3 or self.wing_c_root > 7.5:
            msg = "invalid wing root chord length. Must be between 6.3 - 7.5"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: wing_c_root value changed", msg)
            return 7
        else:
            return self.wing_c_root


'''if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing(name="wing",
               TYPE_airfoil=3,
               airfoil_root="NACA2410",
               airfoil_kink="NACA2410",
               airfoil_tip="NACA0006",
               wing_span=34.10,
               M_cruise=0.756,
               wing_c_root=7,
               incidence=3,
               twist=-5,
               wing_taper_ratio_inboard=0.48)
    display(obj)'''

from math import radians, tan
from parapy.core import *
from parapy.geom import *
from Function.help_fucntions import *
from Geometry.section import Section


class HorizontalTail(GeomBase):
    name = Input("horizontal_tail")
    htp_root_airfoil = Input("Boeing29root")  # Airfoil input for the root chord of the horizontal tail
    htp_tip_airfoil = Input("lockheedtip")  # Airfoil input for the tip chord of the horizontal tail
    htp_area = Input(31)  # Area input for the horizontal tail
    htp_taper = Input(0.256)  # Taper ratio input for the horizontal tail
    htp_dihedral = Input()  # Dihedral angle input for the horizontal tail
    wing_area = Input()  # Total wing area of the wing
    starting_point_mac = Input()  # starting position of the wing M.A.C
    wing_sweep_025c = Input()  # Quarter chord wing sweep
    MAC_chord_length = Input()  # The mean aerodynamic chord length of the wing

    # ******************* Fixed value *******************
    @Attribute
    # Horizontal tail volume coefficient
    def Vh(self):
        return 1

    # horizontal tail aspect ratio
    @Attribute
    def htp_aspect(self):
        return 5

    # horizontal tail span
    @Attribute
    def htp_span(self):
        return (self.ht_area * self.htp_aspect) ** 0.5

    # horizontal tail sweep
    @Attribute
    def htp_sweep(self):
        return self.wing_sweep_025c + 10.

    # Horizontal tail arm coefficient
    @Attribute
    def lh(self):
        return (self.Vh * self.wing_area * self.MAC_chord_length) / self.ht_area

    # horizontal root chord length
    @Attribute
    def htp_c_root(self):
        return (2 * self.htp_span) / (self.htp_aspect * (1 + self.h_taper_ratio))

    # horizontal tip chord length
    @Attribute
    def htp_c_tip(self):
        return self.htp_c_root * self.h_taper_ratio

    @Attribute
    def chords(self):
        return [self.htp_c_root, self.htp_c_tip]

    @Attribute
    def airfoils(self):
        return [self.htp_root_airfoil, self.htp_tip_airfoil]

    @Attribute(in_tree=True)
    def section_positions(self):
        htp_root_pos = translate(self.position, 'x',
                                 (self.starting_point_mac_htp - ((tan(radians(self.htp_sweep))) * self.htp_mac_y_pos)))
        htp_tip_pos = translate(self.position,
                                'x', ((self.starting_point_mac_htp -
                                       ((tan(radians(self.htp_sweep))) * self.htp_mac_y_pos)) +
                                      (tan(radians(self.htp_sweep)) * self.htp_span / 2)),
                                'y', self.htp_span / 2,
                                'z', (self.htp_span * tan(radians(self.dihedral_htp))))
        return [htp_root_pos, htp_tip_pos]

    # The end position of the htp
    @Attribute
    def end_pos_htp(self):
        htp_root_pos = self.section_positions[0]
        return htp_root_pos.x + self.chords[0]

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

    #########################################################################################
    # Calculating the MAC of the HTP
    #########################################################################################

    # calculates the length of the MAC of horizontal tail
    @Attribute
    def htp_mac(self):
        return (2 * self.htp_c_root / 3) * (
                    (1 + self.h_taper_ratio + self.h_taper_ratio ** 2) / (1 + self.h_taper_ratio))

    # calculates the spanwise position of the MAC of horizontal tail
    @Attribute
    def htp_mac_y_pos(self):
        return (self.htp_span / 6) * ((1 + (2 * self.h_taper_ratio)) / (1 + self.h_taper_ratio))

    # returns the starting point of the MAC
    @Attribute
    def starting_point_mac_htp(self):
        x_start_mac_htp = self.starting_point_mac + (self.MAC_chord_length * 0.25) + self.lh - (0.25 * self.htp_mac)
        return x_start_mac_htp

    @Part
    # Draw the MAC line on the HT
    def mac_line_htp(self):
        return LineSegment(Point(self.starting_point_mac_htp, self.htp_mac_y_pos, 2.5),
                           Point(self.starting_point_mac_htp + self.htp_mac, self.htp_mac_y_pos, 2.5),
                           line_thickness=5,
                           color="red")

    # states the coordinates of the aerodynamic center of the horizontal tail
    @Attribute
    def ac_pnt_htp(self):
        x = self.starting_point_mac_htp + (0.25 * self.htp_mac)
        y = self.htp_mac_y_pos
        z = 2.5
        return Point(x, y, z)

    # Marks the aerodynamic center
    @Part
    def htp_ac(self):
        return Sphere(radius=0.2,
                      position=Position(self.ac_pnt_htp),
                      color="green")

    # ******************** Warnings *********************
    popup_gui = Input(True)

    @Attribute
    def h_taper_ratio(self):
        if self.htp_taper < 0.24 or self.htp_taper > 0.4:
            msg = "The horizontal tail taper ratio value must be between 0.24 - 0.4"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: htp_taper value changed", msg)
            return 0.256
        else:
            return self.htp_taper

    @Attribute
    def ht_area(self):
        if self.htp_area < 30 or self.htp_area > 37:
            msg = "Area of horizontal tail if greater than 37 has a small tail arm moment and if less than 30 has " \
                  "insufficient fuselage length "
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: htp_area value changed", msg)
            return 31
        else:
            return self.htp_area

    @Attribute
    def dihedral_htp(self):
        if self.htp_dihedral < 0 or self.htp_dihedral > 7:
            msg = "Invalid dihedral value. Input should be between 0 - 7"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: htp_dihedral value changed", msg)
            return 5
        else:
            return self.htp_dihedral


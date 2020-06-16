# To Do List (Delete one after finishing it)
# TODO: Make the HT and VT more object-oriented
# TODO: Evaluate the effect of the winglet in terms of fuel required for a certain mission
# TODO: Fix the output 3D model
# TODO: Output pdf
# TODO: EMWET


import os
from Geometry.ref_frame import Frame
from Geometry.fuselage import Fuselage
from Geometry.wing import Wing
from Geometry.HT import HorizontalTail
from Geometry.VT import VerticalTail
from Function.readGeometry import ReadGeometry
from Geometry.winglet import *
from parapy.exchange.step import STEPWriter
from Function.avl_analysis import Analysis
from Function.PDFwriter import PDFwriter
from EMWET.EMWET_analysis import Emwet


DIR = os.path.dirname(__file__)


class Aircraft(GeomBase):
    input = ReadGeometry("A320")

    winglet_ON = Input(True)
    TYPE_wing_airfoil = Input(1)
    TYPE_winglet = Input(0)
    limit_span_increase = Input(4)
    M_cruise = Input(input.M_cruise)  # cruise mach number

    # -------- FUSELAGE -----------#
    ln_d = Input(1.22)  # nose slenderness ratio
    lt_d = Input(2.724)  # tail slenderness ratio
    cabin_d = Input(4.14)

    # --------- WING --------------#
    name = Input("wing")
    airfoil_root = Input(input.w_af_root)
    airfoil_kink = Input(input.w_af_kink)
    airfoil_tip = Input(input.w_af_tip)
    wing_span = Input(input.wing_span)
    incidence = Input(input.incidence)
    twist = Input(input.twist)
    wing_c_root = Input(input.wing_c_root)
    wing_taper_ratio_inboard = Input(input.wing_taper_ratio_inboard)

    # ---------- Horizontal Tail -------------#
    htp_root_airfoil = Input("Boeing29root")
    htp_tip_airfoil = Input("lockheedtip")
    htp_area = Input(31)
    htp_taper = Input(0.3)
    htp_dihedral = Input(5)

    # ----------- VERTICAL TAIL ---------------#
    vtp_root_airfoil = Input("NACA0012")
    vtp_tip_airfoil = Input("NACA0012")
    vtp_aspect_ratio = Input(1.82)
    vtp_sweep = Input(35)
    vtp_area = Input(21.5)

    # -------------- Winglet -------------------#
    # --------TYPE 0 Canted Winglet-------------
    ct_name = "Canted Winglet"
    ct_airfoil_root = Input(input.ct_airfoil_root)
    ct_airfoil_tip = Input(input.ct_airfoil_tip)

    ct_chord_root_ratio = Input(input.ct_chord_root_ratio)
    ct_taper_ratio = Input(input.ct_taper_ratio)
    ct_height_ratio = Input(input.ct_height_ratio)
    ct_sweep = Input(input.ct_sweep)
    ct_cant = Input(input.ct_cant, validator=Range(0, 90))
    ct_twist_tip = Input(input.ct_twist_tip)
    ct_toe = Input(input.ct_toe)

    # --------TYPE 1 Wingtip Fence-------------
    wtf_name = Input("Wingtip Fence")
    wtf_airfoil_up = Input(input.wtf_airfoil_up)
    wtf_airfoil_root = Input(input.wtf_airfoil_root)
    wtf_airfoil_down = Input(input.wtf_airfoil_down)
    wtf_chord_root_ratio = Input(input.wtf_chord_root_ratio)
    wtf_taper_ratio_up = Input(input.wtf_taper_ratio_up)
    wtf_taper_ratio_down = Input(input.wtf_taper_ratio_down)
    wtf_height_up_ratio = Input(input.wtf_height_up_ratio)
    wtf_height_down_ratio = Input(input.wtf_height_down_ratio)
    wtf_sweep_up = Input(input.wtf_sweep_up)
    wtf_sweep_down = Input(input.wtf_sweep_down)
    wtf_twist_up = Input(input.wtf_twist_up)
    wtf_twist_down = Input(input.wtf_twist_down)

    # --------TYPE 2 Raked Wingtip-------------
    rkt_name = Input("Raked Wingtip")
    rkt_airfoil_start = Input(input.rkt_airfoil_start)
    rkt_airfoil_tip = Input(input.rkt_airfoil_tip)
    rkt_chord_start = Input(input.rkt_chord_start)
    rkt_taper_ratio = Input(input.rkt_taper_ratio)
    rkt_span_ratio = Input(input.rkt_span_ratio)
    rkt_sweep_le = Input(input.rkt_sweep_le)

    # --------TYPE 3 Sharklet-------------------
    skt_airfoil_start = Input(input.skt_airfoil_start)
    skt_airfoil_mid = Input(input.skt_airfoil_mid)
    skt_airfoil_tip = Input(input.skt_airfoil_tip)

    skt_chord_mid2start_ratio = Input(input.skt_chord_mid2start_ratio)
    skt_K_lambda = Input(input.skt_K_lambda)
    skt_height_ratio = Input(input.skt_height_ratio)
    skt_KR = Input(input.skt_KR)
    skt_cant = Input(input.skt_cant)
    skt_sweep_le = Input(input.skt_sweep_le)
    skt_sweep_transition_te = Input(input.skt_sweep_transition_te)
    skt_twist = Input(input.skt_twist)
    skt_nu_blended_sections = Input(input.skt_nu_blended_sections)

    @Part
    def aircraft_frame(self):
        return Frame(pos=self.position)  # this helps visualizing the wing local reference frame

    @Part
    def htp_right_wing(self):
        return HorizontalTail(htp_root_airfoil=self.htp_root_airfoil,
                              htp_tip_airfoil=self.htp_tip_airfoil,
                              htp_area=self.htp_area,
                              htp_taper=self.htp_taper,
                              htp_dihedral=self.htp_dihedral,
                              wing_area=self.right_wing.wing_area_total,
                              starting_point_mac=self.right_wing.starting_point_mac,
                              wing_sweep_025c=self.right_wing.wing_sweep_025c,
                              MAC_chord_length=self.right_wing.MAC_chord_length,
                              position=self.position.translate('z', 0.3 * self.cabin_d))

    @Part
    def htp_left_wing(self):
        return MirroredShape(shape_in=self.htp_right_wing.solid,
                             reference_point=self.htp_right_wing.position,
                             transparency=0.4,
                             vector1=self.htp_right_wing.position.Vz,
                             vector2=self.htp_right_wing.position.Vx)

    @Part
    def right_wing(self):
        return Wing(name=self.name,
                    TYPE_airfoil=self.TYPE_wing_airfoil,
                    airfoil_root=self.airfoil_root,
                    airfoil_kink=self.airfoil_kink,
                    airfoil_tip=self.airfoil_tip,
                    wing_span=self.wing_span,
                    M_cruise=self.M_cruise,
                    incidence=self.incidence,
                    twist=self.twist,
                    wing_c_root=self.wing_c_root,
                    wing_taper_ratio_inboard=self.wing_taper_ratio_inboard,
                    cabin_l=self.fuselage.cabin_l,
                    position=self.position.translate('-z', 0.40 * self.cabin_d))

    @Part(parse=False)
    def right_winglet(self):
        if self.TYPE_winglet == 0:
            return CantedWinglet(name="Canted Winglet",
                                 airfoil_root=self.ct_airfoil_root,
                                 airfoil_tip=self.ct_airfoil_tip,
                                 chord_wingtip=self.right_wing.chords[2],
                                 chord_root_ratio=self.ct_chord_root_ratio,
                                 taper_ratio=self.ct_taper_ratio,
                                 semi_span=self.right_wing.wing_span/2,
                                 height_ratio=self.ct_height_ratio,
                                 sweep=self.ct_sweep,
                                 cant=self.ct_cant,
                                 twist_tip=self.ct_twist_tip,
                                 toe=self.ct_toe,
                                 limit_span_increase=self.limit_span_increase,
                                 position=self.right_wing.section_positions[2],
                                 avl_duplicate_pos=self.position,
                                 suppress=not self.winglet_ON)

        elif self.TYPE_winglet == 1:
            return WingtipFence(name="Wingtip Fence",
                                airfoil_up=self.wtf_airfoil_up,
                                airfoil_root=self.wtf_airfoil_root,
                                airfoil_down=self.wtf_airfoil_down,
                                chord_wingtip=self.right_wing.chords[2],
                                semi_span=self.right_wing.wing_span/2,
                                chord_root_ratio=self.wtf_chord_root_ratio,
                                taper_ratio_up=self.wtf_taper_ratio_up,
                                taper_ratio_down=self.wtf_taper_ratio_down,
                                height_up_ratio=self.wtf_height_up_ratio,
                                height_down_ratio=self.wtf_height_down_ratio,
                                sweep_up=self.wtf_sweep_up,
                                sweep_down=self.wtf_sweep_down,
                                twist_up=self.wtf_twist_up,
                                twist_down=self.wtf_twist_down,
                                position=rotate(translate(self.right_wing.section_positions[2],
                                                          'x', self.right_wing.chords[2] -
                                                          self.right_wing.chords[2] * self.wtf_chord_root_ratio),
                                                'x', np.deg2rad(-90)),
                                avl_duplicate_pos=self.position,
                                suppress=not self.winglet_ON)

        elif self.TYPE_winglet == 2:
            return RakedWingtip(name="Raked Wingtip",
                                airfoil_start=self.right_wing.airfoil_tip,
                                airfoil_tip=self.rkt_airfoil_tip,
                                chord_start=self.right_wing.chords[2],
                                taper_ratio=self.rkt_taper_ratio,
                                semi_span=self.right_wing.wing_span / 2,
                                span_ratio=self.rkt_span_ratio,
                                sweep_le=self.rkt_sweep_le,
                                position=self.right_wing.section_positions[2],
                                avl_duplicate_pos=self.position,
                                suppress=not self.winglet_ON)

        elif self.TYPE_winglet == 3:
            return Sharklet(name="Sharklet",
                            airfoil_start=self.right_wing.airfoil_tip,
                            airfoil_mid=self.skt_airfoil_mid,
                            airfoil_tip=self.skt_airfoil_tip,
                            # chord start = wing.chord_tip
                            chord_start=self.right_wing.chords[2],
                            chord_mid2start_ratio=self.skt_chord_mid2start_ratio,
                            K_lambda=self.skt_K_lambda,
                            wing_semi_span=self.right_wing.wing_span / 2,
                            height_ratio=self.skt_height_ratio,
                            KR=self.skt_KR,
                            cant=self.skt_cant,
                            sweep_le=self.skt_sweep_le,
                            sweep_transition_te=self.skt_sweep_transition_te,
                            twist=self.skt_twist,
                            dihedral=self.right_wing.wing_dihedral,
                            nu_blended_sections=self.skt_nu_blended_sections,
                            limit_span_increase=self.limit_span_increase,
                            position=rotate(self.right_wing.section_positions[2],
                                            'x', np.deg2rad(self.right_wing.wing_dihedral)),
                            avl_duplicate_pos=self.position,
                            suppress=not self.winglet_ON)

    @Part
    def left_wing(self):
        return MirroredShape(shape_in=self.right_wing.solid,
                             reference_point=self.right_wing.position,
                             transparency=0.4,
                             vector1=self.right_wing.position.Vz,
                             vector2=self.right_wing.position.Vx)

    @Part
    def left_winglet(self):
        return MirroredShape(shape_in=self.right_winglet.surface,
                             reference_point=self.right_wing.position.point,
                             # Two vectors to define the mirror plane
                             vector1=self.right_wing.position.Vz,
                             vector2=self.right_wing.position.Vx,
                             suppress=not self.winglet_ON,
                             mesh_deflection=0.0001)

    @Part
    def vtp_wing(self):
        return VerticalTail(vtp_root_airfoil=self.vtp_root_airfoil,
                            vtp_tip_airfoil=self.vtp_tip_airfoil,
                            vtp_aspect_ratio=self.vtp_aspect_ratio,
                            vtp_sweep=self.vtp_sweep,
                            vtp_area=self.vtp_area,
                            htp_area=self.htp_right_wing.htp_area,
                            lh=self.htp_right_wing.lh,
                            Vh=self.htp_right_wing.Vh,
                            MAC_chord_length=self.right_wing.MAC_chord_length,
                            starting_point_mac=self.right_wing.starting_point_mac,
                            cabin_d=self.fuselage.cabin_d,
                            wing_span=self.right_wing.wing_span,
                            position=rotate90(self.position.translate('z', (0.48 * self.cabin_d)),
                                              'x'),
                            color="blue")

    @Attribute(settable=True)
    def length_fuselage_ahead_wing(self):
        return 12

    @Attribute
    # complete fuselage length
    def fuselage_length(self):
        if self.htp_right_wing.end_pos_htp > self.vtp_wing.end_pos_vtp:
            return self.htp_right_wing.end_pos_htp + 3 + self.length_fuselage_ahead_wing
        else:
            return self.vtp_wing.end_pos_vtp + 3 + self.length_fuselage_ahead_wing

    @Part
    def fuselage(self):
        return Fuselage(pass_down="ln_d, lt_d",
                        position=self.right_wing.position.translate('-x', self.length_fuselage_ahead_wing,
                                                                    'z', 0.4*self.cabin_d),
                        fuselage_length=self.fuselage_length,
                        front_part_length=self.length_fuselage_ahead_wing,
                        cabin_d=self.cabin_d,
                        color="Blue")

    @Attribute
    def avl_surfaces(self):  # this scans the product tree and collect all instances of the avl.Surface class
        return self.find_children(lambda o: isinstance(o, avl.Surface))

    @Part
    def avl_configuration(self):
        return avl.Configuration(name='A320',
                                 reference_area=self.right_wing.wing_area_total,
                                 reference_span=self.right_wing.wing_span,
                                 reference_chord=self.right_wing.MAC_chord_length,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.M_cruise)

    @Part
    def step_writer_components(self):
        return STEPWriter(default_directory=DIR,
                          trees=[self.fuselage,
                                 self.right_wing,
                                 self.right_winglet,
                                 self.left_wing,
                                 self.left_winglet])

    @Part
    def avl_analysis(self):
        return Analysis(aircraft=[self.right_wing,
                                  self.right_winglet,
                                  self.left_wing,
                                  self.left_winglet],
                        altitude=9000,
                        TYPE_winglet=self.TYPE_winglet,
                        TYPE_wing_airfoil=self.TYPE_wing_airfoil,
                        configuration=self.avl_configuration,
                        case_settings=[('fixed_cl', {'alpha': avl.Parameter(name='alpha', value=0.5, setting='CL')})])

    # @Part
    # def Q3d_analysis(self):
    #     return Q3dAnalysis(wing_geom=self.right_wing,
    #                        air_property=self.avl_analysis.air_property,
    #                        mach=self.M_cruise,
    #                        CL=0.5)

    @Part
    def EMWET(self):
        return Emwet(MTOW=83000,
                     MZF=72000,
                     wing=self.right_wing,
                     winglet=self.right_winglet,
                     lift_distribution=self.avl_analysis.lift_strip,
                     moment_distribution=self.avl_analysis.M_pitching_strip)

    @Part
    def PDFwriter(self):
        return PDFwriter(res=0)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft(label="Aircraft assembly")
    display(obj)
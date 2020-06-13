# Todo: update the total wing span each time when winglet or wing geometry changes and limit it.
# Todo: Implement EMWET and make necessary assumptions to achieve the convergence. Plot the influence of winglet on
#       range and fuel


from parapy.geom import *
from parapy.core import *
from Geometry.section import Section
import kbeutils.avl as avl
import numpy as np
from Function.help_fucntions import *
from parapy.core.validate import *


class CantedWinglet(GeomBase):
    name = Input("Canted Wingelet")
    airfoil_root = Input()
    airfoil_tip = Input()
    chord_wingtip = Input()
    chord_root_ratio = Input()
    taper_ratio = Input()
    wing_span = Input()
    height_ratio = Input()
    sweep = Input()
    cant = Input()
    twist_tip = Input()

    avl_duplicate_pos = Input()

    @Attribute
    def chords(self):
        chord_root = self.chord_wingtip * self.chord_root_ratio
        chord_tip = chord_root * self.taper_ratio
        return chord_root, chord_tip

    @Attribute
    def airfoils(self):
        return self.airfoil_root, self.airfoil_tip

    @Attribute
    def height(self):
        return self.wing_span * self.height_ratio

    @Attribute
    def section_positions(self):
        root_pos = rotate(translate(self.position, 'x', self.chord_wingtip - self.chords[0]),
                          'x', np.deg2rad(90-self.cant))
        tip_pos = rotate(root_pos.translate('y', self.height,
                                            'x', np.tan(np.deg2rad(self.sweep))*self.height),
                         'y', np.deg2rad(self.twist_tip))
        return root_pos, tip_pos

    @Attribute
    def span_incl_winglet(self):
        tip_pos = self.section_positions[1]
        total_span = tip_pos.y * 2
        return total_span

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.chords[child.index],
                       position=self.section_positions[child.index])

    @Part
    def surface(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True,
                           mesh_deflection=0.0001)

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.avl_duplicate_pos[1],
                           sections=[section.avl_section
                                     for section in self.sections])

    # ***************** Warnings **********************
    @cant.on_slot_change
    def on_cant_change(self, slot, new, old):
        self.cant = check_slot_change('cant', new, old, [0, 40])

    @sweep.on_slot_change
    def on_sweep_change(self, slot, new, old):
        self.sweep = check_slot_change('sweep', new, old, [0, 45])

    @twist_tip.on_slot_change
    def on_twist_tip_change(self, slot, new, old):
        self.twist_tip = check_slot_change('twist_tip', new, old, [0, 6])

    @chord_root_ratio.on_slot_change
    def on_chord_root_ratio_change(self, slot, new, old):
        self.chord_root_ratio = check_slot_change('chord_root_ratio', new, old, [0.4, 1])

    @taper_ratio.on_slot_change
    def on_taper_ratio_change(self, slot, new, old):
        self.taper_ratio = check_slot_change('taper_ratio', new, old, [0.2, 0.5])

    @height_ratio.on_slot_change
    def height_ratio_listener(self, slot, new, old):
        self.height_ratio = check_slot_change('height_ratio', new, old, [0.05, 0.1])


class WingtipFence(GeomBase):
    name = Input("Wingtip Fence")
    # 0.1645 0.7862 0.1722 0.4778 0.5063 53 66 0 0
    airfoil_up = Input()
    airfoil_root = Input()
    airfoil_down = Input()
    wing_span = Input()
    chord_wingtip = Input()

    chord_root_ratio = Input(validator=Range(0.3, 0.6))
    taper_ratio_up = Input(validator=Range(0.2, 0.5))
    taper_ratio_down = Input(validator=Range(0.2, 0.5))
    height_up_ratio = Input(validator=Range(0.02, 0.6))
    height_down_ratio = Input(validator=Range(0.02, 0.6))
    sweep_up = Input(validator=Range(50, 70))
    sweep_down = Input(validator=Range(50, 70))
    twist_up = Input(validator=Range(0, 5))
    twist_down = Input(validator=Range(-5, 0))

    avl_duplicate_pos = Input()

    @Attribute
    def chords(self):
        chord_root = self.chord_wingtip * self.chord_root_ratio
        chord_up = chord_root * self.taper_ratio_up
        chord_down = chord_root * self.taper_ratio_down
        return chord_up, chord_root, chord_down

    @Attribute
    def height_up(self):
        return self.wing_span * self.height_up_ratio

    @Attribute
    def height_down(self):
        return self.wing_span * self.height_down_ratio

    @Attribute
    def airfoils(self):
        return self.airfoil_up, self.airfoil_root, self.airfoil_down

    @Attribute
    def section_positions(self):
        up_pos = self.position.translate('x', self.height_up * np.tan(np.radians(self.sweep_up)),
                                         'y', self.height_up)
        root_pos = self.position
        down_pos = self.position.translate('x', self.height_down * np.tan(np.radians(self.sweep_down)),
                                           'y', -self.height_down)
        return [up_pos, root_pos, down_pos]

    @Attribute
    def span_incl_winglet(self):
        return self.wing_span

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.chords[child.index],
                       position=self.section_positions[child.index])

    @Part
    def surface(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True,
                           mesh_deflection=0.0001)

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.avl_duplicate_pos[1],
                           sections=[section.avl_section
                                     for section in self.sections])


class RakedWingtip(GeomBase):
    name = Input("RakedWingtip")

    airfoil_start = Input()
    airfoil_tip = Input()
    chord_start = Input()
    taper_ratio = Input()
    wing_span = Input()
    span_ratio = Input()
    sweep_le = Input()

    avl_duplicate_pos = Input()

    @Attribute
    def span(self):
        return self.span_ratio * self.wing_span

    @Attribute
    def chords(self):
        chord_tip = self.chord_start * self.taper_ratio
        return self.chord_start, chord_tip

    @Attribute
    def airfoils(self):
        return self.airfoil_start, self.airfoil_tip

    @Attribute
    def section_positions(self):
        start_pos = self.position
        tip_pos = self.position.translate('x', self.span * np.tan(np.deg2rad(self.sweep_le)),
                                          'y', self.span)
        return start_pos, tip_pos

    @Attribute
    def span_incl_winglet(self):
        tip_pos = self.section_positions[1]
        total_span = tip_pos.y * 2
        return total_span

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.chords[child.index],
                       position=self.section_positions[child.index])

    @Part
    def surface(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True,
                           mesh_deflection=0.0001)

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.avl_duplicate_pos[1],
                           sections=[section.avl_section
                                     for section in self.sections])

    # ************************** Warnings ******************************
    @sweep_le.on_slot_change
    def sweep_le_listener(self, slot, new, old):
        self.sweep_le = check_slot_change("sweep_le", new, old, [50, 65])

    @span_ratio.on_slot_change
    def span_ratio_listener(self, slot, new, old):
        self.span_ratio = check_slot_change("span_ratio", new, old, [0.06, 0.1])

    @taper_ratio.on_slot_change
    def taper_ratio_listener(self, slot, new, old):
        self.taper_ratio = check_slot_change("taper_ratio", new, old, [0.15, 0.3])


class Sharklet(GeomBase):
    name = Input("Sharklet")

    airfoil_start = Input()
    airfoil_mid = Input()
    airfoil_tip = Input()
    chord_start = Input()
    chord_mid = Input()

    K_lambda = Input(0.6)
    wing_semi_span = Input()
    height_ratio = Input(0.1)
    # taper ratio coefficient
    KR = Input(0.4)
    cant = Input(10.)
    sweep_le = Input(46)
    sweep_transition_te = Input(15.)
    twist = Input()
    dihedral = Input()
    nu_blended_sections = Input(10)  # number of sections between start and mid

    avl_duplicate_pos = Input()

    @Attribute
    # radius of the transition part
    def radius(self):
        return self.height * self.KR * np.cos(np.deg2rad(self.cant/2)+np.pi/4) / np.cos(np.deg2rad(self.cant))

    @Attribute
    def height(self):
        return self.height_ratio * self.wing_semi_span

    @Input
    def taper_ratio(self):
        return self.K_lambda * (self.height / self.wing_semi_span) ** 0.2

    @Input
    def chord_tip(self):
        return self.taper_ratio * self.chord_mid

    @Attribute
    # arc length of the transition curve
    def transition_length(self):
        return self.radius * (np.pi/2 - np.deg2rad(self.cant) - np.deg2rad(self.dihedral))

    @Attribute
    # the distance between the mid and start airfoil in x direction
    def transition_delta_x(self):
        # total displacement in x direction between start and mid section
        delta_X = self.chord_start + self.transition_length * np.tan(np.deg2rad(self.sweep_transition_te))\
                  - self.chord_mid
        # displacement in x per section
        disp_x = np.zeros(self.nu_blended_sections)
        for i in range(0, self.nu_blended_sections):
            disp_x[i] = (i+1) * delta_X / (self.nu_blended_sections+1)
        return disp_x

    @Attribute
    # For now, assume the leading edge curvature of the transition part is a straight line
    # assume the trailing edge of the transition part is the extension of the trailing edge of the wing
    def chords(self):
        chords_length = np.zeros(self.nu_blended_sections+3)
        chords_length[0] = self.chord_start
        chords_length[self.nu_blended_sections+1] = self.chord_mid
        chords_length[self.nu_blended_sections+2] = self.chord_tip
        # the change in chord length within transition sections
        delta_chord = (self.chord_mid - self.chord_start) / (self.nu_blended_sections+1)
        for i in range(1, self.nu_blended_sections+1):
            chords_length[i] = self.chord_start + i * delta_chord
        return chords_length

    @Attribute
    def airfoils(self):
        airfoils_group = [self.airfoil_start]
        # use NACA0006 for all temporarily
        airfoils_group = airfoils_group + ["NACA0006"] * self.nu_blended_sections
        airfoils_group.append(self.airfoil_mid)
        airfoils_group.append(self.airfoil_tip)
        return airfoils_group

    @Attribute
    def section_positions(self):
        start_pos = self.position
        # the translation in xyz directions to get the mid root section
        transl_mid_x = self.chord_start + self.transition_length * np.tan(np.deg2rad(self.sweep_transition_te))\
            - self.chord_mid
        transl_mid_y = self.radius * np.sin(np.deg2rad(90-self.cant-self.dihedral))
        transl_mid_z = self.radius - self.radius * np.cos(np.deg2rad(90-self.cant-self.dihedral))
        # apart from translation, rotation is needed.
        mid_pos = rotate(self.position.translate('x', transl_mid_x, 'y', transl_mid_y, 'z', transl_mid_z),
                         'x', np.deg2rad(90-self.cant-self.dihedral))
        tip_pos = rotate(mid_pos.translate('x', self.height * np.tan(np.deg2rad(self.sweep_le)),
                                           'y', self.height/np.cos(np.deg2rad(self.cant))),
                         'y', np.deg2rad(self.twist))
        section_pos = [start_pos]
        # rotation angle needed by each transition section to achieve a smooth arc, translation is calculated
        # according to the delta angle
        delta_angle = np.deg2rad(90-self.cant-self.dihedral) / (self.nu_blended_sections+1)
        for i in range(0, self.nu_blended_sections):
            delta_x = self.transition_delta_x[i]
            delta_y = self.radius * np.sin(delta_angle*(i+1))
            delta_z = self.radius - self.radius * np.cos(delta_angle*(i+1))
            section_pos.append(rotate(start_pos.translate('x', delta_x, 'y', delta_y, 'z', delta_z),
                               'x', delta_angle*(i+1)))
        section_pos.append(mid_pos)
        section_pos.append(tip_pos)
        return section_pos

    @Attribute
    def span_incl_winglet(self):
        tip_pos = self.section_positions[2]
        total_span = tip_pos.y * 2
        return total_span

    @Part
    def sections(self):
        return Section(quantify=len(self.chords),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.chords[child.index],
                       position=self.section_positions[child.index])

    @Part
    def surface(self):
        return LoftedSolid(profiles=[section.curve for section in self.sections],
                           ruled=True,
                           mesh_deflection=0.0001)

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.avl_duplicate_pos[1],
                           sections=[section.avl_section
                                     for section in self.sections])

    # *************** Warnings *******************

    @cant.on_slot_change
    def on_cant_change(self, slot, new, old):
        self.cant = check_slot_change('cant', new, old, [0, 40])

    @KR.on_slot_change
    def on_KR_change(self, slot, new, old):
        self.KR = check_slot_change('KR', new, old, [0.35, 0.5])

    @height_ratio.on_slot_change
    def height_ratio_listener(self, slot, new, old):
        self.height_ratio = check_slot_change('height_ratio', new, old, [0.05, 0.1])

    @K_lambda.on_slot_change
    def K_lambda_listener(self, slot, new, old):
        self.K_lambda = check_slot_change('K_lambda', new, old, [0.55, 0.65])

    @sweep_le.on_slot_change
    def sweep_le_listener(self, slot, new, old):
        self.sweep_le = check_slot_change('sweep_le', new, old, [45, 65])

    @sweep_transition_te.on_slot_change
    def sweep_transition_te_listener(self, slot, new, old):
        self.sweep_transition_te = check_slot_change('sweep_transition_te', new, old, [10, 25])

    @twist.on_slot_change
    def twist_listener(self,slot, new, old):
        self.twist = check_slot_change('twist', new, old, [0, 5])

    @nu_blended_sections.on_slot_change
    def nu_blended_sections_listener(self, slot, new, old):
        self.nu_blended_sections = check_slot_change('nu_blended sections', new, old, [5, 10])



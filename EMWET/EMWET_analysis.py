import os
from parapy.geom import *
from parapy.core import *
from parapy.core.decorators import action
import numpy as np
import time


class Emwet(Base):
    namefile = Input('A320')
    MTOW = Input()  # [kg]
    MZF = Input()  # [kg]
    load_factor = Input(2.5)
    num_section = Input()
    num_airfoil = Input()

    wing = Input()
    winglet = Input()

    spar_front = Input(0.15)
    spar_rear = Input(0.6)
    ftank_start = Input(0.15)
    ftank_end = Input(0.6)
    eng_num = Input(1)
    eng_ypos = Input(0.359)
    eng_mass = Input(2400)  # kg
    E_al = Input('7E10')  # N/m2
    rho_al = Input('2700')  # kg/m3
    Ft_al = Input('2.95E8')  # N/m2
    Fc_al = Input('2.95E8')  # N/m2
    pitch_rib = Input(0.5)  # [m]
    eff_factor = Input(0.96)  # Depend on the stringer type

    lift_distribution = Input()
    moment_distribution = Input()

    @Attribute
    def num_airfoil(self):
        num_af_wing = len(self.wing.chords)
        return num_af_wing

    @Attribute
    def num_section(self):
        num_section_wing = len(self.wing.chords)
        return num_section_wing

    '''
    @Attribute
    def num_airfoil(self):
        num_af_wing = len(self.wing.chords)
        num_af_winglet = len(self.winglet.chords)
        if self.TYPE_winglet == 0:
            return num_af_wing + num_af_winglet
        elif self.TYPE_winglet == 1:
            return num_af_wing
        else:
            return num_af_wing + num_af_winglet - 1

    @Attribute
    def num_section(self):
        num_section_wing = len(self.wing.chords)
        num_section_winglet = len(self.winglet.chords)
        if self.TYPE_winglet == 0:
            return num_section_wing + num_section_winglet - 1
        elif self.TYPE_winglet == 1:
            return num_section_wing
        else:
            return num_section_wing + num_section_winglet - 1

    @Attribute
    def total_span(self):
        end = len(self.winglet.section_positions)
        tip_pos = self.winglet.section_positions[end-1]
        return abs(tip_pos.y) * 2
    '''

    @Attribute(settable=False)
    def path_load_file(self):
        path_wd = os.getcwd()
        path_load_file = path_wd + '\\EMWET\\my_aircraft.load'
        return path_load_file

    @Attribute(settable=False)
    def path_init_file(self):
        path_wd = os.getcwd()
        path_init_file = path_wd + '\\EMWET\\my_aircraft.init'
        return path_init_file

    @Attribute(settable=False)
    def path_weight_file(self):
        path_wd = os.getcwd()
        path_weight_file = path_wd + '\\EMWET\\my_aircraft.weight'
        return path_weight_file

    @Attribute(settable=False)
    def path_emwet_output(self):
        path_wd = os.getcwd()
        path_emwet_output = os.path.join(path_wd, 'Output/EMWET_output.txt')
        return path_emwet_output

    def wing_weight_est(self):
        path_wd = os.getcwd()
        self.write_init()
        self.write_load()
        path_matlab = path_wd + "\\EMWET"
        # change to matlab file directory
        os.chdir(path_matlab)
        cmd = "matlab -nodesktop -nosplash -r \"emwet_exe;exit\""
        os.system(cmd)
        os.chdir(path_wd)
        while not os.path.exists(self.path_weight_file):
            time.sleep(1)
        with open(self.path_weight_file, 'r') as f:
            first_line = f.readline()
            end = len(first_line) - 1
            wing_weight = first_line[22:end]
        return wing_weight

    def write_init(self):
        with open(self.path_init_file, 'w') as f:
            f.write(str(self.MTOW) + ' ' + str(self.MZF) + '\n')
            f.write(str(self.load_factor) + '\n')
            f.write(str(round(self.wing.wing_area_total, 1)) + ' ' + str(self.wing.span_wing) +
                    ' ' + str(self.num_section) + ' ' + str(self.num_airfoil) + '\n')
            for i in range(0, self.num_airfoil):
                which_af = self.wing.section_positions[i]
                af_pos = 2 * which_af.y / self.wing.span_wing
                f.write(str(round(af_pos, 2)) + ' ')
                f.write(self.wing.airfoils[i] + '\n')
            for i in range(0, self.num_section):
                section_pos = self.wing.section_positions[i]
                f.write(str(round(self.wing.chords[i], 2)) + ' ')
                f.write(str(round(section_pos.x, 2)) + ' ')
                f.write(str(round(section_pos.y, 2)) + ' ')
                f.write(str(round(section_pos.z, 2)) + ' ')
                f.write(str(self.spar_front) + ' ')
                f.write(str(self.spar_rear) + '\n')

            f.write(str(self.ftank_start) + ' ' + str(self.ftank_end) + '\n')

            f.write(str(self.eng_num) + '\n')
            f.write(str(self.eng_ypos) + ' ' + str(self.eng_mass) + '\n')

            f.write(self.E_al + ' ' + self.rho_al + ' ' + self.Ft_al + ' ' + self.Fc_al + '\n')
            f.write(self.E_al + ' ' + self.rho_al + ' ' + self.Ft_al + ' ' + self.Fc_al + '\n')
            f.write(self.E_al + ' ' + self.rho_al + ' ' + self.Ft_al + ' ' + self.Fc_al + '\n')
            f.write(self.E_al + ' ' + self.rho_al + ' ' + self.Ft_al + ' ' + self.Fc_al + '\n')

            f.write(str(self.eff_factor) + ' ' + str(self.pitch_rib) + '\n')
            f.write('1 \n')

    def write_load(self):
        with open(self.path_load_file, 'w') as f:
            num_strips = len(self.lift_distribution)
            y = np.linspace(0, 1, num_strips)
            for i in range(0, len(y)):
                to_write = str(y[i]) + ' ' + str(self.lift_distribution[i]) + ' ' + \
                           str(self.moment_distribution[i]) + '\n'
                f.write(to_write)

    @action(label='Reset')
    def reset(self):
        # try:
        #     os.remove(self.path_init_file)
        #     os.remove(self.path_weight_file)
        #     os.remove(self.path_emwet_output)
        # except FileNotFoundError:
        #     pass
        try:
            os.remove(self.path_init_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.path_load_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.path_weight_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.path_emwet_output)
        except FileNotFoundError:
            pass

    @action(label='Record')
    def record(self):
        wing_weight = self.wing_weight_est()
        with open(self.path_emwet_output, 'a+') as f:
            to_write = wing_weight + '\n'
            f.write(to_write)
        try:
            os.remove(self.path_init_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.path_load_file)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.path_weight_file)
        except FileNotFoundError:
            pass









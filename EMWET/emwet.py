import os
from parapy.geom import *
from parapy.core import *
import numpy as np


class EMWET():
    namefile = Input('Fokker50')
    MTOW = Input()  # [kg]
    MZF = Input()  # [kg]
    load_factor = Input()
    span = Input()  # [m]
    root_chord = Input()  # [m]
    taper_ratio = Input()
    sweep_le = Input()  # [deg]


    spar_front = Input()
    spar_rear = Input()
    ftank_start = Input()
    ftank_end = Input()
    eng_num = Input()
    eng_ypos = Input()
    eng_mass = Input()  # kg
    E_al = Input()  # N/m2
    rho_al = Input()  # kg/m3
    Ft_al = Input()  # N/m2
    Fc_al = Input()  # N/m2
    pitch_rib = Input()  # [m]
    eff_factor = Input()  # Depend on the stringer type
    Airfoil = Input()
    section_num = Input()
    airfoil_num = Input()
    wing_surf = Input()


    @Attribute
    def exe_emwet(self):
        with open('Fokker50test.init', 'w') as f:
            f.writeline(str(self.MTOW) + ' ' + str(self.MZF) + '\n')
            f.write(str(self.load_factor) + '\n')
            f.write(self.wing_surf + ' ' + self.span + ' ' + self.section_num + ' ' + self.airfoil_num)
            f.write(self.Airfoil)
            f.write(self.Airfoil)
            f.write(self.root_chord + ' ' + '0 0 0 ' + self.spar_front + ' ' + self.spar_rear)
            f.write(self.root_chord * self.taper_ratio + ' ' + str(self.span / 2 * np.tan(self.sweep_le)) + ' ' +
                    str(self.span / 2) + ' ' + '0' + ' ' + self.spar_front + ' ' + self.spar_rear)

            f.write(ftank_start + ' ' + ftank_end)

            f.write(eng_num)
            f.write(eng_ypos, eng_mass)

            f.write(E_al, rho_al, Ft_al, Fc_al)
            f.write(E_al, rho_al, Ft_al, Fc_al)
            f.write(E_al, rho_al, Ft_al, Fc_al)
            f.write(E_al, rho_al, Ft_al, Fc_al)

            f.write(eff_factor, pitch_rib)
            f.write('1 \n')
        path = os.path + '/ENWET/emwet_exe.m'
        cmd = "matlab -nodesktop -nosplash -r \"run(" + path + ")exit\""
        os.system(cmd)
        return 'EMWET analysis finished'




import numpy as np
import pathlib


class ReadGeometry:
    def __init__(self, name):
        self.name = name
        cur_path = pathlib.Path().absolute()
        with open(str(cur_path)+"/input.txt", 'r') as f:
            searchlines = f.readlines()
        for i, line in enumerate(searchlines):
            if "#Wing" == line.rstrip():
                # pos_wing = np.array(searchlines[i+1].split(), dtype=float)
                # self.wing_position_fraction_long = pos_wing[0]
                # self.wing_position_fraction_vrt = pos_wing[1]

                w_airfoils = searchlines[i+1].split()
                self.w_af_root = w_airfoils[0]
                self.w_af_kink = w_airfoils[1]
                self.w_af_tip = w_airfoils[2]

                dat_wing = np.array(searchlines[i+2].split(), dtype=float)
                self.wing_span = dat_wing[0]
                self.M_cruise = dat_wing[1]
                self.M_tech_factor = dat_wing[2]
                self.wing_c_root = dat_wing[3]
                self.incidence = dat_wing[4]
                self.twist = dat_wing[5]
                self.wing_taper_ratio_inboard = dat_wing[6]

            if "#Winglet" == line.rstrip():
                self.TYPE_winglet = int(searchlines[i+1])
                self.wlt_airfoils = searchlines[i+2].split()
                self.dat_wlt = np.array(searchlines[i+3].split(), dtype=float)
                # 0: canted winglet
                # 1: wingtip fence
                # 2: raked wingtip
                # 3: Sharklet
                if self.TYPE_winglet == 0:
                    self.ct_airfoil_root = self.wlt_airfoils[0]
                    self.ct_airfoil_tip = self.wlt_airfoils[1]

                    self.ct_chord_root_ratio = self.dat_wlt[0]
                    self.ct_taper_ratio = self.dat_wlt[1]
                    self.ct_height_ratio = self.dat_wlt[2]
                    self.ct_sweep = self.dat_wlt[3]
                    self.ct_cant = self.dat_wlt[4]
                    self.ct_twist_tip = self.dat_wlt[5]
                if self.TYPE_winglet == 1:
                    self.wtf_airfoil_up = self.wlt_airfoils[0]
                    self.wtf_airfoil_root = self.wlt_airfoils[1]
                    self.wtf_airfoil_down = self.wlt_airfoils[2]

                    self.wtf_chord_root_ratio = self.dat_wlt[0]
                    self.wtf_taper_ratio_up = self.dat_wlt[1]
                    self.wtf_taper_ratio_down = self.dat_wlt[2]
                    self.wtf_height_up_ratio = self.dat_wlt[3]
                    self.wtf_height_down_ratio = self.dat_wlt[4]
                    self.wtf_sweep_up = self.dat_wlt[5]
                    self.wtf_sweep_down = self.dat_wlt[6]
                    self.wtf_twist_up = self.dat_wlt[7]
                    self.wtf_twist_down = self.dat_wlt[8]
                if self.TYPE_winglet == 2:
                    self.rkt_airfoil_start = self.wlt_airfoils[0]
                    self.rkt_airfoil_tip = self.wlt_airfoils[1]

                    self.rkt_chord_start = self.dat_wlt[0]
                    self.rkt_taper_ratio = self.dat_wlt[1]
                    self.rkt_span_ratio = self.dat_wlt[2]
                    self.rkt_sweep_le = self.dat_wlt[3]
                # Sharklet
                if self.TYPE_winglet == 3:
                    self.skt_airfoil_start = self.wlt_airfoils[0]
                    self.skt_airfoil_mid = self.wlt_airfoils[1]
                    self.skt_airfoil_tip = self.wlt_airfoils[2]

                    self.skt_chord_mid = self.dat_wlt[0]
                    self.skt_K_lambda = self.dat_wlt[1]
                    self.skt_height_ratio = self.dat_wlt[2]
                    self.skt_KR = self.dat_wlt[3]
                    self.skt_cant = self.dat_wlt[4]
                    self.skt_sweep_le = self.dat_wlt[5]
                    self.skt_sweep_transition_te = self.dat_wlt[6]
                    self.skt_twist = self.dat_wlt[7]
                    self.skt_nu_blended_sections = int(self.dat_wlt[8])



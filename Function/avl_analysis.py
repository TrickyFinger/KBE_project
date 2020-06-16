from kbeutils import avl
from parapy.core import *
import matplotlib.pyplot as plt
import numpy as np
import os
from parapy.core.validate import *
from parapy.core.decorators import action
from parapy.gui.image import Image
from Function.help_fucntions import *
from fpdf import FPDF
#from EMWET import emwet


class Analysis(avl.Interface):
    # TYPE_winglet and altitude will be passed to interface for warning evaluation
    # TYPE_wing_airfoil will be passed to interface for plotting purposes
    # supercritical: 1, NACA-6: 2, Conventional: 3.
    # TYPE_wing_airfoil will be passed to interface for plotting purposes
    # supercritical: 1, NACA-6: 2, Conventional: 3.
    aircraft = Input(in_tree=True)
    case_settings = Input()
    altitude = Input(validator=Range(0, 11000))
    plot_which = Input('altitude')
    TYPE_winglet = Input()
    TYPE_wing_airfoil = Input()
    wing_weight = Input()
    configuration = Input()

    @Attribute
    def air_property(self):
        # barometric formula for air density (0-11000m)
        g = 9.80665  # gravitational accel       [m/s2]
        R = 8.3144598  # universal gas constant    [Nm]
        M = 0.0289644  # molar mass of Earth's air [kg/mol]
        T = 288.15  # standard temperature      [K]
        L = -0.0065  # temperature lapse rate    [K/m]
        rho_b = 1.225  # air density at sea level  [kg/m3]
        gamma = 1.4
        air_density = rho_b * (T / (T + L * int(self.altitude))) ** (1 + (g * M) / (R * L))
        speed_of_sound = np.sqrt(gamma * R * (T + L * int(self.altitude)) / M)
        return air_density, speed_of_sound

    @Attribute
    # dynamic pressure
    def q(self):
        rho = self.air_property[0]
        a = self.air_property[1]
        q = 0.5 * rho * (a * float(self.configuration.mach)) ** 2
        return q

    @Part
    def cases(self):
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])

    @Attribute
    def Bref(self):
        Bref = []
        for _, result in self.results.items():
            Bref.append(float(result['Totals']['Bref']))
        return Bref

    @Attribute
    def Sref(self):
        Sref = []
        for _, result in self.results.items():
            Sref.append(float(result['Totals']['Sref']))
        return Sref

    @Attribute
    def CL(self):
        for _, result in self.results.items():
            return result['Totals']['CLtot']

    @Attribute
    def CD(self):
        for _, result in self.results.items():
            return result['Totals']['CDtot']

    @Attribute
    def l_over_d(self):
        res = round(float(self.CL) / float(self.CD), 2)
        return str(res)

    @Attribute
    def M_pitching_strip(self):  # sectional pitching moment
        Cm_c4 = []
        for _, result in self.results.items():
            for i in range(0, int(len(result['StripForces']['wing']['cm_c/4'])/2)):
                Cm_c4_next = result['StripForces']['wing']['cm_c/4'][i]
                Cm_c4.append(float(Cm_c4_next))
        return np.array(Cm_c4)

    @Attribute
    def lift_strip(self):
        ccl = []
        yle = []
        for _, result in self.results.items():
            for i in range(0, int(len(result['StripForces']['wing']['c cl'])/2)):
                ccl.append(float(result['StripForces']['wing']['c cl'][i]))
                yle.append(float(result['StripForces']['wing']['Yle'][i]))
        ccl = np.array(ccl)
        dy = yle[3] - yle[2]
        return ccl * dy * self.q

    @Attribute
    def root_bending_moment(self):
        wlt_names = ['Canted Winglet', 'Wingtip Fence', 'Raked Wingtip']
        wing_ccl = []
        wing_yle = []
        winglet_ccl = []
        winglet_yle = []
        for case_name, result in self.results.items():
            ccl = result['StripForces']['wing']['c cl']
            wing_ccl.append(ccl)
            yle = result['StripForces']['wing']['Yle']
            wing_yle.append(yle)
            for idx_name in range(len(wlt_names)):
                try:
                    name = wlt_names[idx_name]
                    ccl = result['StripForces'][name]['c cl']
                    winglet_ccl.append(ccl)
                    yle = result['StripForces'][name]['Yle']
                    winglet_yle.append(yle)
                    break
                except KeyError:
                    continue
        nu_wing_strips = int(len(wing_ccl[1]) / 2)
        nu_winglet_strips = int(len(winglet_ccl[1]) / 2)

        wing_ccl = np.array(wing_ccl)
        wing_ccl = wing_ccl[:, 0:nu_wing_strips]
        wing_yle = np.array(wing_yle)
        wing_yle = wing_yle[:, 0:nu_wing_strips]
        winglet_ccl = np.array(winglet_ccl)
        winglet_ccl = winglet_ccl[:, 0:nu_winglet_strips]
        winglet_yle = np.array(winglet_yle)
        winglet_yle = winglet_yle[:, 0:nu_winglet_strips]

        M_root_wing = np.zeros(len(self.results.items()))
        M_root_winglet = np.zeros(len(self.results.items()))
        for i in range(0, len(self.results.items())):
            if self.TYPE_winglet == 0:
                # canted winglet
                cant = self.aircraft.right_winglet.cant
            elif self.TYPE_winglet == 1:
                # wingtip fence
                cant = 0
            else:
                # raked wingtip, ignore dihedral
                cant = 90

            dy_wing = wing_yle[0, 3] - wing_yle[0, 2]
            dy_winglet = winglet_yle[0, 3] - winglet_yle[0, 2]
            Sf_wing = np.array(wing_ccl[i, :] * self.q * dy_wing)
            Sf_winglet = np.array(winglet_ccl[i, :] * self.q * dy_winglet)

            M_root_wing[i] = sum(np.multiply(Sf_wing, wing_yle[i, :]))
            M_root_winglet[i] = sum(np.multiply(Sf_winglet, winglet_yle[i, :]))

        M_root = M_root_wing + M_root_winglet

        return list(M_root)

    @Attribute
    def plot_M_root_bending(self):
        with open("../output.txt", 'r+') as f:
            data = []
            count = 0
            for line in f:
                if count % 2 == 1:
                    temp = line.split('\t')
                    temp = [x for x in temp if x != '' and x != '\n']
                    data.append(temp)
                count = count + 1
            data = np.array(data)
            if self.plot_which == 'altitude':
                x_val = data[:, 3]
                plt.xlabel('altitude (m)')
            if self.plot_which == 'sweep':
                x_val = data[:, 4]
                plt.xlabel('sweep')
            y_val = data[:, 7]
            plt.plot(x_val, y_val)
            plt.ylabel('Root bending moment (Nm) at Cl=0.5')
            plt.show()
        return 'Plot done'

    @Attribute
    def path_avl_output(self):
        path_wd = os.getcwd()
        path_avl_output = path_wd + '\\Output\\AVL_output.txt'
        return path_avl_output

    # @Attribute
    # def output_images(self):
    #     image_1 = Image(shapes=self.aircraft[0].solid, view='top', width=400, height=400)
    #     image_2 = Image(shapes=self.aircraft[1].surface, view='top', width=400, height=400)
    #     return image_1, image_2

    @action(label='Reset')
    def reset(self):
        try:
            os.remove(self.path_avl_output)
        except FileNotFoundError:
            pass

    @action(label='Check Inputs')
    def check(self):
        if self.TYPE_winglet == 3:
            msg1 = "Sharklet is not supported for AVL analysis"
            warnings.warn(msg1)
            generate_warning("Warning: ", msg1)
        elif not 0 < self.altitude < 11000:
            msg2 = "Altitude should not exceed 11000m"
            warnings.warn(msg2)
            generate_warning("Warning: ", msg2)
        else:
            msg = "You are flying at " + str(self.altitude) + "m. All good! Launch it!"
            generate_warning(" ", msg)

    @action(label='Record')
    def record(self):
        with open(self.path_avl_output, 'a+') as f:
            to_write = str(self.CL) + ' ' + str(self.CD) + ' ' + str(self.l_over_d) + '\n'
            f.write(to_write)

    # @action(label='Adjust cant')
    # def adjust_cant(self):
    #     msg1 = "This function is to analyze the effect of cant angle on the performance, only applicable to " \
    #            "Canted winglet (TYPE_winglet = 0)"
    #     msg2 = "This is not a Canted winglet (TYPE_winglet = 0)"
    #     generate_warning('Warning: ', msg1)
    #     if self.TYPE_winglet != 0:
    #         generate_warning('Warning: ', msg2)
    #         return
    #     else:
    #         cant = self.configuration.right_winglet.cant




from kbeutils import avl
from parapy.core import *
import matplotlib.pyplot as plt
import numpy as np
from parapy.core.validate import *
from parapy.core.decorators import action
from parapy.gui.image import Image
from Function.help_fucntions import *
from fpdf import FPDF
from EMWET import emwet


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
    configuration = Input()
    sp_fuel =

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

        right_wing = self.aircraft.right_wing

        with open("../output.txt", "a") as file:
            file.write('Airfoil type\tWinglet type\tMach\tAltitude\tSweep 0.25c\t\tq\t'
                       'M_root(fix AoA)\t\tM_root(fix Cl)\n\t\t')
            file.write(str(self.TYPE_wing_airfoil))
            file.write('\t\t\t\t')
            file.write(str(self.TYPE_winglet))
            file.write("\t\t")
            file.write(str(self.configuration.mach))
            file.write("\t\t")
            file.write(str(4000 * self.altitude - 3000))
            file.write("\t\t")
            file.write(str(round(right_wing.wing_sweep_025c, 2)))
            file.write("\t")
            file.write(str(round(q, 2)))
            file.write("\t")
        return q

    @Part
    def cases(self):
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])

    @Attribute
    def l_over_d(self):
        return {case_name: result['Totals']['CLtot'] / result['Totals']['CDtot']
                for case_name, result in self.results.items()}

    @Attribute
    def CL(self):
        return {case_name: result['Totals']['CLtot']
                for case_name, result in self.results.items()}

    @Attribute
    def CD(self):
        return {case_name: result['Totals']['CDtot']
                for case_name, result in self.results.items()}

    @Attribute
    def rootBendingMoment(self):
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

        file = open("../output.txt", "a")
        for m in list(M_root):
            file.write(str(int(m)))
            file.write("\t\t\t")
        file.write("\n")
        file.close()

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
    def output_images(self):
        image_1 = Image(shapes=self.aircraft[0].solid, view='top', width=400, height=400)
        image_2 = Image(shapes=self.aircraft[1].surface, view='top', width=400, height=400)
        return image_1, image_2

    @Attribute
    def range_increase(self):
        emwet_case1 = emwet(namefile='xxx',
                            MTOW=Input(),  # [kg]
                            MZF=Input(),  # [kg]
                            load_factor=Input(),
                            span=Input(),  # [m]
                            root_chord=Input(),  # [m]
                            taper_ratio=Input(),
                            sweep_le=Input(),  # [deg]

                            spar_front=Input(),
                            spar_rear=Input(),
                            ftank_start=Input(),
                            ftank_end=Input(),
                            eng_num=Input(),
                            eng_ypos=Input(),
                            eng_mass=Input(),  # kg
                            E_al=Input(),  # N/m2
                            rho_al=Input(),  # kg/m3
                            Ft_al=Input(),  # N/m2
                            Fc_al=Input(),  # N/m2
                            pitch_rib=Input(),  # [m]
                            eff_factor=Input(),  # Depend on the stringer type
                            Airfoil=Input(),
                            section_num=Input(),
                            airfoil_num=Input(),
                            wing_surf=Input())

    @Attribute
    def range_est(self):
        cruise_speed = self.configuration.mach * self.air_property[1]


    @Attribute
    def fuel_est(self):


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

    @action(label='Print PDF')
    def printPDF(self):
        self.output_images[0].write('Output/test1.png')
        self.output_images[1].write('Output/test2.png')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.image('Output/test1.png', 10, 10)
        pdf.output('Output/testpdf.pdf', 'F')

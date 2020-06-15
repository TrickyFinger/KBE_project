# This file was created by Anita Mohil on March 21,2020
from parapy.core import *
from parapy.geom import *
from math import radians
from math import tan
from Function.help_fucntions import *
import warnings


class Fuselage(GeomBase):
    """Create fuselage shape based on user inputs"""
    ln_d = Input(1.22)  # nose slenderness ratio
    lt_d = Input(2.724)  # tail slenderness ratio
    fuselage_length = Input()
    cabin_d = Input()

    # **************** Fixed value *******************

    @Attribute
    # Tail upsweep angle measured from centreline
    def upsweep_angle(self):
        return 10

    @Attribute
    # scaling of nose sections ( 5 sections)
    def fu_sections(self):
        return [0.1, 0.55, 0.8, 0.9, 0.96, 1.]

    @Attribute
    # tail cone radius as percentage of the cabin radius
    def fraction_r(self):
        return 0.1

    # ***********************************************
    """ CALCULATE NOSE LENGTH OF THE FUSELAGE """
    @Attribute
    def nose_length(self):
        return self.cabin_d * self.nose_slenderness_ratio

    """ CALCULATE THE RADIUS OF THE TAIL AT SEVERAL SECTIONS AND LATER FORM A LOFTED SOLID """
    @Attribute
    def tail_radius(self):
        return self.fraction_r * self.cabin_d / 2

    """ CALCULATES THE LENGTH OF THE CABIN """
    @Attribute
    def cabin_l(self):
        return self.fuselage_length - (self.nose_length + self.tail_length)

    @Part
    def cabin(self):
        """ create cabin part of the fuselage, modeled as a cylinder, rotate to align with x axis and translate
        such that the nose starts at Point(0,0,0) """
        return TransformedShape(shape_in=RotatedShape(Cylinder(radius=self.cabin_d / 2.,
                                                               height=self.cabin_l),
                                                      self.position, Vector(0, 1, 0), radians(90)),
                                from_position=self.position,
                                to_position=translate(self.position, 'x', self.nose_length),
                                color='white')

    @Attribute
    def nose_step_length(self):
        """ step size in between the generated curves"""
        steplength = self.nose_length / (len(self.fu_sections) - 1)
        return steplength

    @Attribute
    def local_nose_radius(self):
        """ nose radius at each specified position"""
        local_nose_r = []
        for i in self.fu_sections:
            local_nose_r.append(self.cabin_d / 2. * i)
        return local_nose_r

    @Part
    def nose_crv(self):
        """generate circular curves for the nose"""
        return Circle(quantify=len(self.fu_sections),
                      radius=self.local_nose_radius[child.index],
                      position=rotate90(translate(self.position, x=child.index * self.nose_step_length),
                                        Vector(0, 1, 0)))

    @Part
    def nose(self):
        """ generate the nose profile """
        return LoftedSolid(profiles=self.nose_crv,
                           color='white')

    # ----------------TAIL SECTION---------------########

    """ calculate length of the fuselage tail"""
    @Attribute
    def tail_length(self):
        return self.tail_slenderness_ratio * self.cabin_d

    """ use the different tail sections to form a complete lofted solid for the tail """
    @Part
    def fuselage_tail(self):
        """
        create truncated cone with the end radius tail_r
        """
        return LoftedSolid(profiles=[Circle(radius=self.cabin_d / 2.,
                                            position=rotate90(translate(self.cabin.position,
                                                                        x=self.cabin_l), Vector(0, 1, 0))),
                                     Circle(radius=(self.cabin_d / 2) * 0.99,
                                            position=rotate90(translate(self.cabin.position,
                                                                        x=self.cabin_l + 0.25,
                                                                        z=((self.cabin_d / 2) - (
                                                                                self.cabin_d / 2) * 0.99)),
                                                              Vector(0, 1, 0))),
                                     Circle(radius=self.tail_radius,
                                            position=rotate90(translate(self.cabin.position,
                                                                        x=self.cabin_l + self.tail_length,
                                                                        z=self.tail_length * tan(
                                                                            radians(self.upsweep_angle))),
                                                              Vector(0, 1, 0)))],
                           color='white')

    # --------------- GENERATE WARNINGS ----------------------#
    popup_gui = Input(True)

    @Attribute
    def nose_slenderness_ratio(self):
        if self.ln_d < 1.22 or self.ln_d > 2.0:
            msg = "Nose slenderness ratio for a this assignment ranges between 1.22 to 2"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: ln_d Value changed", msg)
            return 1.22
        else:
            return self.ln_d

    @Attribute
    def tail_slenderness_ratio(self):
        if self.lt_d < 2.5 or self.lt_d > 3.2:
            msg = "Tail slenderness ratio values must be between 2.5 - 3.2"
            warnings.warn(msg)
            if self.popup_gui:
                generate_warning("Warning: lt_d Value changed", msg)
            return 2.724
        else:
            return self.lt_d


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage()
    display(obj)

from parapy.core import *
from parapy.geom import *
from parapy.gui import *
from math import *


class Engine(GeomBase):
    ########################################################################################################################
    ###THESE CAN REMAIN HARDCODED, WE NEED NOT TO CHANGE THESE DURING DEMONSTRATION

    casing_length = Input(float(0.7))
    engine_diameter = Input(float(0.9))
    exhaust_diameter_end = Input(float(0.5))
    exhaust_length_end = Input(float(1.4))
    nozzle_diameter = Input(float(0.4))
    nozzle_length = Input(float(1.6))
    pylon_length = Input(float(0.4))
    pylon_width = Input(float(0.7))
    pylon_height = Input(float(0.08))
    frac_cab = Input(float(0.94))

    # Inputs to position the engine with respect to the fuselage:
    Cabin_pos = Input(30)
    Cab_d = Input(10)
    Cab_l = Input(47)

    ########################################################################################################################

    @Attribute
    def Case_length(self):
        return self.casing_length

    @Attribute
    def Eng_diameter(self):
        return self.engine_diameter

    @Attribute
    def End_exhaust_diameter(self):
        return self.exhaust_diameter_end

    @Attribute
    def Exhaust_length_end(self):
        return self.exhaust_length_end

    @Attribute
    def Nozzle_diameter(self):
        return self.nozzle_diameter

    @Attribute
    def Nozzle_length(self):
        return self.nozzle_length

    @Attribute
    def Pylon_length(self):
        return self.pylon_length

    @Attribute
    def Pylon_width(self):
        return self.pylon_width

    @Attribute
    def Pylon_height(self):
        return self.pylon_height

    @Attribute
    def total_engine_length(self):
        return self.casing_length + self.exhaust_length_end + self.nozzle_length

    @Part(parse=False)
    def Eng_Case(self):
        circ1 = Circle(radius=self.engine_diameter / 2, position=Point(0, 0, 0))
        circ2 = Circle(radius=self.engine_diameter / 2, position=Point(0, 0, self.casing_length))
        circ3 = Circle(radius=self.exhaust_diameter_end / 2, position=Point(0, 0, self.exhaust_length_end))
        circ4 = Circle(radius=self.nozzle_diameter / 2, position=Point(0, 0, self.nozzle_length))

        return LoftedSolid(profiles=[circ1, circ2]), LoftedSolid(profiles=[circ2, circ3]), \
               LoftedSolid(profiles=[circ3, circ4])

    @Part(in_tree=True)
    def pylon(self):
        return Box(width=self.pylon_width,
                   length=self.pylon_length,
                   height=self.pylon_height,
                   color="red",
                   position=translate(self.position, 'y', self.engine_diameter / 2,
                                      rotate(self.position, 'y', -90 * (pi / 180))))

    # positioning of the engines
    #: ------------------------------------------------------------------------------------
    #: -------------------------------------------------------------------------------------

    @Attribute(in_tree=True)
    def right_engine(self):
        '''First rotate the wing such that it is aligned with the y axis, then place it in x direction at
        60% of the cabin. Lastly move the wing down to the bottom of the fuselage'''
        shape1 = TransformedShape(shape_in=RotatedShape(self.Eng_Case[0], self.Eng_Case[0].position,
                                                        Vector(0, 1, 0), radians(90)),
                                  from_position=self.position,
                                  to_position=translate(self.position,
                                                        'x', self.Cabin_pos + self.frac_cab * self.Cab_l,
                                                        'y', self.Cabin_pos - 0.95 * self.Cab_d / 2
                                                        - self.engine_diameter / 2 - self.pylon_length))
        return shape1

    @Part
    def right_pylon(self):
        '''First rotate the wing such that it is aligned with the y axis, then place it in x direction at
        60% of the cabin. Lastly move the wing down to the bottom of the fuselage'''
        return TransformedShape(shape_in=self.pylon,
                                from_position=self.position,
                                to_position=translate(self.position,
                                                      'x', self.Cabin_pos + self.frac_cab * self.Cab_l,
                                                      'y',
                                                      self.Cabin_pos - 0.95 * self.Cab_d / 2 - self.engine_diameter),
                                color='red')

    # @Part
    # def left_pylon(self):
    #     return MirroredShape(self.right_pylon, self.position, Vector(0, 0, 1), Vector(1, 0, 0),
    #                          color='red')
    #
    # @Attribute(in_tree=True)
    # def left_engine(self):
    #     return MirroredShape(self.right_engine[0], self.position, Vector(0, 0, 1), Vector(1, 0, 0)), \
    #            MirroredShape(self.right_engine[1], self.position, Vector(0, 0, 1), Vector(1, 0, 0)), \
    #            MirroredShape(self.right_engine[2], self.position, Vector(0, 0, 1), Vector(1, 0, 0))


if __name__ == '__main__':
    from parapy.gui import display

    obj = Engine()
    display(obj)

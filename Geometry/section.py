from kbeutils.geom import Naca4AirfoilCurve
from kbeutils.geom.curve import Naca5AirfoilCurve
from parapy.geom import *
from parapy.core import *
from Geometry import Airfoil
import kbeutils.avl as avl


class Section(GeomBase):
    
    # airfoil_name = Input(validator=_len_4_or_5)
    airfoil_name = Input("NACA2410")
    chord = Input()


    @Attribute
    def isNACA(self):
        return True if self.airfoil_name[0:4] == "NACA" else False

    @Attribute
    def airfoil_code(self):
        return self.airfoil_name[4:len(self.airfoil_name)] if self.isNACA == True else 0

    @Part(parse=False)
    def airfoil(self):
        if self.isNACA:
            return DynamicType(type=Naca5AirfoilCurve if len(self.airfoil_name) == 5 else Naca4AirfoilCurve,
                               designation=self.airfoil_code,
                               mesh_deflection=0.00001,
                               hidden=True)
        else:
            return Airfoil(airfoil_name=self.airfoil_name,
                           mesh_deflection=0.0001,
                           hidden=True)

    @Part
    def curve(self):
        return ScaledCurve(self.airfoil,
                           self.position.point,
                           self.chord,
                           mesh_deflection=0.00001)

    # @Part  # the camber of the airfoil is ignored
    # def avl_section_no_curvature(self):
    #     return avl.Section(chord=self.chord)

    # @Part  # the camber of the airfoil is accounted, but works only for NACA4 airfoil (AVL limitation)
    # def avl_section(self):
    #     return avl.Section(chord=self.chord,
    #                        airfoil=avl.NacaAirfoil(designation=self.airfoil_name))

    # @Part  # the camber of the airfoil is accounted. Any curve is allowed
    # def avl_section(self):
    #     return avl.Section(chord=self.chord,
    #                        airfoil=avl.DataAirfoil(self.curve.sample_points))

    @Part  # the camber of the airfoil is accounted. Any curve is allowed. It includes avl_section_by_points
    def avl_section(self):
        return avl.SectionFromCurve(curve_in=self.curve)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Section(airfoil_name="NACA2412",
                  chord=2,
                  label="wing section",
                  )
    display(obj)

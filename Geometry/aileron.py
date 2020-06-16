from parapy.geom import *
from parapy.core import *
from numpy import *


class Movable(GeomBase):
    loft = Input()  # a solid loft
    rootcrv = Input()  # root airfoil section
    tipcrv = Input()  # tip airfoil section

    mov_start = Input(0.15)  #: spanwise position of movable inboard section, as % of lifting surface span
    mov_end = Input(0.95)  #: spanwise position of movable outboard section, as % of lifting surface span

    h_c_fraction = Input(0.8)  # movable hing position, as % of chord
    s_c_fraction1 = Input(0.85)  # movable frontspar position, as % of chord
    s_c_fraction2 = Input(0.9)  # movable backspar position, as % of chord

    @Attribute  # position of the rib cutting planes (defining inboard and outboard position of movable)
    def closure_rib_pln_locs(self):
        return [self.rootcrv.location.interpolate(self.tipcrv.location, self.mov_start),
                self.rootcrv.location.interpolate(self.tipcrv.location, self.mov_end)]

    @Part  # the cutting planes defining the inboard and outboard position of the movable
    def closure_rib_plns(self):
        return Plane(quantify=2,
                     reference=self.closure_rib_pln_locs[child.index],
                     normal=self.position.Vy)

    @Part
    def closure_rib_plns_fused(self):  # generate a list of faces, on whose order it CANNOT be relied.
        return FusedShell(shape_in=self.loft.lateral_faces[0],  # this is the skin of the lifting surface
                          tool=self.closure_rib_plns)

    @Attribute  # sorting based on num of neighbours (which is a message answered by any face object)
    # Note that the sorted function has no side effect, i.e. it does not change the original list
    def wing_skin_fces_sorted(self):
        sorted_fces_by_n_neighbours = sorted(self.closure_rib_plns_fused.faces, key=lambda face: len(face.neighbours))
        return sorted_fces_by_n_neighbours[-1]  # sorting is in ascending order. The face with most neighbours is  /
        # thus the last one ([-1]) in the sorted list

    @Attribute
    def le_root(self):
        return self.rootcrv.location

    @Attribute
    def te_root(self):
        return Point(7.28960832, 0.0, -1.656)

    @Attribute
    def le_tip(self):
        return self.tipcrv.location

    @Attribute
    def te_tip(self):
        return Point(7.660832, 0.0, -1.656)

    @Part
    def hinge_pln(self):  # hinge line plane definition
        return Plane(reference=self.le_root.interpolate(self.te_root, self.h_c_fraction),
                     normal=Vector(1, 0, 0))

    @Part
    def hinge_pln_fused(self):  # notice difference with closed rib plane
        # fused. Here no extra surfaces are generated as the intersection between the plane and the sorted middle face /
        # do not form a closed boundary
        return FusedShell(shape_in=self.wing_skin_fces_sorted,
                          tool=self.hinge_pln)  # this results in 3 faces. The LE one and the upper and lower TE faces

    @Attribute
    def movable_skin_fcs(self):
        sorted_fces_by_cog_x = sorted(self.hinge_pln_fused.faces, key=lambda face: face.cog.x)
        return sorted_fces_by_cog_x[1:]  # wing leading edge excluded (i.e. all elements apart the first).
        # The two TE faces are kept because have the largest value of cog.x

    @Attribute  # movable spar points on root section
    def spar_pln_locs_root(self):
        return [self.le_root.interpolate(self.te_root, self.s_c_fraction1),
                self.le_root.interpolate(self.te_root, self.s_c_fraction2)]

    @Attribute  # movable spar points on tip section
    def spar_pln_locs_tip(self):
        return [self.le_tip.interpolate(self.te_tip, self.s_c_fraction1),
                self.le_tip.interpolate(self.te_tip, self.s_c_fraction2)]

    @Part
    def spar_plns(self):  # movable spar planes
        return Plane(quantify=2,
                     reference=self.spar_pln_locs_root[child.index],
                     normal=Vector(1, 0, 0))

    @Part
    def segmented_movable_skin_fcs(self):
        return SkinSparSegmentation(quantify=2,  # upper and lower movable faces
                                    spar_plns=self.spar_plns,  # 2 planes
                                    skin_fce=self.movable_skin_fcs[child.index])  # one face at the time

    @Attribute
    def spar_edge_pairs(self):
        # First sort edges in x direction (thus from LE to TE)
        fce1_spar_edges_sorted_in_x = sorted(self.segmented_movable_skin_fcs[0].spar_edges,
                                             key=lambda e: e.midpoint.x)
        fce2_spar_edges_sorted_in_x = sorted(self.segmented_movable_skin_fcs[1].spar_edges,
                                             key=lambda e: e.midpoint.x)
        # Then make sure that edge directions are the same for every edge. Otherwise, twist of
        # surfaces may occur.
        edge_pairs = []
        for e1, e2 in zip(fce1_spar_edges_sorted_in_x, fce2_spar_edges_sorted_in_x):
            edge_pairs.append([e1, e2.directed(e1.direction_vector)])
        return edge_pairs

    @Part
    def spar_faces(self):
        return RuledSurface(quantify=len(self.spar_edge_pairs),
                            curve1=self.spar_edge_pairs[child.index][0],
                            curve2=self.spar_edge_pairs[child.index][1])

    @Attribute
    def movable_faces(self):
        faces = []
        for segmented_movable_face in self.segmented_movable_skin_fcs:
            faces.append(segmented_movable_face.te_skin_fce)
            faces.append(segmented_movable_face.mainbox_skin_fce)
            faces.append(segmented_movable_face.le_skin_fce)
        faces.extend(self.spar_faces)
        return faces

    @Part
    def movable_faces_comp(self):
        """Make compound for easing rotation, translation or transformation of shape. Also
        convenient for nice visualisation. """
        return Compound(self.movable_faces,
                        transparency=0.3)


class SkinSparSegmentation(Base):
    spar_plns = Input()
    skin_fce = Input()

    @Part
    def spar_plns_fused(self):
        return FusedShell(shape_in=self.skin_fce,
                          tool=self.spar_plns)

    @Attribute
    def spar_edges(self):
        return [edge for edge in self.spar_plns_fused.edges if len(edge.on_faces) == 2]

    @Attribute
    def le_skin_fce(self):
        sorted_fces_in_x = sorted(self.spar_plns_fused.faces, key=lambda f: f.uv_center_point.x)
        return sorted_fces_in_x[0]

    @Attribute
    def mainbox_skin_fce(self):
        sorted_fces_in_x = sorted(self.spar_plns_fused.faces, key=lambda f: f.uv_center_point.x)
        return sorted_fces_in_x[1]

    @Attribute
    def te_skin_fce(self):
        sorted_fces_in_x = sorted(self.spar_plns_fused.faces, key=lambda f: f.uv_center_point.x)
        return sorted_fces_in_x[-1]

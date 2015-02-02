import bpy
from sys import argv
from pprint import pprint

import os
import sys
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))

from libvmf import parse

FILE = './test_maps/simple_brush.vmf'
# FILE = './ttt_67thway/src/ttt_67thway.vmf'

class PointsList(list):
    def add_unique(self, value):
        if value not in self:
            self.append(value)
        return self.index(value)


def main():
    with open(FILE, 'r') as maphandle:
        map_data = parse.VmfParser(maphandle)

    solids = map_data.mapdata['world']['solid']
    if not isinstance(solids, list):
        solids = [solids]
    for solid in solids:

        points_list = PointsList()
        print('=' * 80)
        faces = list()
        name = 'solid-%i' % solid['id']
        mesh = bpy.data.meshes.new(name)   # create a new mesh
        ob = bpy.data.objects.new(name, mesh)          # create an object with that mesh
        ob.location = bpy.context.scene.cursor_location   # position object at 3d-cursor
        bpy.context.scene.objects.link(ob)                # Link object to scene

        for side in solid['side']:
            plane = side['plane']
            pprint(side['id'])
            face = list()
            for idx, point in enumerate(plane.split('(')[1:]):
                point = tuple(point.rstrip(') ').split())
                point = [float(i) * 0.01 for i in point]
                point_idx = points_list.add_unique(point)
                pprint(('point', point, point_idx))
                face.append(point_idx)

            print('+' * 80)
            pprint(
                [points_list[i] for i in face]
            )
            # inherit_idx = points_list.add_unique(inherit)
            # pprint(('inherit', inherit, inherit_idx))
            print('+' * 80)
            faces.append(tuple(face))
            print('-' * 80)
            break;
        print('=' * 80)
        pprint(list(points_list))
        pprint(faces)

        # Fill the mesh with verts, edges, faces
        mesh.from_pydata(list(points_list), [], faces)   # edges or faces should be [], or you ask for problems
        mesh.update(calc_edges=True)    # Update mesh with new data

main()
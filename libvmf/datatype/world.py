""" Top level nodes
"""

from libvmf.datatype.base import ValveDict
from libvmf.datatype.base import ValveClass

from libvmf.datatype.solid import ValveSolid
from libvmf.datatype.entity import ValveEntity

from libvmf.datatype.camera import ValveCameras


class ValveWorld(ValveClass):
    """ The World Geometry Node
    """
    vmf_skyname = str
    vmf_maxpropscreenwidth = int
    vmf_detailvbsp = str
    vmf_detailmaterial = str
    vmf_comment = str
    vmf_mapversion = int
    vmf_classname = str
    vmf_solid = ValveSolid


class ValveMap(ValveDict):
    """ The file's outer most node
    """
    vmf_world = ValveWorld
    vmf_entity = ValveEntity
    vmf_cameras = ValveCameras
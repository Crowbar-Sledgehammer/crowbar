import sys
import time

from pprint import pprint, pformat

class ValveException(Exception):
    pass

class ValveKeyError(ValveException):
    pass

class ValveTypeError(ValveException):
    pass


class ValveDict(dict):
    vmf_id = int

    def __init__(self, *args, **kw):
        super(ValveDict, self).__init__()
        self.__setitem__ = super(ValveDict, self).__setitem__
    def __setitem__(self, key, value):
        if key == 'datatype':
            self.__setitem__(key, value)
            return

        vmf_key = 'vmf_%s' % key
        if not hasattr(self, vmf_key):
            raise ValveKeyError('Key `%s` not allowed in %s' % (key, self._type()))

        allowedcontainer = getattr(self, vmf_key)

        if not type(value) is allowedcontainer:
            # Lunacy!
            if not type(value)(allowedcontainer(value)) == value:
                raise ValveTypeError(
                    "Illigal Type %s for key `%s`, expected Type %s for value `%s`" % (
                        type(value), key, allowedcontainer, value
                    )
                )

            # We can cast it, we have te technology!
            value = allowedcontainer(value)

        self.__setitem__(key, value)

    def _type(self):
        return self.__class__.__name__

ValveDict.vmf_datatype = ValveDict

class ValveWorld(ValveDict):
    vmf_skyname = str
    vmf_maxpropscreenwidth = int
    vmf_detailvbsp = str
    vmf_detailmaterial = str
    vmf_comment = str
    vmf_mapversion = int
    vmf_classname = str

class ValveEntity(ValveDict):
    vmf_classname = str
    vmf_origin = str # "776.0 259.0 -96.0"

    def __setitem__(self, key, value):
        self.__setitem__(key, value)


class ValveCameras(ValveDict):
    vmf_activecamera = int

class ValveCamera(ValveDict):
    vmf_position = str # "[-2712.7458 6088.62 149.23857]"
    vmf_look = str # "[-2460.03 6088.62 65.0]"

class ValveDisplacement(ValveDict):
    vmf_power = int # "3"
    vmf_startposition = str # "[384.0 512.0 72.0]"
    vmf_elevation = int # "0"
    vmf_subdiv = int # "0"

    class _RowData(ValveDict):
        def __setitem__(self, key, value):
            # Allow variable keys
            if key.startswith('row') and key[3:].isdigit():
                setattr(self, 'vmf_%s' % key, str)

            super(ValveDisplacement._RowData, self).__setitem__(key, value)

    class AllowedVerts(ValveDict):
        def __setitem__(self, key, value):
            # todo, restruct to numeric keys only?
            self.__setitem__(key, value)

    class Alphas(_RowData):
        pass

    class Distances(_RowData):
        pass

    class Normals(_RowData):
        pass


class ValveSide(ValveDict):
    vmf_plane = str
    vmf_smoothing_groups = int
    vmf_material = str
    vmf_uaxis = str # "[0.0 0.0 -1.0 288] 0.25"
    vmf_vaxis = str # "[0.0 1.0 0.0 0] 0.25"
    vmf_lightmapscale = int

class ValveMap(ValveDict):
    vmf_world   = ValveWorld
    vmf_entity  = list
    vmf_cameras = ValveCameras


if '__main__' == __name__:
    test =    ValveMap()
    test['world'] = ValveWorld()
    test['world']['id'] = 1
    pprint(test)

class ValveMap_test(dict):
    lines = 0
    i = 0
    indent = 0
    mapobject = ValveWorld
    mapdata = mapobject()
    _parsenode = []
    datatypes = {
        'entity': ValveEntity,
        'world': ValveWorld,
        'cameras': ValveCameras,
        'camera': ValveCamera,
        'solid': ValveDict,
        'side': ValveSide,
        'dispinfo': ValveDisplacement,
        'normals': ValveDict,
        'distances': ValveDict,
        'alphas': ValveDict,
        'triangle_tags': ValveDict,
        'allowed_verts': ValveDict,
        'connections': list,
        # Todo Refactor datatypes to be children of datatype
        # ValveDisplacement:
        'allowed_verts': ValveDisplacement.AllowedVerts,
        'alphas': ValveDisplacement.Alphas,
        'distances': ValveDisplacement.Distances,
        'normals': ValveDisplacement.Normals,
    }
    _parseerrors = []

    """docstring for ValveMap"""
    def __init__(self, filehandle, stdout=sys.stdout):
        entry_time = time.time()
        super(ValveMap_test, self).__init__()
        self.filehandle = filehandle
        self.stdout = stdout

        self.lines = self.bufcount()
        self.minupdate = self.lines // 400 or 10


        self.iterator = iter(self.filehandle.readline, '')
        self.mapdata = self._parse(ValveWorld())
        self.elpsed_time = time.time() - entry_time
        self.stdout.write('\n%s\n' % self.elpsed_time)

        pprint(self._parseerrors)
        pprint(self.mapdata)
        # with open('dumps.vmfstuff', 'w') as fh:
            # fh.write(pformat(self.mapdata))

    def report(self, callback=lambda x: False):
        percent = "{0:.0f} ".format(float(self.i)/self.lines * 100)
        output = (percent, self.i, self.lines)
        if None != self.stdout:
            self.stdout.write(
                '%s%% %i/%i\r' % output
            )

        callback(output)
        return output

    def bufcount(self):
        """ Count lines in file as fast as possible! """
        self.filehandle.seek(0)
        buf_size = 1024 * 1024
        read_f = self.filehandle.read # loop optimization

        buf = read_f(buf_size)
        while buf:
            self.lines += buf.count('\n')
            buf = read_f(buf_size)

        self.filehandle.seek(0)

        return self.lines


    def _parse(self, output):
        try:
            while True:
                line = next(self.iterator).rstrip('\n\r')
                self.i += 1
                if line.endswith('}'):
                    return output
                line = line[self.indent:]
                if 0 == self.i % self.minupdate:
                    self.report()

                if line.startswith('{'):
                    assert datatype in self.datatypes, "Unknown datatype [ %s ]" % datatype
                    self.indent += 1
                    value = self._parse(self.datatypes[datatype]())
                    if isinstance(output, dict):
                        if type(value) is str and 'id' in value:
                            output[value['id']] = value
                        elif not datatype in output:
                            output['datatype'] = value
                        else:
                            if isinstance(list, output['datatype']):
                                output['datatype'].append(value)
                            else:
                                output['datatype'] = [output['datatype']].append(value)
                    elif isinstance(output, list):
                        output.append((datatype, value))
                    self.indent -= 1
                    continue

                if line.startswith('"'):
                    key, value = line.split('" "')
                    key = key[1:]
                    value = value[:-1]
                    if isinstance(output, dict):
                        if key in output:
                            self.stdout.write('Line %i: Duplicate key <%s> dropped\n' % (self.i, key))
                        try:
                            output[key] = value
                        except ValveException as err:
                            self._parseerrors.append('Ln %s: %s' % (self.i, err))

                    elif isinstance(output, list):
                        output.append((key, value))
                    continue


                datatype = line

        except StopIteration:
            assert 0 == len(self._parsenode)
            self.report()
            return output


if '__main__' == __name__:
    with open('ttt_67thway/src/ttt_67thway.vmf', 'r') as maphandle:
        ValveMap_test(maphandle)

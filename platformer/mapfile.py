import xml.etree.ElementTree
import base64
import zlib
import pygame
import sys

class MapFile:
    def __init__(self, filename):
        self.filename = filename

        # load and parse the TMX file
        tree = xml.etree.ElementTree.parse(filename)
        element = tree.getroot()

        # gather basic attributes of the entire map
        if element.tag != 'map':
            print >>sys.stderr, 'MapFile: root element of TMX file must be a "map"'
            sys.exit(1)
        attr = element.attrib
        if attr['orientation'] != 'orthogonal':
            print >>sys.stderr, 'MapFile: map must have "orthogonal" orientation'
            sys.exit(1)
        self.tilewidth = int(attr['tilewidth'])
        self.tileheight = int(attr['tileheight'])
        self.width = int(attr['width'])
        self.height = int(attr['height'])
        if 'backgroundcolor' in attr:
            self.backgroundcolor = attr['backgroundcolor']
        else:
            self.backgroundcolor = '#000000'

        # now parse the pieces
        self.tiles = {}
        self.background = []
        self.foreground = []
        self.solid = []
        self.objects = []

        for child in element:
            # load a tileset
            if child.tag == 'tileset':
                self._loadTileset(child)

            # is this a layer we know how to process?
            elif child.tag == 'layer':
                # load a background layer
                if child.attrib['name'] == 'background':
                    if len(self.background) > 0:
                        print >>sys.stderr, 'MapFile: >1 background layers found'
                        sys.exit(1)
                    self.background = self._loadLayer(child, 'background')

                #Load Foreground layer
                elif child.attrib['name'] == 'foreground':
                    if len(self.foreground) > 0:
                        print >>sys.stderr, 'MapFile: >1 foreground layers found'
                        sys.exit(1)
                    self.foreground = self._loadLayer(child, 'foreground')

                # load a solid layer
                elif child.attrib['name'] == 'solid':
                    if len(self.solid) > 0:
                        print >>sys.stderr, 'MapFile: >1 solid layers found'
                        sys.exit(1)
                    layer = self._loadLayer(child, 'solid')
                    for row in layer:
                        srow = []
                        for elt in row:
                            srow.append(elt > 0)
                        self.solid.append(srow)

                # no other known layer types
                else:
                    print >>sys.stderr, 'MapFile: unknown layer found in map file: {}'.format(child.attrib['name'])
                    sys.exit(1)

            # load object data
            elif child.tag == 'objectgroup':
                self._loadObjectlayer(child)

            # some other element we don't know how to process
            else:
                print >>sys.stderr, 'MapFile: unknown child element: {}'.format(child.tag)
                sys.exit(1)

        # make sure we found everything we expected
        if len(self.background) == 0:
            print >>sys.stderr, 'MapFile: no background layer found'
            sys.exit(1)
        if len(self.solid) == 0:
            print >>sys.stderr, 'MapFile: no solid layer found'
            sys.exit(1)
        if len(self.tiles) == 0:
            print >>sys.stderr, 'MapFile: no tileset found'
            sys.exit(1)

    def _loadTileset(self, element):
        if element.tag != 'tileset':
            print >>sys.stderr, '_loadTileset: wrong root element type: {}'.format(element.tag)
            sys.exit(1)
        attr = element.attrib

        # make sure this is a simple tileset with no complicating factors
        if 'tilewidth' in attr and int(attr['tilewidth']) != self.tilewidth:
            print >>sys.stderr, '_loadTileset: tile width mismatch: expecting {}, found {}'. \
                    format(self.tilewidth, int(attr['tilewidth']))
            sys.exit(1)
        if 'tileheight' in attr and int(attr['tileheight']) != self.tileheight:
            print >>sys.stderr, '_loadTileset: tile height mismatch: expecting {}, found {}'. \
                    format(self.tileheight, int(attr['tileheight']))
            sys.exit(1)
        if 'spacing' in attr and int(attr['spacing']) != 0:
            print >>sys.stderr, '_loadTileset: must have 0 spacing between tiles'
            sys.exit(1)
        if 'margin' in attr and int(attr['margin']) != 0:
            print >>sys.stderr, '_loadTileset: must have 0 margin between tiles'
            sys.exit(1)
        if 'source' in attr:
            print >>sys.stderr, '_loadTileset: tileset must come from image file, not TSX file'
            sys.exit(1)

        # where does our numbering start?
        gid = int(attr['firstgid'])
        loadedImage = False

        # process child elements
        for child in element:
            if child.tag == 'image':
                if loadedImage:
                    print >>sys.stderr, '_loadTileset: >1 image file found for a single tileset'
                    sys.exit(1)
                loadedImage = True
                self._loadTilesetImage(child, gid)
            else:
                print >>sys.stderr, '_loadTileset: {} objects are not supported in tilesets'.format(child.tag)
                sys.exit(1)
        if not loadedImage:
            print >>sys.stderr, '_loadTileset: did not find tileset image'
            sys.exit(1)

    def _loadTilesetImage(self, element, gid):
        if element.tag != 'image':
            print >>sys.stderr, '_loadTilesetImage: wrong root element type: {}'.format(element.tag)
            sys.exit(1)
        attr = element.attrib

        # make sure there is nothing complicated about this image
        if 'format' in attr:
            print >>sys.stderr, '_loadTilesetImage: image file must not be embedded'
            sys.exit(1)
        if 'trans' in attr:
            print >>sys.stderr, '_loadTilesetImage: transparency colors are not supported: use alpha channel'
            sys.exit(1)
        imagewidth = -1
        if 'width' in attr:
            imagewidth = int(attr['width'])
        imageheight = -1
        if 'height' in attr:
            imageheight = int(attr['height'])
        if 'source' not in attr:
            print >>sys.stderr, '_loadTilesetImage: missing source attribute'
            sys.exit(1)

        # load the image file
        image = pygame.image.load(attr['source'])
        (sizex, sizey) = image.get_size()
        if imagewidth >= 0 and imagewidth != sizex:
            print >>sys.stderr, '_loadTilesetImage: image width mismatch: expected {}, found {}'.format(imagewidth, sizex)
            sys.exit(1)
        if imageheight >= 0 and imageheight != sizey:
            print >>sys.stderr, '_loadTilesetImage: image height mismatch: expected {}, found {}'.format(imageheight, sizey)
            sys.exit(1)

        # carve it up into tiles
        for y in range(0, imageheight, self.tileheight):
            for x in range(0, imagewidth, self.tilewidth):
                r = pygame.rect.Rect(x, y, self.tilewidth, self.tileheight)
                tile = image.subsurface(r)
                if gid in self.tiles:
                    print >>sys.stderr, '_loadTilesetImage: duplicate gid: {}'.format(gid)
                    sys.exit(1)
                self.tiles[gid] = tile
                gid += 1

    def _loadLayer(self, element, name):
        if element.tag != 'layer':
            print >>sys.stderr, '_loadTileset: wrong root element type: {}'.format(element.tag)
            sys.exit(1)
        attr = element.attrib

        # check the attributes
        if 'name' not in attr or attr['name'] != name:
            print >>sys.stderr, '_loadLayer: expected layer with name {}, found {}'.format(repr(name), repr(attr['name']))
            sys.exit(1)
        if 'x' in attr and int(attr['x']) != 0:
            print >>sys.stderr, '_loadLayer: found x != 0'
            sys.exit(1)
        if 'y' in attr and int(attr['y']) != 0:
            print >>sys.stderr, '_loadLayer: found y != 0'
            sys.exit(1)
        if 'width' in attr and int(attr['width']) != self.width:
            print >>sys.stderr, '_loadLayer: width of {} does not match map width of {}'.format(int(attr['width']), self.width)
            sys.exit(1)
        if 'height' in attr and int(attr['height']) != self.height:
            print >>sys.stderr, '_loadLayer: height of {} does not match map height of {}'.format(int(attr['height']), self.height)
            sys.exit(1)
        # ignore opacity and visible attributes

        # load the actual data
        loadedData = False
        data = []
        for child in element:
            if child.tag != 'data':
                print >>sys.stderr, '_loadLayer: child element of unsupported type {} found'.format(child.tag)
                sys.exit(1)
            if loadedData:
                print >>sys.stderr, '_loadLayer: >1 data elements found'
                sys.exit(1)

            # is it in a format we understand?
            gids = []
            if 'encoding' not in child.attrib and 'compression' not in child.attrib:
                # load the list of tile numbers
                for tile in child:
                    if tile.tag != 'tile':
                        print >>sys.stderr, '_loadLayer: expected tile, found {} element'.format(tile.tag)
                        sys.exit(1)
                    gid = int(tile.attrib['gid'])
                    gids.append(gid)
            elif child.attrib['encoding'] != 'base64':
                print >>sys.stderr, '_loadLayer: unsupported encoding type: {}'.format(child.attrib['encoding'])
                sys.exit(1)
            elif child.attrib['compression'] != 'gzip' and child.attrib['compression'] != 'zlib':
                print >>sys.stderr, '_loadLayer: unsupported compression type: {}'.format(child.attrib['compression'])
                sys.exit(1)
            else:
                comp_elt = base64.standard_b64decode(child.text)
                if child.attrib['compression'] == 'gzip':
                    raw = zlib.decompress(comp_elt[10:], -zlib.MAX_WBITS)
                else:
                    raw = zlib.decompress(comp_elt)
                for i in range(0, len(raw), 4):
                    chunk = raw[i:i+4]
                    gid =  ord(chunk[0])
                    gid += ord(chunk[1]) * 0x100
                    gid += ord(chunk[2]) * 0x10000
                    gid += ord(chunk[3]) * 0x1000000
                    gids.append(gid)

            # convert it into rows
            row = []
            for (count, gid) in enumerate(gids):
                row.append(gid)
                if count % self.width == self.width - 1:
                    data.append(row)
                    row = []
            if len(row) != 0 or len(data) != self.height:
                print >>sys.stderr, '_loadLayer: found wrong number of tiles: {} when {} expected'.format(count, self.height * self.width)
                sys.exit(1)

            loadedData = True

        if not loadedData:
            print >>sys.stderr, '_loadLayer: no data section found'
            sys.exit(1)

        return data

    def _loadObjectlayer(self, element):
        if element.tag != 'objectgroup':
            print >>sys.stderr, '_loadObjectlayer: wrong root element type: {}'.format(element.tag)
            sys.exit(1)
        attr = element.attrib

        # ignore color, x, y, width, height, opacity, and visible
        groupname = attr['name']

        for child in element:
            if child.tag != 'object':
                print >>sys.stderr, '_loadObjectlayer: child element must be of type object, not {}'.format(child.tag)
                sys.exit(1)
            attr = child.attrib

            # get the name if any
            if 'name' in attr and attr['name'] != '':
                name = attr['name']
            else:
                name = None

            # get the type (required)
            if 'type' in attr and attr['type'] != '':
                kind = attr['type']
            else:
                print >>sys.stderr, '_loadObjectlayer: object must have a type'
                sys.exit(1)

            # get the object's position in pixels
            x = int(attr['x'])
            y = int(attr['y'])

            # get the size or tile number
            if 'gid' in attr:
                gid = int(attr['gid'])
                width, height = None, None

                # map editor places tiles based on lower-left corner
                y -= self.tileheight
            else:
                gid = None
                width = int(attr['width'])
                height = int(attr['height'])

            # make sure there are no child elements
            if len(child) > 0:
                print >>sys.stderr, '_loadObjectlayer: object must not have properties or be an ellipse, polygon, polyline, or image'
                sys.exit(1)

            o = Object(groupname, name, kind, x, y, width, height, gid)
            self.objects.append(o)
    def __str__(self):
        return 'MapFile({}), size: {}*{}, tilesize: {}*{}, tiles: {}, objects: {}'.format(
                self.filename, self.width, self.height, self.tilewidth, self.tileheight, len(self.tiles), len(self.objects))

    def __repr__(self):
        return self.__str__()

class Object:
    def __init__(self, group, name, kind, x, y, width, height, gid):
        self.group = group
        self.name = name
        self.kind = kind
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.gid = gid

    def __str__(self):
        return 'Object({},{},{},{},{},{},{},{})'.format(
                self.group, self.name, self.kind, self.x, self.y, self.width, self.height, self.gid)

    def __repr__(self):
        return self.__str__()

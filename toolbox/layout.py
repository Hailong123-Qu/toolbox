
import gui
import pcbnew
import math as m
from linear import Linear as ln

class Layout:
    """
    Class for common Pcbnew layout operations.
    """
    @staticmethod
    def get_selected_pads(board=None):
        if board is None:
            board = pcbnew.GetBoard()
        
        return list(filter(lambda p: p.IsSelected(), board.GetPads()))
    
    @staticmethod
    def get_pad_coord(pads):
        '''Obtain wxPoint(x,y) coordinates of pads.'''
        return list(filter(lambda p: p.GetPosition(), pads))
    
    @staticmethod
    def get_track_width():
        '''Returns current track width dimension that the user has set.'''
        return pcbnew.GetBoard().GetDesignSettings().GetCurrentTrackWidth()
    
    @staticmethod
    def get_selected_pad_centers():
        '''Returns the center coordinates of any module with a selected pad.'''
        board = pcbnew.GetBoard()
        modules = pcbnew.board.GetModules()
        spads = [p for p in board.GetPads() if p.IsSelected()]
        pcoords = [p.GetPosition() for p in spads]
        return [modules.GetPad(p).GetCenter() for p in pcoords]
    
    @staticmethod
    def draw_track_segment(board, start, end, net, layer=0):
        '''Returns a new pcbnew board with an added track.'''
        tseg = pcbnew.TRACK(board)
        tseg.SetStart(start)
        tseg.SetEnd(end)
        tseg.SetWidth(Layout.get_track_width())
        tseg.SetLayer(layer)
        board.Add(tseg)
        return board
    
    @staticmethod
    def get_selected_tracks(board=None):
        if board is None:
            board = pcbnew.GetBoard()
        
        return list(filter(lambda t: t.IsSelected(), board.GetTracks()))
    
    @staticmethod
    def dist(points):
        '''Distance between two points'''
        p0, p1 = points
        return m.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
    
    @staticmethod
    def closest_track_endpoints(tracks):
        p0, p1 = tracks[0].GetStart(), tracks[0].GetEnd()
        p2, p3 = tracks[1].GetStart(), tracks[1].GetEnd()
        distances = [Layout.dist([p0, p2]), Layout.dist([p0, p3]), \
                        Layout.dist([p1, p2]), Layout.dist([p1, p3])]
        if distances[0] == min(distances):
            return (p0, p2)
        elif distances[1] == min(distances):
            return (p0, p3)
        elif distances[2] == min(distances):
            return (p1, p2)
        elif distances[3] == min(distances):
            return (p1, p3)
    
    @staticmethod
    def closest_track_pad_endpoints(pad, track):
        p0, p1 = track.GetStart(), track.GetEnd()
        distances = [Layout.dist([p0, pad.GetPosition()]), \
                     Layout.dist([p1, pad.GetPosition()])]
        if distances[0] == min(distances):
            return (p0, pad.GetPosition())
        elif distances[1] == min(distances):
            return (p1, pad.GetPosition())        

    @staticmethod
    def smdRectPad(module, size, pos, name, angle, net):
        '''Build a rectangular pad.'''
        pad = pcbnew.D_PAD(module)
        pad.SetSize(size)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        # Set only the copper layer without mask
        # since nothing is mounted on these pads
        pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))       # Get active layer
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        
        pad.Rotate(pos, angle)
        # Set clearance to small value, because
        # pads can be very close together.
        # If distance is smaller than clearance
        # DRC doesn't allow routing the pads
        pad.SetLocalClearance(1)
        pad.SetNet(net)

        return pad

    @staticmethod
    def Polygon(module, points, layer):
        '''Draw a polygon through specified points.'''
        polygon = pcbnew.EDGE_MODULE(module)
        polygon.SetWidth(0)         # Disables outline
        polygon.SetLayer(layer)
        polygon.SetShape(pcbnew.S_POLYGON)
        polygon.SetPolyPoints(points)
        module.Add(polygon)

        return module
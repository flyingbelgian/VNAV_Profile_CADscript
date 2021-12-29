import FreeCAD, Part, csv

DOC = FreeCAD.activeDocument()
DOC_NAME = "SurfaceExperimenting"

def clear_doc():
    """Clear the active document deleting all the objects"""
    for obj in DOC.Objects:
        DOC.removeObject(obj.Name)

def setview():
    """Rearrange View"""
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Gui.activeDocument().activeView().viewTop()
    FreeCAD.Gui.activeDocument().activeView().setAxisCross(True)

def makeSurf(V1,V2,V3,V4):
    """Make a surface bound by 4 vertices"""
    L1 = Part.LineSegment(V1,V2)
    L3 = Part.LineSegment(V3,V4)
    E1 = Part.Edge(L1)
    E3 = Part.Edge(L3)
    surf = Part.makeRuledSurface(E1, E3)
    return surf

def makeSegment(width_start, width_end, x_start, x_end):
    V1 = FreeCAD.Vector(x_start,width_start,0)
    V2 = FreeCAD.Vector(x_start,width_start/2,0)
    V3 = FreeCAD.Vector(x_start,-width_start/2,0)
    V4 = FreeCAD.Vector(x_start,-width_start,0)
    V5 = FreeCAD.Vector(x_end,width_end,0)
    V6 = FreeCAD.Vector(x_end,width_end/2,0)
    V7 = FreeCAD.Vector(x_end,-width_end/2,0)
    V8 = FreeCAD.Vector(x_end,-width_end,0)
    primsurf = makeSurf(V2,V3,V6,V7)
    secsurf1 = makeSurf(V1,V2,V5,V6)
    secsurf2 = makeSurf(V3,V4,V7,V8)
    segment = primsurf.fuse((secsurf1, secsurf2)).removeSplitter()
    return segment

if DOC is None:
    FreeCAD.newDocument(DOC_NAME)
    FreeCAD.setActiveDocument(DOC_NAME)
    DOC = FreeCAD.activeDocument()
else:
    clear_doc()

#Import parameters
parameters = {}
with open("D:\GitHub\VNAV_Profile_CADscript\parameters.csv") as source:
    data = csv.reader(source)
    for row in data:
        parameters[row[0]] = float(row[1])

m = 1 #this value set to 1000 or as required to obtain correct final dimensions

THRx = 332638.270*m
THRy = 6241727.539*m
THRz = 4.915*m
THR = FreeCAD.Vector(THRx, THRy, THRz)
THR_angle = 166+(47/60)+(3/3600)

#Surface 1 - Nominal FAF to end of splay in
segment1 = makeSegment(parameters['SW_FAF']*m, parameters['SW_MAPt']*m, parameters['Dist_FAFtoTHR']*m, parameters['xFAF_splay']*m)
Part.show(segment1, "Segment_1")

#Surface2 - end of splay in to start of splay out
segment2 = makeSegment(parameters['SW_MAPt']*m, parameters['SW_MAPt']*m, parameters['xFAF_splay']*m, parameters['xMAPt_start']*m)
Part.show(segment2, "Segment_2")

#Surface3 - start splay out to end of splay out in MA
segment3 = makeSegment(parameters['SW_MAPt']*m, parameters['SW_MA']*m, parameters['xMAPt_start']*m, parameters['xMAPt_splay']*m)
Part.show(segment3, "Segment_3")

#Surface.Placement=FreeCAD.Placement(THR, FreeCAD.Rotation(-THR_angle,0,0), FreeCAD.Vector(0,0,0))

DOC.recompute()
setview()
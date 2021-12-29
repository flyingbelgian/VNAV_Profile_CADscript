import FreeCAD, Part

DOC = FreeCAD.activeDocument()
DOC_NAME = "SurfaceExperimenting"

def clear_doc():
    """Clear the active document deleting all the objects"""
    for obj in DOC.Objects:
        DOC.removeObject(obj.Name)

def setview():
    """Rearrange View"""
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Gui.activeDocument().activeView().viewIsometric()
    FreeCAD.Gui.activeDocument().activeView().setAxisCross(True)

def makeSurf(V1,V2,V3,V4):
    """Make a surface bound by 4 vertices"""
    L1 = Part.LineSegment(V1,V2)
    L3 = Part.LineSegment(V3,V4)
    E1 = Part.Edge(L1)
    E3 = Part.Edge(L3)
    surf = Part.makeRuledSurface(E1, E3)
    return surf

def fuseObjects(name,objects):
    obj = DOC.addObject("Part::MultiFuse", name)
    obj.Shapes = objects
    return obj

if DOC is None:
    FreeCAD.newDocument(DOC_NAME)
    FreeCAD.setActiveDocument(DOC_NAME)
    DOC = FreeCAD.activeDocument()
else:
    clear_doc()

m = 1

StartWidth = 2000*m
EndWidth = 4000*m
Length = 8000*m
Height = 100*m

THRx = 332638.270*m
THRy = 6241727.539*m
THRz = 4.915*m
THR = FreeCAD.Vector(THRx, THRy, THRz)
THR_angle = 166+(47/60)+(3/3600)

V1 = FreeCAD.Vector(-StartWidth,0,Height)
V2 = FreeCAD.Vector(-StartWidth/2,0,0)
V3 = FreeCAD.Vector(StartWidth/2,0,0)
V4 = FreeCAD.Vector(StartWidth,0,Height)
V5 = FreeCAD.Vector(-EndWidth,Length,Height)
V6 = FreeCAD.Vector(-EndWidth/2,Length,0)
V7 = FreeCAD.Vector(EndWidth/2,Length,0)
V8 = FreeCAD.Vector(EndWidth,Length,Height)

primsurf = makeSurf(V2,V3,V6,V7)
secsurf1 = makeSurf(V1,V2,V5,V6)
secsurf2 = makeSurf(V3,V4,V7,V8)

Surface = primsurf.fuse((secsurf1, secsurf2)).removeSplitter()
Part.show(Surface, "Surface")

#Surface.Placement=FreeCAD.Placement(THR, FreeCAD.Rotation(-THR_angle,0,0), FreeCAD.Vector(0,0,0))

DOC.recompute()
setview()
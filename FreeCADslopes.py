import FreeCAD, Part, csv

DOC = FreeCAD.activeDocument()
DOC_NAME = "SurfaceExperimenting"

####### At the moment this always assumes Cat D aicraft, functionality for different aircraft categories to be added later

m = 1 #this value set to 1000 or as required to obtain correct final dimensions
z = 5 #this value is multiplier for elevation to exaggerate vertical dimension

THRx = 332638.270*m
THRy = 6241727.539*m
THRz = 4.915*m*z
THR = FreeCAD.Vector(THRx, THRy, THRz)
THR_angle = 166+(47/60)+(3/3600)

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

def makeSegment(x_start, y_start, z_start, moc_start, x_end, y_end, z_end, moc_end):
    V1 = FreeCAD.Vector(x_start *m,  y_start *m, (z_start + moc_start) *m *z)
    V2 = FreeCAD.Vector(x_start *m,  y_start/2 *m, z_start *m *z)
    V3 = FreeCAD.Vector(x_start *m, -y_start/2 *m, z_start *m *z)
    V4 = FreeCAD.Vector(x_start *m, -y_start *m, (z_start + moc_start) *m *z)
    V5 = FreeCAD.Vector(x_end *m,  y_end *m, (z_end + moc_end) *m *z)
    V6 = FreeCAD.Vector(x_end *m,  y_end/2 *m, z_end *m *z)
    V7 = FreeCAD.Vector(x_end *m, -y_end/2 *m, z_end *m *z)
    V8 = FreeCAD.Vector(x_end *m, -y_end *m, (z_end + moc_end) *m *z)
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
param = {}
with open("D:\GitHub\VNAV_Profile_CADscript\parameters.csv") as source:
    data = csv.reader(source)
    for row in data:
        param[row[0]] = float(row[1])

#Surface start
zOAS_FAF = (param['xFAF'] - param['xFAS']) * param['grad_FAS']

#Segment 1 - Nominal FAF to end of splay in
zOAS_FAFsplay = (param['xFAF_splay'] - param['xFAS']) * param['grad_FAS']
segment1 = makeSegment(
    param['xFAF'], param['SW_FAF'], zOAS_FAF, param['MOC_final'],
    param['xFAF_splay'], param['SW_MAPt'], zOAS_FAFsplay, param['MOC_final'])
Part.show(segment1, "Segment_1")

#Segment2 - end of splay in to xFAS
zOAS_xFAS = 0
segment2 = makeSegment(
    param['xFAF_splay'], param['SW_MAPt'], zOAS_FAFsplay, param['MOC_final'],
    param['xFAS'], param['SW_MAPt'], zOAS_xFAS, param['MOC_final'])
Part.show(segment2, "Segment_2")

#Segment3 - xFAS to ground surface with final MOC
xOAS_end = - (param['MOC_final']-param['MOC_MA_init']) / param['grad_FAS'] + param['xFAS']
print(xOAS_end)   ### for debugging only!!!
segment3 = makeSegment(
    param['xFAS'], param['SW_MAPt'], 0, param['MOC_final'],
    xOAS_end, param['SW_MAPt'], 0, param['MOC_MA_init'])
Part.show(segment3, "Segment_3")

#Segment4 - ground surface with final MOC to start missed approach surface
segment4 = makeSegment(
    xOAS_end, param['SW_MAPt'], 0, param['MOC_MA_init'],
    param['xMAPt_start'], param['SW_MAPt'], 0, param['MOC_MA_init'])
Part.show(segment4, "Segment_4")

#Segment5 - ground surface start of missed approach to xZ
width_xZ = ((param['xMAPt_start'] - param['xZ_D_calc']) * param['splay_out']) + param['SW_MAPt']
segment5 = makeSegment(
    param['xMAPt_start'], param['SW_MAPt'], 0, param['MOC_MA_init'],
    param['xZ_D_calc'], width_xZ, 0, param['MOC_MA_init'])
Part.show(segment5, "Segment_5")

#Segment6 - xZ to end of MA splay
zOAS_MAsplay = - (param['xMAPt_splay'] - param['xZ_D_calc']) * param['grad_MA']
segment6 = makeSegment(
    param['xZ_D_calc'], width_xZ, 0, param['MOC_MA_init'],
    param['xMAPt_splay'], param['SW_MA'], zOAS_MAsplay, param['MOC_MA_init'])
Part.show(segment6, "Segment_6")

#Surface.Placement=FreeCAD.Placement(THR, FreeCAD.Rotation(-THR_angle,0,0), FreeCAD.Vector(0,0,0))

DOC.recompute()
setview()
# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This is derived from a cadquery script for generating QFP models in X3D format.
#
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
#
# Dimensions are from Jedec MS-026D document.

## requirements
## cadquery FreeCAD plugin
##   https://github.com/jmwright/cadquery-freecad-module

## to run the script just do: freecad make_gwexport_fc.py modelName
## e.g. c:\freecad\bin\freecad make_gw_export_fc.py SOIC_8

## the script will generate STEP and VRML parametric models
## to be used with kicad StepUp script

#* These are a FreeCAD & cadquery tools                                     *
#* to export generated models in STEP & VRML format.                        *
#*                                                                          *
#* cadquery script for generating QFP/SOIC/SSOP/TSSOP models in STEP AP214  *
#*   Copyright (c) 2015                                                     *
#* Maurice https://launchpad.net/~easyw                                     *
#* All trademarks within this guide belong to their legitimate owners.      *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc.,                                                      *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA           *
#*                                                                          *
#****************************************************************************

__title__ = "make GullWings ICs 3D models"
__author__ = "maurice and hyOzd"
__Comment__ = 'make GullWings ICs 3D models exported to STEP and VRML for Kicad StepUP script'

___ver___ = "1.3.3 15/08/2015"

# maui import cadquery as cq
# maui from Helpers import show
from math import tan, radians, sqrt
from collections import namedtuple

import sys, os

# maui start
import FreeCAD, Draft, FreeCADGui
import ImportGui


outdir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(outdir)

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui

#checking requirements
#######################################################################
FreeCAD.Console.PrintMessage("FC Version \r\n")
FreeCAD.Console.PrintMessage(FreeCAD.Version())
FC_majorV=FreeCAD.Version()[0];FC_minorV=FreeCAD.Version()[1]
FreeCAD.Console.PrintMessage('FC Version '+FC_majorV+FC_minorV+'\r\n')

if int(FC_majorV) <= 0:
    if int(FC_minorV) < 15:
        reply = QtGui.QMessageBox.information(None,"Warning! ...","use FreeCAD version >= "+FC_majorV+"."+FC_minorV+"\r\n")


# FreeCAD.Console.PrintMessage(all_params_soic)
FreeCAD.Console.PrintMessage(FreeCAD.ConfigGet("AppHomePath")+'Mod/')
file_path_cq=FreeCAD.ConfigGet("AppHomePath")+'Mod/CadQuery'
if os.path.exists(file_path_cq):
    FreeCAD.Console.PrintMessage('CadQuery exists\r\n')
else:
    msg="missing CadQuery Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki"
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)

#######################################################################

# CadQuery Gui
from Gui.Command import *

# Import cad_tools
import cq_cad_tools
# Reload tools
reload(cq_cad_tools)
# Explicitly load all needed functions
from cq_cad_tools import FuseObjs_wColors, GetListOfObjects, restore_Main_Tools, \
 exportSTEP, close_CQ_Example, exportVRML, saveFCdoc, z_RotateObject, Color_Objects

# Gui.SendMsgToActiveView("Run")
Gui.activateWorkbench("CadQueryWorkbench")
import FreeCADGui as Gui

close_CQ_Example(App, Gui)

# from export_x3d import exportX3D, Mesh
import cadquery as cq
from Helpers import show
# maui end

import cq_params_gw_soic  # modules parameters
from cq_params_gw_soic import *

import cq_params_gw_qfp  # modules parameters
from cq_params_gw_qfp import *

import cq_params_gw_ssop  # modules parameters
from cq_params_gw_ssop import *

import cq_params_gw_tssop  # modules parameters
from cq_params_gw_tssop import *

import cq_params_gw_sot  # modules parameters
from cq_params_gw_sot import *

# all_params= all_params_soic.copy()
# all_params.update(all_params_qfp)

# all_params1= all_params_soic.copy()
# all_params1.update(all_params_qfp)
# all_params= all_params1.copy()
# all_params.update(all_params_ssop)

all_params= all_params_soic.copy()
all_params.update(all_params_qfp)
all_params.update(all_params_ssop)
all_params.update(all_params_tssop)
all_params.update(all_params_sot)


# all_params = dict(all_params1.items() | all_params2.items())

def make_gw(params):

    c  = params.c
    the  = params.the
    tb_s  = params.tb_s
    ef  = params.ef
    fp_r  = params.fp_r
    fp_d  = params.fp_d
    fp_z  = params.fp_z
    R1  = params.R1
    R2  = params.R2
    S  = params.S
# automatically calculated    L  = params.L
    D1  = params.D1
    E1  = params.E1
    E   = params.E
    A1  = params.A1
    A2  = params.A2
    b   = params.b
    e   = params.e
    npx = params.npx
    npy = params.npy
    mN  = params.modelName
    rot = params.rotation
    dest_dir_pref = params.dest_dir_prefix

    if params.epad:
        D2 = params.epad[0]
        E2 = params.epad[1]

    # calculated dimensions for body
    # checking pin lenght compared to overall width
    # d=(E-E1 -2*(S+L)-2*(R1))
    L=(E-E1-2*(S+R1))/2
    FreeCAD.Console.PrintMessage('E='+str(E)+';E1='+str(E1)+';S='+str(S)+';L='+str(L)+'\r\n')

    ## d=(E-E1 -2*(S+L)-2*(R1))
    ## FreeCAD.Console.PrintMessage('E='+str(E)+';E1='+str(E1)+';S='+str(S)+';L='+str(L)+';d='+str(d)+'\r\n')
    ## #if (d > 0):
    ## if (d > c/10):  #tolerance
    ##     L=L+d/2
    ##     FreeCAD.Console.PrintMessage(str(E-E1-2*(S+L))+'\r\nincreasing pin lenght\r\n')
    ## if (d < -c/10):  #tolerance
    ##     L=L+d/2
    ##     FreeCAD.Console.PrintMessage(str(E-E1-2*(S+L))+'\r\ntrimming pin lenght\r\n')
    A = A1 + A2
    A2_t = (A2-c)/2 # body top part height
    A2_b = A2_t     # body bottom part height
    D1_b = D1-2*tan(radians(the))*A2_b # bottom width
    E1_b = E1-2*tan(radians(the))*A2_b # bottom length
    D1_t1 = D1-tb_s # top part bottom width
    E1_t1 = E1-tb_s # top part bottom length
    D1_t2 = D1_t1-2*tan(radians(the))*A2_t # top part upper width
    E1_t2 = E1_t1-2*tan(radians(the))*A2_t # top part upper length

    if ef!=0:
        case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
             workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
             rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
             loft(ruled=True).faces(">Z").fillet(ef)
    else:
        case = cq.Workplane(cq.Plane.XY()).workplane(offset=A1).rect(D1_b, E1_b). \
             workplane(offset=A2_b).rect(D1, E1).workplane(offset=c).rect(D1,E1). \
             rect(D1_t1,E1_t1).workplane(offset=A2_t).rect(D1_t2,E1_t2). \
             loft(ruled=True).faces(">Z")

    # fillet the corners
    if ef!=0:
        BS = cq.selectors.BoxSelector
        case = case.edges(BS((D1_t2/2, E1_t2/2, 0), (D1/2+0.1, E1/2+0.1, A2))).fillet(ef)
        case = case.edges(BS((-D1_t2/2, E1_t2/2, 0), (-D1/2-0.1, E1/2+0.1, A2))).fillet(ef)
        case = case.edges(BS((-D1_t2/2, -E1_t2/2, 0), (-D1/2-0.1, -E1/2-0.1, A2))).fillet(ef)
        case = case.edges(BS((D1_t2/2, -E1_t2/2, 0), (D1/2+0.1, -E1/2-0.1, A2))).fillet(ef)

    # first pin indicator is created with a spherical pocket
    sphere_r = (fp_r*fp_r/2 + fp_z*fp_z) / (2*fp_z)
    sphere_z = A + sphere_r * 2 - fp_z - sphere_r
    sphere = cq.Workplane("XY", (-D1_t2/2+fp_d+fp_r, -E1_t2/2+fp_d+fp_r, sphere_z)). \
             sphere(sphere_r)
    case = case.cut(sphere)

    # calculated dimensions for pin
    R1_o = R1+c # pin upper corner, outer radius
    R2_o = R2+c # pin lower corner, outer radius

    # Create a pin object at the center of top side.
    bpin = cq.Workplane("YZ", (0,E1/2,0)). \
        moveTo(-tb_s, A1+A2_b). \
        line(S+tb_s, 0). \
        threePointArc((S+R1/sqrt(2), A1+A2_b-R1*(1-1/sqrt(2))),
                      (S+R1, A1+A2_b-R1)). \
        line(0, -(A1+A2_b-R1-R2_o)). \
        threePointArc((S+R1+R2_o*(1-1/sqrt(2)), R2_o*(1-1/sqrt(2))),
                      (S+R1+R2_o, 0)). \
        line(L-R2_o, 0). \
        line(0, c). \
        line(-(L-R2_o), 0). \
        threePointArc((S+R1+R2_o-R2/sqrt(2), c+R2*(1-1/sqrt(2))),
                      (S+R1+R2_o-R1, c+R2)). \
        lineTo(S+R1+c, A1+A2_b-R1). \
        threePointArc((S+R1_o/sqrt(2), A1+A2_b+c-R1_o*(1-1/sqrt(2))),
                      (S, A1+A2_b+c)). \
        line(-S-tb_s, 0).close().extrude(b).translate((-b/2,0,0))

    pins = []
    # create top, bottom side pins
    first_pos = -(npx-1)*e/2
    for i in range(npx):
        pin = bpin.translate((first_pos+i*e, 0, 0))
        pins.append(pin)
        pin = bpin.translate((first_pos+i*e, 0, 0)).\
              rotate((0,0,0), (0,0,1), 180)
        pins.append(pin)

    # create right, left side pins
    first_pos = -(npy-1)*e/2
    for i in range(npy):
        pin = bpin.translate((first_pos+i*e, (D1-E1)/2, 0)).\
              rotate((0,0,0), (0,0,1), 90)
        pins.append(pin)
        pin = bpin.translate((first_pos+i*e, (D1-E1)/2, 0)).\
              rotate((0,0,0), (0,0,1), 270)
        pins.append(pin)

    # create exposed thermal pad if requested
    if params.epad:
        pins.append(cq.Workplane("XY").box(D2, E2, A1).translate((0,0,A1/2)))

    # merge all pins to a single object
    merged_pins = pins[0]
    for p in pins[1:]:
        merged_pins = merged_pins.union(p)
    pins = merged_pins

    # extract pins from case
    case = case.cut(pins)

    return (case, pins)


def run():  # unused
    FreeCAD.Console.PrintMessage('\r\nRun Called...\r\n')
    # get variant names from command line
    ## if len(sys.argv) < 2:
    ##     print("No variant name is given!")
    ##     return
    ##
    ## if sys.argv[1] == "all":
    ##     variants = all_params.keys()
    ## else:
    ##     variants = sys.argv[1:]
    ##
    ## outdir = os.path.abspath("./generated_qfp/")
    ## if not os.path.exists(outdir):
    ##     os.makedirs(outdir)
    ##
    ## for variant in variants:
    ##     if not variant in all_params:
    ##         print("Parameters for %s doesn't exist in 'all_params', skipping." % variant)
    ##         continue
    ##     make_one(variant, outdir + ("/qfp_%s.x3d" % variant))



if __name__ == "__main__":
    FreeCAD.Console.PrintMessage('\r\nRunning...\r\n')
# maui     run()
    ## if (not "modelName" in all_params['AKA']):
    ##     ModelName = "newModel" # "LQFP64_p05_h12"
    ## else:
    ##     ModelName = all_params.modelName

    if len(sys.argv) < 3:
        FreeCAD.Console.PrintMessage('No variant name is given! building AKA')
        model_to_build='AKA'
    else:
        model_to_build=sys.argv[2]

    if model_to_build == "all":
        variants = all_params.keys()
    else:
        variants = [model_to_build]

    for variant in variants:
        FreeCAD.Console.PrintMessage('\r\n'+variant)
        if not variant in all_params:
            print("Parameters for %s doesn't exist in 'all_params', skipping." % variant)
            continue
        ModelName = all_params[variant].modelName
        Newdoc = FreeCAD.newDocument(ModelName)
        App.setActiveDocument(ModelName)
        Gui.ActiveDocument=Gui.getDocument(ModelName)
        case, pins = make_gw(all_params[variant])

        color_attr=case_color+(0,)
        show(case, color_attr)
        color_attr=pins_color+(0,)
        show(pins, color_attr)

        doc = FreeCAD.ActiveDocument
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui,
                        doc.Name, objs[0].Name, objs[1].Name)
        doc.Label=ModelName
        objs=GetListOfObjects(FreeCAD, doc)
        objs[0].Label=ModelName
        restore_Main_Tools()
        #rotate if required
        if (all_params[variant].rotation!=0):
            rot= all_params[variant].rotation
            z_RotateObject(doc, rot)
        out_dir=destination_dir+all_params[variant].dest_dir_prefix+'/'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        #out_dir="./generated_qfp/"
        # export STEP model
        exportSTEP(doc,ModelName,out_dir)
        # scale and export Vrml model
        scale=0.3937001
        exportVRML(doc,ModelName,scale,out_dir)
        # Save the doc in Native FC format
        saveFCdoc(App, Gui, doc, ModelName,out_dir)
        #display BBox
        FreeCADGui.ActiveDocument.getObject("Part__Feature").BoundingBox = True
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxometric()
from ast import Assign
from http.client import NOT_FOUND
from tkinter import BOTH
import ifcopenshell
import random
from ifcopenshell.util.selector import Selector
selector = Selector()

#status list given below is common for all the four Ifcs, 
status_list = ['Black&WhiteWallPaint','GypsumSurface','ConcreteSurface','GypsumPlaster','GypsumBoard','GypsumPLaster','CMU', 'Foam','AluminumFrame']

#open Ifc file - for instance _ the second process result
f = ifcopenshell.open("all_insp_added.ifc")
color_palet = []
mm = f.by_type("IfcGeometricRepresentationContext")[0]
for p in range(len(status_list)):
    rgb_i = [random.random(), random.random(), random.random()]
    color_palet.append(rgb_i)

for x in range(1,5,1):
    data_inst = x
    for i in range(len(status_list)):

        material = f.createIfcMaterial("material for {}".format(status_list[i]))
        material_layer = f.createIfcMaterialLayer(material, 200, None)
        material_layer_set = f.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = f.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS3", "POSITIVE", 0.)
        colour_rgb = f.createIfcColourRgb(None, color_palet[i][0], color_palet[i][1], color_palet[i][2])
        surface_style_rendering = f.createIfcSurfaceStyleRendering(colour_rgb, 0., None, None, None, None,None, None,ReflectanceMethod = 'NOTDEFINED')
        surface_style = f.createIfcSurfaceStyle("material for {}".format(status_list[i]), 'BOTH', [surface_style_rendering])
        presentation_style_assignment =  f.createIfcPresentationStyleAssignment([surface_style])
        styled_item = f.createIfcStyledItem(None,[presentation_style_assignment],None)
        styled_representation = f.createIfcStyledRepresentation(mm, 'Style', 'Material', [styled_item])
        material_definition_representation = f.createIfcMaterialDefinitionRepresentation(None, None, [styled_representation],material)

        reln = f.by_type("IfcRelAssignsToControl")
        elements = selector.parse(f, '.IfcTask[Pset_AsIsDataInstance_{0}.ElementConstructionStatus = "{1}"]'.format(data_inst,status_list[i]))

        for j in range(len(reln)):
            for k in range(len(elements)):
                if reln[j][6][0] == elements[k][0]:
                    #if the property attached with an element (from the relationship schema) is similar to the property filterd 
                    
                    element =  reln[j][4][0]
                    #with this condition, element by the GUID - reln[j][4][0][0] carries the property status_list[i]
                    #print("change the color of element GUID {0} to a specific color of {1}".format(element[0], status_list[i]))
                    #from this point i guess it will be specific to the graphic media that is to be used ... 

                    f.get_inverse(element)[13][5] = material_layer_set_usage
                    print(f.get_inverse(element)[13][5])

import multiprocessing
import ifcopenshell
import pandas as pd
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.geolocation
import numpy as np

#ifc_file = ifcopenshell.open('As_planned\ifc2x3_arc_model.ifc')

def extract_xy_verts(ifc):
    try:
        #ifc_file = ifcopenshell.open('As_planned\ifc2x3_arc_model.ifc')
        ifc_file = ifc
    except:
        print(ifcopenshell.get_log())
    else:
        settings = ifcopenshell.geom.settings()
        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
        all_verts = []
        if iterator.initialize():
            while iterator.next():
                shape = iterator.get()
                faces = shape.geometry.faces # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
                verts = shape.geometry.verts # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
                # Since the lists are flattened, you may prefer to group them per face like so depending on your geometry kernel
                grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
                all_verts.append((shape.guid, grouped_verts))

    space_verts = []

    for j in range(0,len(all_verts)):
        if (ifc_file.by_guid('{}'.format(all_verts[j][0])).is_a('IfcSpace')):
            space_verts.append((all_verts[j]))
        else:
            continue

    space_verts_pts = []
    for k in range(0,len(space_verts)): 
        space_verts_p = space_verts[k][1]
        pd_verts = pd.DataFrame(space_verts_p, columns = ['x','y','z'])
        pd_zero_level = pd_verts[pd_verts["z"]==0]
        pd_zero_level.pop("z")
        space_verts_pts.append(pd_zero_level)

    space_verts_csv = []
    for n in range(0,len(space_verts)): 
        space_verts_p = space_verts[n][1]
        pd_verts = pd.DataFrame(space_verts_p, columns = ['x','y','z'])
        pd_zero_csv = pd_verts[pd_verts["z"]==0]
        pd_zero_csv.pop("z")
        pd_zero_array = np.asfarray(pd_zero_csv)
        labeled_array = [space_verts[n][0],pd_zero_array]
        space_verts_csv.append(labeled_array)
    
    #np.savetxt("room_verts.csv", space_verts_csv, fmt='%s')
    
    return space_verts_csv

import open3d as o3d
import numpy as np
import pandas as pd
import pyvista as pv
import cv2
import copy
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import math

#pcd prep 
#vxl = 0.8, to start with for our given leser scanner 
#fltr_no = 100 and std_ratio = 2.0 - if no number is given 

def pcd_prep(pcd, vxl, fltr_no, std_rto):
    downS_cplt_S1 = pcd.voxel_down_sample(voxel_size =vxl)

    def display_inlier_outlier(cloud, ind):
        inlier_cloud = cloud.select_by_index(ind)
        outlier_cloud = cloud.select_by_index(ind, invert=True)

        print("Showing outliers (red) and inliers (gray): ")
        outlier_cloud.paint_uniform_color([1, 0, 0])
        inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
        o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                        zoom=0.3412,
                                        front=[0.4257, -0.2125, -0.8795],
                                        lookat=[2.6172, 2.0475, 1.532],
                                        up=[-0.0694, -0.9768, 0.2024])

    cl, ind = downS_cplt_S1.remove_statistical_outlier(nb_neighbors=fltr_no, std_ratio=std_rto)
 
    ## function to extract floor plan out of a given point cloud, function results in - edges, surface and also saves
    #a scaled floor plan as a plot in the file directory 

def floor_plan_extraction_as_is(pcd_data, a):
    #pcd_data is a point cloud data loaded into open3d, and a is alpha value for pyvisa 3ddelaunay surface
    #reconstruction, angle is - feature angle - use 12 - as default (for this specific example)
    xyz_pcd_df = pd.DataFrame(pcd_data.points, columns = ['x','y','z'])
    xy_view = copy.copy(xyz_pcd_df)
    xy_view.pop("z")
    xy_view.insert(2, 'z', 0)
    xy_view_array = xy_view.to_numpy()
    xy_cloud = pv.PolyData(xy_view_array)
    xy_surf = xy_cloud.delaunay_2d(alpha=a)
    xy_edges = xy_surf.extract_feature_edges(boundary_edges=True,
                           feature_edges=False,
                           manifold_edges=False)
    xy_surf.plot(cpos="xy", show_edges=True)
    xy_p = pv.Plotter()
    xy_p.set_background('white')
    xy_p.add_mesh(xy_edges, color="black", line_width=5)
    xy_p.camera_position = 'xy'
    #xy_p.show(screenshot='pyvisa_export')
    xy_p.save_graphic('export_as_is.svg')
    #plt.imshow(xy_p.image)
    #plt.savefig('origional_rotation.png')
    file_svg = svg2rlg("export_as_is.svg")
   # return file_svg
    renderPM.drawToFile(file_svg, "export_as_is.png", fmt="PNG")
    im = cv2.imread('export_as_is.png')
    img = copy.copy(im)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 200, minLineLength=100, maxLineGap=5)
    angle_ = []
    for [[x1, y1, x2, y2]] in lines:
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angle_.append(angle)
    median_angle = np.median(angle_)
    i=1
    angles_report = []
    while i < 5:
        rot_angle = median_angle-(90*i)
        angles_report.append(rot_angle)
        p = pv.Plotter()
        rot_edges = xy_edges.copy()
        rot_edges.rotate_z(rot_angle)
        p.add_mesh(rot_edges, color="white",line_width=5)
        p.camera_position = "xy"
        p.save_graphic('rotated_position_{}.svg'.format(i))

        file_svg = svg2rlg("rotated_position_{}.svg".format(i))
        renderPM.drawToFile(file_svg, "rotated_position_{}.png".format(i), fmt="PNG")
       # im = cv2.imread('export_as_is.png')
       # p = pv.Plotter()
        #img_rotated = ndimage.rotate(im, rot_angle)
        #cv2.imwrite('rot_image_in2_{}.jpg'.format(i), img_rotated)
        i=i+1 
    return (xy_surf, xy_edges,angles_report, xyz_pcd_df)


import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas as pd
import cv2
from pyvista.core.pointset import PolyData
from shapely.geometry import polygon
from final_floorPlanInfo_extract import space_xy_verts


#create directory (temp_dir - in the current directory to save the temporay plots )

current_path = os.getcwd()
temp_dir, temp_mkdir = 'temp_dir/', 'temp_dir'
p_store = os.path.join(current_path,temp_dir).replace(os.sep,'/')
p_mkdir = os.path.join(current_path,temp_mkdir)
path = "{}".format(p_store)
if not os.path.exists(p_mkdir):
  os.mkdir(p_mkdir)
def rotateImage(image, angle):
  center=tuple(np.array(image.shape[0:2])/2)
  rotate_mat = cv2.getRotationMatrix2D(center,angle,1.0)
  return cv2.warpAffine(image, rotate_mat, image.shape[0:2],flags=cv2.INTER_LINEAR)

def search_match(ifc_file, room_template):
  #ifc_file - add the ifc file of the building model for the room search 
  #room_template - room floor plan - approximated from the point cloud 

  verts = space_xy_verts(ifc_file)
  xy_max_marg = [0,0]
  xy_min_marg = [0,0]

  for t in range (0, len(verts)):
    #shaping room sketch per scale 
    vert_t = pd.DataFrame(verts[t][1], columns = ["x","y"])
    x_max, y_max = vert_t["x"].max(), vert_t["y"].max()
    x_min, y_min = vert_t["x"].min(),vert_t["y"].min()
    if x_max > xy_max_marg[0]:
      xy_max_marg[0] = x_max
    if xy_min_marg[0] == 0:
      xy_min_marg[0]= x_min
    elif xy_min_marg[0] > x_min:
      xy_min_marg[0]= x_min
    if y_max > xy_max_marg[1]:
      xy_max_marg[1] = y_max
    if xy_min_marg[1] == 0:
      xy_min_marg[1]= y_min
    elif xy_min_marg[1] > y_min:
      xy_min_marg[1]= y_min

  for v in range(0, len(verts)):
    # itrate within all rooms, plot the shapes and save the sapes with the room GUIDs
    vert_i = pd.DataFrame(verts[v][1], columns = ["x","y"])
    cnt = vert_i.shape[0]-1
    xx=[vert_i.iat[0,0],vert_i.iat[cnt,0]]
    yy=[vert_i.iat[0,1],vert_i.iat[cnt,1]]
    plt.plot(vert_i["x"],vert_i["y"], color = 'k', linewidth = 5)
    plt.plot(xx,yy, color = 'k', linewidth = 5)
    plt.axis('off')
    plt.tight_layout()
    plt.axis([xy_min_marg[0],xy_max_marg[0], xy_min_marg[1],xy_max_marg[1]])
    plt.savefig(path+"{}".format(verts[v][0]))
    plt.clf()

  # load the image image, convert it to grayscale and detect edges
  print("template Image:")
  template = cv2.imread(room_template)
  #template = cv2.imread("export_as_is.png")
  cv2.imshow("image1",template)
  template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
  template = cv2.Canny(template, 50, 200)
  cv2.waitKey(0)

  angle_jump=1

  # loop over all the images to match the template
  for imagePath in glob.glob("temp_dir" +"/*"):
  # load the image, convert it to grayscale, and initialize founf variable
    vertex_image = cv2.imread(imagePath)
    vertex_gray = cv2.cvtColor(vertex_image, cv2.COLOR_BGR2GRAY)
    found = None
    # detect edges in the resized, grayscale image and apply template
    # matching to find the template in the image
    for angl in range(angle_jump,360,angle_jump):
      vertex_edged = cv2.Canny(vertex_gray, 50, 200)
      result = cv2.matchTemplate(vertex_edged, template, cv2.TM_CCOEFF)
      (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
      # print(maxVal)
      # print(maxLoc)
      # print()
      # if we have found a new maximum correlation value, then update
      # the bookkeeping variable
      if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc)
        match_img = vertex_image
        img_name=imagePath
      
      # rotate through all angles  
      vertex_R_image = rotateImage(vertex_image,angl)
      vertex_gray = cv2.cvtColor(vertex_R_image, cv2.COLOR_BGR2GRAY)
      
  # unpack the found variable and display result
  (maxVal, maxLoc) = found
  print("Image that best match with the tempelate:")
  cv2.imshow("image2", match_img)
  cv2.waitKey(0)
  #print()
  #print(maxVal)
  #print('Image Name:')
  #print(img_name)

  #compute area, centroid and angle

  for h in range(0, len(verts)):
    if img_name == verts[h][0]:
      p_centr = pd.DataFrame(verts[h][1], columns=["x", "y"])
      xy_count = len(p_centr.index)
      p_centr_x, p_centr_y = p_centr["x"].sum()/xy_count, p_centr["y"].sum()/xy_count
      shape = polygon(zip(verts["x"],verts["y"]))
      p_area = shape.area
  
  return p_centr_x, p_centr_y, p_area, img_name, angl


   



#example 
#ifc_file = ifcopenshell.open('As_planned\ifc2x3_arc_model.ifc')
#search_match(ifc_file, "export_as_is.png")


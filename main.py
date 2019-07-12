"""
 ----------------------------------------------------
  @Author: tsukasa
  @Affiliation: Waseda University
  @Email: rinsa@suou.waseda.jp
  @Date: 2019-07-11 18:06:50
  @Last Modified by:   tsukasa
  @Last Modified time: 2019-07-13 01:00:06
 ----------------------------------------------------

  Usage:
   python <file_name>.py argvs[1] argvs[2]
  
   argvs[1]  :  path to input .obj
   argvs[2]  :  output directly

"""



import numpy as np
import sys
import os


## my funcs
from bvh.BVH import *
from utils.obj_functions import *
argvs = sys.argv


## config
meshpath = argvs[1]
outpath = argvs[2]


## return bbox information from bvh node
def create_box(nodelist):

  botleft = nodelist.aabb.botleft
  topright = nodelist.aabb.topright
  vertex = np.zeros((8, 3), dtype=np.float32)
  vertex[0] = botleft
  vertex[1] = [botleft[0], topright[1], botleft[2]]
  vertex[2] = [topright[0], topright[1], botleft[2]]
  vertex[3] = [topright[0], botleft[1], botleft[2]]
  vertex[4] = [botleft[0], botleft[1], topright[2]]
  vertex[5] = [botleft[0], topright[1], topright[2]]
  vertex[6] = topright
  vertex[7] = [topright[0], botleft[1], topright[2]]


  face = np.array([[0, 4, 1],
                   [1, 4, 5],
                   [4, 7, 5],
                   [5, 7, 6],
                   [3, 7, 6],
                   [2, 3, 6],
                   [0, 2, 3],
                   [0 ,1, 2],
                   [1, 6, 2],
                   [1, 5, 6],
                   [0, 7, 4],
                   [0, 3, 7]])

  return vertex, face




## save all each bvh bbox as .obj file
def save_all_bbox(bvhnodelist):
      
  num = 0
  for i in bvhnodelist:
    ver, tri = create_box(i)
    writeobj(os.path.join(outpath, "{}.obj".format(num)), ver, tri)
    num += 1







## save each bvh layer's bbox as one .obj file
def save_each_layer(bvhnodelist):

  ## first layer
  layer = 0
  print("layer:{}".format(layer))
  layer_v, layer_f = create_box(bvhnodelist[0])
  writeobj(os.path.join(outpath, "layer_{}.obj".format(layer)), layer_v, layer_f)
  list = [0]
  layer += 1


  ## func for get child node
  def return_child(node, list):
    new_list = []

    for i in list:
      child1 = node[i].child1
      child2 = node[i].child2

      if(child1 != -1):
        new_list.append(child1)
      if(child2 != -1):
        new_list.append(child2)
      if(child1 == -1 and child2 == -1):
        new_list.append(i)

    return new_list




  ## create new mesh for each layer
  prev = -1
  while len(return_child(bvhnodelist, list)) != prev:
    print("layer:{}".format(layer))

    # update node list
    list = return_child(bvhnodelist, list)
    for i, index in enumerate(list):

      temp_v, temp_f = create_box(bvhnodelist[index])
      if(i == 0):
        layer_v = temp_v
        layer_f = temp_f
      else:
        layer_v = np.vstack((layer_v, temp_v))
        layer_f = np.vstack((layer_f, temp_f+(8*i)))

    writeobj(os.path.join(outpath, "layer_{}.obj".format(layer)), layer_v, layer_f)
    print(len(list))
    prev = len(list)
    layer += 1



def main():

  print("1. loading mesh... ")
  vertices, triangles = loadobj(meshpath)
  face_normals, vertices_normals = compute_normal(vertices, triangles)
  print("done")


  print("2. building BVH... ")
  vertices_bvh = np.copy(vertices[triangles.ravel()])
  vertices_bvh_normals = np.copy(vertices_normals[triangles.ravel()])
  root = buildBVH(vertices_bvh.reshape((-1, 3, 3)), 
                  vertices_bvh_normals.reshape((-1, 3, 3)), 
                  np.array(range(triangles.shape[0])))
  print("done")

  
  print("3. Serializing bvh nodes... ")
  bvhnodelist, bvhtrilist, bvhnormallist, bvhtriindlist = BVHserializer(root)
  np.savez(os.path.join(outpath, "{}_precomp.npz".format(os.path.basename(meshpath))), 
                        vertices=vertices,
                        triangles=triangles,
                        vertices_bvh=vertices_bvh,
                        bvhnodelist=bvhnodelist,
                        bvhtrilist=bvhtrilist,
                        bvhtriindlist=bvhtriindlist,
                        bvhnormallist=bvhnormallist)
  print("done")



  ## save all bbox
  # save_all_bbox(bvhnodelist)
  save_each_layer(bvhnodelist)





if __name__ == '__main__':
  main()
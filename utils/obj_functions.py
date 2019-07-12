"""
 ----------------------------------------------------
  @Author: tsukasa
  @Affiliation: Waseda University
  @Email: rinsa@suou.waseda.jp
  @Date: 2019-06-03 15:17:55
  @Last Modified by:   tsukasa
  @Last Modified time: 2019-07-12 20:29:01
 ----------------------------------------------------


"""


import numpy as np
import torch
import math


def loadobj(path):
  vertices = []
  #texcoords = []
  triangles = []
  normals = []

  with open(path, 'r') as f:
    for line in f:
      if line[0] == '#':
        continue

      pieces = line.split(' ')

      if pieces[0] == 'v':
        vertices.append([float(x) for x in pieces[1:4]])      
      # elif pieces[0] == 'vt':
      #   texcoords.append([float(x) for x in pieces[1:]])
      elif pieces[0] == 'f':
        if pieces[1] == '':
            triangles.append([int(x.split('/')[0]) - 1 for x in pieces[2:]])
        else: 
            triangles.append([int(x.split('/')[0]) - 1 for x in pieces[1:]])
      elif pieces[0] == 'vn':
        normals.append([float(x) for x in pieces[1:]])
      else:
        pass

  return (np.array(vertices, dtype=np.float32),
            #np.array(texcoords, dtype=np.float32),
            np.array(triangles, dtype=np.int32))#,
            # np.array(normals, dtype=np.float32))




def writeobj(filepath, vertices, triangles):
  with open(filepath, "w") as f:
    for i in range(vertices.shape[0]):
      f.write("v {} {} {}\n".format(vertices[i, 0], vertices[i, 1], vertices[i, 2]))
    for i in range(triangles.shape[0]):
      f.write("f {} {} {}\n".format(triangles[i, 0] + 1, triangles[i, 1] + 1, triangles[i, 2] + 1))





def compute_normal(vertices, indices):
  '''
  Compute vertex normal: Nelson Max's method
  see here: "Weights for Computing Vertex Normals from Facet Normals"
  '''
  eps = 1e-10
  fn = np.zeros(indices.shape, dtype=np.float32)
  vn = np.zeros(vertices.shape, dtype=np.float32)
  v = [vertices[indices[:, 0], :],
       vertices[indices[:, 1], :],
       vertices[indices[:, 2], :]]

  ## loop for adjacent vertices
  ## this code assume triangle mesh
  ## f(v0, v1, v2)
  for i in range(3):
    v0 = v[i]
    v1 = v[(i + 1) % 3]
    v2 = v[(i + 2) % 3]
    e1 = v1 - v0
    e2 = v2 - v0
    e1_len = np.linalg.norm(e1, axis=-1)
    e2_len = np.linalg.norm(e2, axis=-1)
    side_a = e1 / (np.reshape(e1_len, (-1, 1)) + eps)
    side_b = e2 / (np.reshape(e2_len, (-1, 1)) + eps)


    ## compute face normal
    if(i == 0):
      fn = np.cross(side_a, side_b)
      fn = fn / (np.reshape(np.linalg.norm(fn, axis=-1), (-1, 1)) + eps)
      # fn = n


    ## comput angle between 2 edge
    angle = np.where(np.sum(side_a *side_b, axis=-1) < 0,
                    np.pi - 2.0 * np.arcsin(np.around(0.5 * np.linalg.norm(side_a + side_b, axis=-1))),
                    2.0 * np.arcsin(np.around(0.5 * np.linalg.norm(side_b - side_a, axis=-1))))
    sin_angle = np.sin(angle)


    ## compute weight, and re-compute normal
    contrib = fn * np.reshape(sin_angle / ((e1_len * e2_len) + eps), (-1, 1))
    index = indices[:, i]

    ## add as vertex normal
    for i in range(index.shape[0]):
      vn[index[i], :] += contrib[i, :]


  ## normalize
  vn = vn / (np.reshape(np.linalg.norm(vn, axis=-1), (-1, 1)) + eps)

  return fn, vn






def loadfp(path):
  fp = []
  
  with open(path, 'r') as f:
    for line in f:
      fp.append(line)
      
  return np.array(fp, dtype=np.int32)
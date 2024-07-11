#!/usr/bin/env python3

from deepface import DeepFace

dfs = DeepFace.find(
  img_path = "img.webp", 
  db_path = "./dest", 
  # detector_backend = 'VGG-Face',
  align = True,
)
print(dfs)
# for f in dfs:
#   print(f.identity.to_frame())
  # print(f.identity[0], f.distance)
  # print(f'{f.identity}{f.distance}')
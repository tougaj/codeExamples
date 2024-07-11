#!/usr/bin/env python3

from deepface import DeepFace

dfs = DeepFace.find(
  img_path = "img.webp", 
  db_path = "/home/admk7/tugaj/codeExamples/deepFace/dest", 
  # detector_backend = 'VGG-Face',
  align = True,
)
print(dfs)
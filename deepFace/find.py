#!/usr/bin/env python3

import pandas as pd
from deepface import DeepFace

MAX_RESULT_COUNT = 40

dfs = DeepFace.find(
  img_path = "target.png", 
  db_path = "./dest", 
  detector_backend = 'centerface',
  # detector_backend = 'retinaface',
  # model_name = 'VGG-Face',
  align = True,
)

identity = dfs[0].identity.to_list()
distance = dfs[0].distance.to_list()
print(f'\nFound {len(identity)} matches\nPrinting first {MAX_RESULT_COUNT}\n')
for i in range(min(len(identity), MAX_RESULT_COUNT)):
  print(f'{identity[i]}\t{distance[i]}')

#!/usr/bin/env python3

from deepface import DeepFace
import os
import time
from PIL import Image
from pathlib import Path

MIN_SIZE = 50

start_time = time.time()
directory = './repr_faces'
i = 0
file_list = os.listdir(directory)
list_len = len(file_list)
errors_count = 0
result = {}
for filename in file_list:
	if i % 20 == 0:
		print(f'Processing {i+1} from {list_len}')
	# Перевіряємо, чи файл має розширення .jpg
	# if filename.lower().endswith('.jpg'):
	file_path = os.path.join(directory, filename)
	fp = Path(file_path)
	basename = fp.stem
	extension = fp.suffix
	# (not_used, extension) = os.path.splitext(file_path)
	# print(f'Found JPG file: {file_path}')

	face_objs = None
	try:
		face_objs = DeepFace.represent(
			img_path = file_path, 
			detector_backend = 'centerface',
			align = True,
		)
	except:
		errors_count += 1
		print(f'⚠️  No faces detected in {basename}{extension}')
		pass
	# j = 0
	if face_objs:
		result[basename] = face_objs[0]['embedding']
	# if face_objs:
	# 	for face in face_objs:
	# 		# output_path = f'./dest/{basename}_{i}_{j}{extension}'
	# 		output_path = f'./dest/{basename}_{j}{extension}'
	# 		crop_face(file_path, face['facial_area'], output_path)
	# 		# print(face['facial_area'])
	# 		j += 1
	i += 1

print(result)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"🏁 Elapsed time: {elapsed_time:.4f} seconds with {errors_count} error")

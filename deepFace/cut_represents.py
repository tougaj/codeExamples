#!/usr/bin/env python3

from deepface import DeepFace
import os
import time
from PIL import Image
from pathlib import Path
import json

MIN_SIZE = 50
RECORDS_PER_FILE = 500

def save_data(data, file_no):
	with open(f'repr_faces_{file_no:02d}.json', 'w') as json_file:
	    json.dump(result, json_file, indent=2)  # Параметр indent дозволяє зробити файл більш читабельним


start_time = time.time()
directory = './dest'
i = 0
file_list = os.listdir(directory)
list_len = len(file_list)
errors_count = 0
result = []
file_no = 0
for filename in file_list:
	if i % 5 == 0:
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
			# detector_backend = 'centerface',
			detector_backend = 'yolov8',
			align = True,
		)
	except:
		errors_count += 1
		print(f'⚠️  No faces detected in {basename}{extension}')
		pass
	# j = 0
	if face_objs:
		result.append({'id': basename, 'face': face_objs[0]['embedding']})
	i += 1
	if i % RECORDS_PER_FILE == 0:
		save_data(result, file_no)
		result = [];
		file_no += 1

if len(result) != 0:
	save_data(result, file_no)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"🏁 Elapsed time: {elapsed_time:.4f} seconds with {errors_count} error")

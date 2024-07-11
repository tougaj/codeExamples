#!/usr/bin/env python3

from deepface import DeepFace
import os
import time
from PIL import Image
from pathlib import Path

def crop_face(img_path, face_data, output_path):
	"""
	Вирізає обличчя з зображення на основі координат і зберігає його в окремий файл.

	:param img_path: Шлях до зображення.
	:param face_data: Словник з даними про обличчя.
	:param output_path: Шлях до вихідного файлу.
	"""
	# Завантаження зображення
	image = Image.open(img_path)

	# Отримання координат обличчя
	x = face_data['x']
	y = face_data['y']
	w = face_data['w']
	h = face_data['h']

	# Обчислення координат для вирізання
	left = x
	top = y
	right = x + w
	bottom = y + h

	# Вирізання обличчя
	face_image = image.crop((left, top, right, bottom))

	# Збереження вирізаного обличчя
	try:
		face_image.save(output_path)
	except:
		print(f'Error saving to {output_path}')
		pass
	# print(f"Face image saved to {output_path}")


start_time = time.time()
directory = './source'
i = 0
file_list = os.listdir(directory)
list_len = len(file_list)
errors_count = 0
for filename in file_list:
	print(f'Processing {i} from {list_len}')
	# Перевіряємо, чи файл має розширення .jpg
	# if filename.lower().endswith('.jpg'):
	file_path = os.path.join(directory, filename)
	fp = Path(file_path)
	basename = fp.stem
	extension = fp.suffix
	# (not_used, extension) = os.path.splitext(file_path)
	# print(f'Found JPG file: {file_path}')

	try:
		face_objs = DeepFace.extract_faces(
			img_path = file_path, 
			detector_backend = 'centerface',
			align = True,
		)
	except:
		errors_count += 1
		print(f'Error by processing {basename}{extension}')
		pass
	j = 0
	if face_objs:
		for face in face_objs:
			output_path = f'./dest/{basename}_{i}_{j}{extension}'
			crop_face(file_path, face['facial_area'], output_path)
			# print(face['facial_area'])
			j += 1
	i += 1

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds with {errors_count} error")

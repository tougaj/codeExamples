#!/usr/bin/env python3

import time
from argparse import ArgumentParser
from pathlib import Path

from deepface import DeepFace
from PIL import Image


def create_errors_dir(path: Path):
    """
    The function `create_errors_dir` checks if a directory named ERROR_DIR exists
    and creates it if it does not.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def crop_face(img_path: Path, face_data: str, output_path: Path, min_size: int):
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
    if max(w, h) < min_size:
        print(f'⚠️  Face is to small {w}x{h}')
        return

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
    except Exception as e:
        print(f'⚠️  Error saving to {output_path}: {e}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-z", "--size", type=int,
                        default=50, help="Image min size")
    parser.add_argument("-s", "--source", type=str,
                        default='./images', help="Images source directory")
    parser.add_argument("-d", "--destination", type=str,
                        default='./faces', help="Faces destination directory")
    parser.add_argument("-e", "--errors", type=str,
                        default='./errors', help="Errors directory")
    args = parser.parse_args()
    MIN_SIZE = args.size
    SOURCE_DIRECTORY = Path(args.source)
    DESTINATION_DIR = Path(args.destination)
    ERROR_DIR = Path(args.errors)

    create_errors_dir(ERROR_DIR)
    start_time = time.time()
    counter = 0
    file_list = [file for file in SOURCE_DIRECTORY.iterdir()
                 if file.is_file()]
    list_len = len(file_list)
    errors_count = 0
    for file_path in file_list:
        if counter % 20 == 0:
            print(f'Processing {counter+1} from {list_len}')
        # Перевіряємо, чи файл має розширення .jpg
        # if filename.lower().endswith('.jpg'):
        # file_path = SOURCE_DIRECTORY / input_file_name
        base_name = file_path.stem
        extension = file_path.suffix
        # (not_used, extension) = os.path.splitext(file_path)
        # print(f'Found JPG file: {file_path}')

        face_objs = None
        try:
            face_objs = DeepFace.extract_faces(
                img_path=file_path,
                detector_backend='centerface',
                align=True,
            )
        except Exception as e:
            errors_count += 1
            file_name = f'{base_name}{extension}'
            file_path.rename(ERROR_DIR / f'{file_name}')
            print(f'⚠️  No faces detected in {file_name}. Moved to errors')
        face_no = 0
        if face_objs:
            for face in face_objs:
                out_path = DESTINATION_DIR / \
                    f'{base_name}_{face_no}{extension}'
                crop_face(
                    img_path=file_path,
                    face_data=face['facial_area'],
                    output_path=out_path,
                    min_size=MIN_SIZE
                )
                # print(face['facial_area'])
                face_no += 1
        counter += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"🏁 Elapsed time: {elapsed_time:.4f} seconds with {errors_count} error")

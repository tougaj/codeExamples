#!/usr/bin/env python3
"""Скрипт демонструє використання черги та багатопоточності
"""

import queue
import subprocess
from threading import Thread
from time import sleep

q = queue.Queue()

def process_item(item: str):
    """Процедура обробки елемента

    Args:
        item (string): елемент
    """
    command = ['./prog.sh', item]
    print(f'🔶 Before process {item}')
    subprocess.run(command, check=True)
    print(f'🔷 After process {item}')

def worker():
    """Функція треду обробки елементів
    """
    while True:
        item = q.get()
        process_item(item)
        q.task_done()

def inserter():
    """Функція треду вставки елементів
    """
    item_no = 0
    while True:
        q.put(f'new_{item_no}')
        print(f'➕ Inserted into queue new_{item_no}')
        item_no += 1
        sleep(10)

def main():
    """Основна функція програми
    """
    # Turn-on the worker thread.
    for i in range(5):
        Thread(target=worker, daemon=True).start()

    # Send thirty task requests to the worker.
    for item in range(30):
        q.put(f'{item}')

    Thread(target=inserter, daemon=True).start()

    # Block until all tasks are done.
    q.join()
    print('🏁 All work completed')

if __name__ == '__main__':
    main()

from copy import copy
from distutils.file_util import copy_file
from hashlib import new
from locale import currency
import numbers
from re import sub
import docker
import tarfile
import subprocess
import time
from datetime import datetime
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import re

class NewFileHandler(FileSystemEventHandler):
	def __init__(self, output_file):
		self.output_file = output_file
		self.task_start_time = 0.0
		self.log_paths = []
	
	def on_created(self, event):
		if not event.is_directory:
			current_time = int(time.time())
			if self.task_start_time == 0.0:
				self.task_start_time = current_time
			if current_time == self.task_start_time:
				self.log_paths.append(event.src_path)
			print(f"New file created: {event.src_path}")
			new_file_path = event.src_path
			file_name = os.path.basename(new_file_path)
			output_file_path = os.path.join(self.output_file, file_name)
			shutil.copy(new_file_path, output_file_path)

def monitor_folder(source_folder, target_folder, output_floder):
	event_handler = NewFileHandler(output_floder)
	observer = Observer()
	observer.schedule(event_handler, target_folder, recursive=False)
	observer.start()
	print(f"Monitoring folder: {target_folder}")
	# subprocess.run(f"rm -rf {target_folder}/**", shell=True)
	# subprocess.run(f"cp -r {source_folder}/** {target_folder}", shell=True)
	# copy_files_from_floder(source_folder,target_floder)

	try:
		while True:
			if event_handler.task_start_time != 0.0:
				event_handler.task_start_time = 0.0
				numbers = re.findall(r'\d+', event_handler.log_paths[0])
				list_size = len(numbers)
				year = int(numbers[list_size-1][:4])
				mouth = int(numbers[list_size-1][4:6])
				day = int(numbers[list_size-1][6:8])
				hour = int(numbers[list_size-1][8:10])
				minute = int(numbers[list_size-1][10:12])
				second = int(numbers[list_size-1][12:14])
				date = datetime(year, mouth, day, hour, minute, second)
				date_str1 = date.strftime("%Y-%m-%d")
				date_str2 = date.strftime("%H:%M:%S")
				print("first_log_time:"+date_str1+' '+date_str2)
				task_name = "task"+'_'+date_str1+'_'+date_str2
				os.makedirs(output_floder+'/'+task_name)
				# 移动文件到子文件夹中
				for log_path in event_handler.log_paths:
					log_name = os.path.basename(log_path)
					log_copy_path = output_floder+'/'+log_name
					if os.path.isfile(log_copy_path):
						shutil.move(log_copy_path, output_floder+'/'+task_name)
				event_handler.log_paths.clear()
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

def copy_files_from_floder(source_folder, target_folder):
	subprocess.run(f"rm -rf {target_folder}/**", shell=True)
	subprocess.run(f"cp -r {source_folder} {target_folder}", shell=True)


def get_container_id_by_name(container_name):
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if container.name == container_name:
            return container.id
    return None

def copy_folder_from_docker(container_id, source_path, target_path):
    command = f'docker cp {container_id}:{source_path} {target_path}'
    subprocess.run(command, shell=True)

def copy_folder_from_docker_by_name(container_name, source_path, target_path):
	client = docker.from_env()
	containers = client.containers.list()
	container_id = None
	for container in containers:
		if container.name == container_name:
			container_id = container.id
			break
	if not container_id:
		command = f'docker cp {container_id}:{source_path} {target_path}'
		subprocess.run(command, shell=True)
		return container_id
	else:
		print("docker name:"+container_name+"not exist")
		return None

def monitor_docker_folder(container_id, source_folder, destination_folder):
    client = docker.from_env()
    container = client.containers.get(container_id)

    # 获取容器中的文件夹路径
    container_folder = os.path.join(container.attrs['GraphDriver']['Data']['MergedDir'], source_folder)

    # 创建目标文件夹
    os.makedirs(destination_folder, exist_ok=True)

    # 获取容器中的文件夹中的所有文件
    existing_files = set(os.listdir(container_folder))

    while True:
        # 获取容器中的文件夹中的所有文件
        current_files = set(os.listdir(container_folder))

        # 计算新增文件
        new_files = current_files - existing_files

        # 将新增文件复制到目标文件夹
        for file in new_files:
            src_path = os.path.join(container_folder, file)
            dest_path = os.path.join(destination_folder, file)
            shutil.copy(src_path, dest_path)

        # 更新已存在文件列表
        existing_files = current_files

        # 等待一段时间后再次检查
        time.sleep(1)	

source_folder = "/home/kzb/python_demo/docker_log"
target_folder = "/home/kzb/python_demo/log"
target_copy_folder = "/home/kzb/python_demo/log_copy"

# 使用 shell 命令拷贝文件夹
# subprocess.run(f"cp -r {source_folder} {target_folder}", shell=True)
def main():
	print("simone")
	monitor_folder(source_folder, target_folder, target_copy_folder)

if __name__ == "__main__":
	main()

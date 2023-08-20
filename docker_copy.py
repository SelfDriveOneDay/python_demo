import docker
import os
import shutil
import time

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

# 使用示例
container_id = 'your_container_id'
source_folder = '/path/to/source/folder'
destination_folder = '/path/to/destination/folder'

monitor_docker_folder(container_id, source_folder, destination_folder)
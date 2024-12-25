# 获取当前文件的绝对路径
import os

current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 构建CSS文件的完整路径
pictures_file_path = os.path.join(current_directory, "pictures")
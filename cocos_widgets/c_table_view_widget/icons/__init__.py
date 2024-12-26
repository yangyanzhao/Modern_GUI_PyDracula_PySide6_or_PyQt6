import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 路径拼接
# os.path.join(current_directory, "xxx")

# 创建一个字典来存储文件路径
icons = {}

# 遍历文件夹中的所有文件
for filename in os.listdir(current_directory):
    if filename.endswith('.png') or filename.endswith('.svg'):
        # 获取文件的完整路径
        file_path = os.path.join(current_directory, filename)
        # 将文件路径存储在字典中，键为文件名
        icons[filename] = file_path

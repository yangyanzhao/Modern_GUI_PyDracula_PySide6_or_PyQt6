# 自定义控件
# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

from .custom_grips import CustomGrip
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file_path)
# 获取当前文件所在目录的父级目录
parent_directory = os.path.dirname(current_directory)
# 获取当前文件所在目录的爷爷级别目录
grandparent_directory = os.path.dirname(parent_directory)
# 获取当前文件所在目录的曾祖父级别目录
great_grandparent_directory = os.path.dirname(grandparent_directory)
# 路径拼接
# os.path.join(current_directory, "xxx")

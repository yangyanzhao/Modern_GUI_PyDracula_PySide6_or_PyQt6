# 创建或加载数据库，auto_dump=True 表示在每次修改数据时自动持久化到文件。
import os.path

import pickledb

from db.pickle_db import current_directory

pickle = pickledb.load(os.path.join(current_directory, 'pickle_db.json'), auto_dump=True)

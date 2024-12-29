# 去掉以_list结尾的键值对
# 去掉_parent的key
def remove_list_keys(data):
    copy = data.copy()
    if '_parent' in copy:
        del copy['_parent']  # 去除出循环引用
    # 遍历字典的键
    keys_to_remove = []
    for key in copy:
        # 检查键是否以 "_list" 结尾
        if key.endswith("_list"):
            keys_to_remove.append(key)
        if key.endswith("_checked"):
            keys_to_remove.append(key)

    # 删除以 "_list" 结尾的键值对
    for key in keys_to_remove:
        del copy[key]

    return copy

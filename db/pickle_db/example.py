import pickledb

if __name__ == '__main__':
    # 创建或加载数据库，auto_dump=True 表示在每次修改数据时自动持久化到文件。
    db = pickledb.load('example.json', auto_dump=True)
    # 手动触发持久化
    db.dump()
    # 设置数据
    db.set('username', '张三丰')
    # 获取数据
    value = db.get('username')
    # 获取所有键
    keys: list = db.getall()
    # 检查键是否存在
    exists = db.exists('password')
    if exists:
        # 删除键值对
        db.rem('password')
    # 获取数据库键的数量
    total_count = db.totalkeys()
    # 清空数据库
    db.deldb()
    """---------------------------list-----------------------------"""
    # 存储列表
    db.set('fruits', ['apple', 'banana'])
    # 向列表追加列表
    db.append('fruits', ['cherry'])
    # 创建key为friends的空列表
    db.lcreate("friends")
    # 向列表添加元素
    db.ladd("friends", "lucy")
    # 向列表中插入元素
    db.lextend("friends", ['bob', 'charlie'])
    # 获取列表元素
    friends = db.lgetall('friends')
    # 获取列表中的一个元素
    friend = db.lget('friends', 1)
    # 删除列表中的指定元素
    db.lremvalue('friends', 'bob')
    db.lpop('friends', 0)
    # 删除列表及其所有元素
    # db.lremlist('friends')
    # 获取列表长度
    db.llen('friends')
    # 对列表中的元素进行追加操作，字符串则+=，列表则+=
    db.lappend('friends', 0, 'dave')
    # 判断列表中是否存在某个值
    db.lexists('friends', 'lily')
    """----------------------------dict----------------------------"""
    # 创建key为user的空字典
    db.dcreate('user')
    # 添加一个键值对到字典中
    db.dadd('user', ('name', 'Alice'))
    # 获取字典中的某个键数据
    db.dget('user', 'name')
    # 获取字典中所有的键值对
    db.dgetall('user')
    # 删除字典及其所有元素
    db.drem('user')
    # 删除字典中的某个键
    db.dpop('user', 'name')
    # 获取字典中的所有键
    db.dkeys('user')
    # 获取字典中的所有值
    db.dvals('user')
    # 判断字典中是否存在某个键
    db.dexists('user', 'name')
    # 合并存储两个字典到user1
    db.dmerge('user1', 'user2')
    # 存储字典
    db.set('user', {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'})
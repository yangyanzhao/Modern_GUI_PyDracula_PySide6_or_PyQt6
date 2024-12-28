"""
解析MYSQL的DDL工具类
"""
import re


def parse_ddl(ddl_statement):
    # 定义正则表达式模式
    pattern = re.compile(
        r"""
        \s*`(?P<name>[^`]+)`\s+          # 字段名称，用反引号括起来
        (?P<type>[^\s(]+)(?:\([^)]+\))?\s*  # 字段类型，可能包含括号内的参数
        (?:
            .*?                       # 匹配任意字符，直到遇到注释
            COMMENT\s+'(?P<comment>[^']*)'  # 注释，用单引号括起来
        )?
        """,
        re.VERBOSE | re.IGNORECASE
    )

    # 查找所有匹配的字段定义
    matches = pattern.finditer(ddl_statement)

    # 提取字段名称、类型和注释
    fields = []
    for match in matches:
        name = match.group('name')
        type_ = match.group('type')
        comment = match.group('comment')

        # 如果注释不存在，设置为空字符串
        if comment is None:
            comment = ''

        fields.append({
            'name': name,
            'type': type_,
            'comment': comment
        })

    return fields


if __name__ == '__main__':
    # 示例DDL语句
    ddl_statement = """
    CREATE TABLE `users` (
        `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
        `name` VARCHAR(255) NOT NULL COMMENT '用户名',
        `email` VARCHAR(255) NOT NULL COMMENT '用户邮箱',
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    # 解析DDL语句
    fields = parse_ddl(ddl_statement)

    # 输出结果
    for field in fields:
        print(f"Name: {field['name']}, Type: {field['type']}, Comment: {field['comment']}")

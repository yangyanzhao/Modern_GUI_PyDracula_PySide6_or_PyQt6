import os
import functools
import sys
import logging
import time

"""
日志插件
"""


class Logger(object):
    def __init__(self, filename=None, callback=None, original_stdout=None):
        self.filename = filename
        self.callback = callback
        self.terminal = sys.stdout
        self.in_callback = False  # 添加一个标志，防止递归调用
        self.is_logging = False  # 添加一个标志，区分来自 logging 的输出
        self.original_stdout = original_stdout  # 保存原始的标准输出
        if filename:
            # 检查文件是否存在，如果不存在则创建
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8'):
                    pass
            self.log = open(filename, "a", encoding='utf-8')

    def write(self, message):
        if not self.is_logging:
            self.terminal.write(message)
        if self.filename:
            try:
                self.log.write(message)
                self.log.flush()  # 确保立即写入文件
            except Exception as e:
                print(f"Error writing to log file: {e}")
        if self.callback and not self.in_callback:
            try:
                self.in_callback = True  # 设置标志，防止递归调用
                if self.callback.__code__.co_argcount == 1:
                    self.callback(message)
                else:
                    self.callback(message, self.original_stdout)
            finally:
                self.in_callback = False  # 恢复标志

    def flush(self):
        # 这个 flush 方法是为了兼容性，并不需要实际实现
        pass

    def close(self):
        if self.filename:
            self.log.close()


class CustomLoggingHandler(logging.Handler):
    def __init__(self, logger_instance):
        super().__init__()
        self.logger_instance = logger_instance

    def emit(self, record):
        try:
            self.logger_instance.is_logging = True  # 设置标志，表示来自 logging 的输出
            msg = self.format(record)
            self.logger_instance.write(msg + '\n')
        except Exception:
            self.handleError(record)
        finally:
            self.logger_instance.is_logging = False  # 恢复标志


def redirect_output(filename=None, callback=None):
    """
    filename 记录文件地址
    callback 北向回调
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 保存原始的标准输出和标准错误
            original_stdout = sys.stdout
            original_stderr = sys.stderr

            # 重定向标准输出和标准错误到自定义的 Logger 类
            logger_instance = Logger(filename, callback, original_stdout)
            sys.stdout = logger_instance
            sys.stderr = logger_instance

            # 配置 logging 模块使用自定义的日志处理器
            custom_handler = CustomLoggingHandler(logger_instance)
            logging.getLogger().addHandler(custom_handler)

            try:
                # 执行被装饰的函数
                result = func(*args, **kwargs)
            finally:
                # 关闭文件并恢复原始的标准输出和标准错误
                logger_instance.close()
                sys.stdout = original_stdout
                sys.stderr = original_stderr

                # 移除自定义的日志处理器
                logging.getLogger().removeHandler(custom_handler)

            return result

        return wrapper

    return decorator


class Demo:
    def __init__(self):
        pass

    @redirect_output(filename='test.log', callback=lambda msg: print(f"【{msg}】"))
    def do(self):
        for i in range(10):
            print(10)
            time.sleep(1)


if __name__ == '__main__':
    demo = Demo()
    demo.do()

import os
import sys

"""
程序开机自启
"""


class StartupManager:
    """
    开机启动管理器
    """
    bat_name = "startup"

    @staticmethod
    def check_startup_status():
        """
        检测开机自启状态
        :return:
        """
        bat_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                                f'{StartupManager.bat_name}.bat')
        if os.path.exists(bat_path):
            return True
        else:
            return False

    @staticmethod
    def add_to_startup():
        """
        开启开机自启
        :return:
        """
        executable_path = sys.executable
        executable_name = os.path.basename(executable_path)
        file_path = os.path.join(os.getcwd(), f"{executable_name}")
        bat_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                                f'{StartupManager.bat_name}.bat')
        print(bat_path)
        with open(bat_path, "w+") as bat_file:
            bat_file.write(r'start "" "%s"' % file_path)

    @staticmethod
    def remove_from_startup():
        """
        移除开机自启
        :return:
        """
        bat_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
                                f'{StartupManager.bat_name}.bat')
        print(bat_path)
        if os.path.exists(bat_path):
            os.remove(bat_path)


if __name__ == '__main__':
    status = StartupManager.check_startup_status()
    print(status)
    StartupManager.remove_from_startup()
    # manager.add_to_startup()

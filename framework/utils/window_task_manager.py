import os
import sys

import comtypes
import pythoncom
import win32timezone
import win32com.client
from win32com.client.dynamic import CDispatch


# 创建关机任务
def create_shutdown_task(time, task_name):
    try:
        # 确保在每个线程中初始化 COM 库
        comtypes.CoInitialize()

        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        task_def = scheduler.NewTask(0)

        # 创建触发器
        trigger = task_def.Triggers.Create(2)  # 2 表示每天触发器
        trigger.StartBoundary = time  # 设置触发时间
        trigger.DaysInterval = 1  # 每天触发

        # 创建操作
        action = task_def.Actions.Create(0)  # 0 表示执行命令
        action.ID = 'ShutdownAction'
        action.Path = 'shutdown'
        action.Arguments = '/s /t 180 /c "该计算机将在 3 分钟后关闭。请保存您的工作并退出程序。"'  # /s 表示关机，/t 0 表示立即关机

        # 注册任务
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6,  # 6 表示创建或覆盖任务
            '',  # 用户名
            '',  # 密码
            0  # 0 表示交互式任务
        )
    finally:
        comtypes.CoUninitialize()


# 创建重启任务
def create_startup_task(time, task_name):
    try:
        # 确保在每个线程中初始化 COM 库
        comtypes.CoInitialize()

        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        task_def = scheduler.NewTask(0)

        # 创建触发器
        trigger = task_def.Triggers.Create(2)  # 2 表示每天触发器
        trigger.StartBoundary = time  # 设置触发时间
        trigger.DaysInterval = 1  # 每天触发

        # 创建操作
        action = task_def.Actions.Create(0)  # 0 表示执行命令
        action.ID = 'StartupAction'
        action.Path = 'shutdown'
        action.Arguments = '/r /t 180 /c "该计算机将在 3 分钟后重启。请保存您的工作并退出程序。"'  # /r 表示重启，/t 0 表示立即重启

        # 注册任务
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6,  # 6 表示创建或覆盖任务
            '',  # 用户名
            '',  # 密码
            0  # 0 表示交互式任务
        )
    finally:
        comtypes.CoUninitialize()


# 创建定时启动当前程序的任务
def create_startup_current_program_task(time, task_name):
    try:
        # 确保在每个线程中初始化 COM 库
        comtypes.CoInitialize()
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        task_def = scheduler.NewTask(0)

        # 创建触发器
        trigger = task_def.Triggers.Create(2)  # 2 表示每天触发器
        trigger.StartBoundary = time  # 设置触发时间
        trigger.DaysInterval = 1  # 每天触发

        # 创建操作
        action = task_def.Actions.Create(0)  # 0 表示执行命令
        action.ID = 'StartupCurrentProgramAction'
        executable_path = sys.executable
        executable_name = os.path.basename(executable_path)
        action.Path = os.path.join(os.getcwd(), f"{executable_name}")
        action.Arguments = ''  # 如果需要传递参数，可以在这里设置

        # 注册任务
        root_folder.RegisterTaskDefinition(
            task_name,
            task_def,
            6,  # 6 表示创建或覆盖任务
            '',  # 用户名
            '',  # 密码
            0  # 0 表示交互式任务
        )
    finally:
        comtypes.CoUninitialize()


# 删除任务
def delete_task(task_name):
    try:
        # 确保在每个线程中初始化 COM 库
        comtypes.CoInitialize()
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
    finally:
        comtypes.CoUninitialize()

    try:
        root_folder.DeleteTask(task_name, 0)
    except Exception as e:
        print(f"任务 {task_name} 不存在或无法删除: {e}")


def check_task_status(task_name):
    tasks = list_tasks()
    for task in tasks:
        if task.Name == task_name:
            return True
    return False


def get_task_next_run_time(task_name):
    tasks = list_tasks()
    for task in tasks:
        if task.Name == task_name:
            time = task.NextRunTime
            return time


def list_tasks():
    try:
        # 确保在每个线程中初始化 COM 库
        comtypes.CoInitialize()
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder: CDispatch = scheduler.GetFolder('\\')

        tasks = root_folder.GetTasks(0)
    finally:
        comtypes.CoUninitialize()

    # print(f"任务总数: {tasks.Count}")
    # for task in tasks:
    #     print(f"上次运行时间: {task.LastRunTime}")
    #     print(f"上次运行结果: {task.LastTaskResult}")
    #     print(f"任务名称: {task.Name}")
    #     print(f"下次运行时间: {task.NextRunTime}")
    #     print(f"错过的运行次数: {task.NumberOfMissedRuns}")
    #     print(f"任务路径: {task.Path}")
    #     print(f"任务状态: {task.State}")
    #     print(f"任务描述: {task.Definition.RegistrationInfo.Description}")
    #     print("-" * 40)
    return tasks


if __name__ == "__main__":
    # 示例：创建一个每天 23:00 关机的任务
    # create_shutdown_task('DailyShutdown', '2023-10-01T23:00:00')

    # 示例：创建一个每天 07:00 开机的任务
    # create_startup_task('DailyStartup', '2023-10-01T07:00:00')

    # 示例：删除任务
    # delete_task('DailyShutdown')
    # delete_task('DailyStartup')
    # get_task_next_run_time("DailyShutdown")
    # 示例：任务列表
    list_tasks()
    # create_shutdown_task('DailyShutdown', '2023-10-01T23:00:00')

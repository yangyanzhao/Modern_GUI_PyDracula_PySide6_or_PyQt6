import asyncio
import datetime
import os
import random

from playwright.async_api import async_playwright, ElementHandle, Page

from modules.zhihu_auto.plugin_email.email_notice import email_notification


async def screenshot_page(page: ElementHandle,
                          folder_path: str  = None,
                          file_name: str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f') + f'[{random.randint(0, 99999)}]') -> str:
    """
    :param page 页面句柄或者定位器
    :param folder_path 文件夹地址
    :param file_name 文件名称
    """
    screenshot_path = f'{file_name}_element.png'
    if isinstance(page, ElementHandle):
        if folder_path:
            screenshot_path = os.path.join(folder_path, f'{file_name}_element.png')
        await page.screenshot(path=screenshot_path)
    elif isinstance(page, Page):
        if folder_path:
            screenshot_path = os.path.join(folder_path, f'{file_name}_page.png')
        await page.screenshot(path=screenshot_path, full_page=True)
    else:
        if folder_path:
            screenshot_path = os.path.join(folder_path, f'{file_name}_element.png')
        await page.screenshot(path=screenshot_path)
    return screenshot_path


# 使用示例
async def main():
    async def start_chrome():
        command = r'"C:\Users\Lenovo\AppData\Local\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9998 --user-data-dir=D:/chrome_user_data/15925828527 --window-position=10000,10000 --start-maximized'
        process = await asyncio.create_subprocess_shell(command)
        return process

    # 启动 Chrome
    chrome_process = await start_chrome()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{9998}")
        content = browser.contexts[0]
        page = await content.new_page()
        await page.goto("https://www.baidu.com", timeout=60 * 1000)
        page_path = await screenshot_page(page=page, file_name=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f'))
        await email_notification(message=f"random_browsing_289行p", image_paths=[page_path])

        await asyncio.sleep(1)
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')
        # 选择要截图的元素（例如百度搜索框）
        element = await page.query_selector('input[name="wd"]')
        element_path = await screenshot_page(page=element,file_name=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f'))
        await email_notification(message=f"random_browsing_289e行", image_paths=[element_path])

        await page.close()
        await content.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())

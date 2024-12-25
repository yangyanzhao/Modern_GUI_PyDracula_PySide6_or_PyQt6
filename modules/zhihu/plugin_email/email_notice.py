import asyncio
import logging
import smtplib
import traceback
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage




async def email_notification(message: str, image_paths: list = None, receiver: str = '854642685@qq.com'):
    """
    发送邮件通知，包含多张图片和文字说明
    """
    try:
        MAIL = {
            "from": '1324355181@qq.com',
            "pwd": 'ikqwkotiaelhjejf',
            "smtp": 'smtp.qq.com',
            "port": 465  # 使用SSL端口为465,非SSL端口为25
        }

        msg = MIMEMultipart('related')
        msg['Subject'] = Header('来遥远星系', 'utf-8')  # 标题
        msg['From'] = MAIL['from']  # 发件人
        msg['To'] = receiver  # 收件人

        # 创建邮件正文
        html_content = f'<p>{message}</p>'
        if image_paths:
            for i, image_path in enumerate(image_paths):
                html_content += f'<p><img src="cid:image{i + 1}"></p>'

        html_message = MIMEText(html_content, 'html', 'utf-8')  # 正文
        msg.attach(html_message)

        if image_paths:
            # 添加多张图片附件
            for i, image_path in enumerate(image_paths):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<image{i + 1}>')
                    msg.attach(img)
        """
        # 非SSL，如果为SSL则看下面
        # server = smtplib.SMTP(MAIL['smtp'])
        # 使用SSL连接SMTP服务器
        """
        # 使用SSL连接SMTP服务器
        server = smtplib.SMTP_SSL(MAIL['smtp'], MAIL['port'])

        # 登陆邮箱发送邮件
        server.login(MAIL['from'], MAIL['pwd'])
        server.sendmail(MAIL['from'], [receiver], msg.as_string())
        logging.info('发送邮件成功')

    except Exception as e:
        logging.error(f"发送邮件失败: {e}")
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    image_paths = [r'D:\pythonwork\pythonauto\test\3.jpeg', r'D:\pythonwork\pythonauto\test\2.jpg',
                   r'D:\pythonwork\pythonauto\test\1.jpg']
    asyncio.run(email_notification('这是多张图片的文字说明', image_paths))

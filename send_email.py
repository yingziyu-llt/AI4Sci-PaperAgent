import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

def send_email_report(subject, content):
    sender = 'linletian1@sina.com'
    receiver = 'yingziyu-lin@outlook.com'
    auth_code = '5f703f9ed3bebbde'

    message = MIMEText(content, 'plain', 'utf-8')

    message['From'] = formataddr((str(Header('每日论文推荐', 'utf-8')), sender))
    message['To'] = receiver
    message['Subject'] = Header(subject, 'utf-8')

    try:
        # 新浪邮箱 SMTP 服务器：smtp.sina.com
        # 如果 465 端口不行，可以尝试 587 (使用 smtp.starttls())
        smtp = smtplib.SMTP_SSL("smtp.sina.com", 465)
        smtp.login(sender, auth_code)
        # 确保这里的 sender 和 message['From'] 里的地址一致
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")



import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from .config import SENDER_EMAIL, AUTH_CODE, RECEIVER_EMAIL
import os
from typing import List, Dict, Any
import httpx  # 确保在文件顶部导入
from .config import ONEBOT_HTTP_URL, ONEBOT_ACCESS_TOKEN, QQ_GROUP_ID


CACHE_FILE = "paper_cache.json"

def load_cache() -> List[str]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f).get("processed_ids", [])
            except:
                return []
    return []

def update_cache(new_ids: List[str]):
    cache = load_cache()
    updated_cache = list(set(cache + new_ids))
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({"processed_ids": updated_cache}, f, indent=2)

def is_new(paper: Dict[str, Any], cache: List[str]) -> bool:
    paper_id = paper.get("doi") or paper.get("id") or paper.get("link")
    return paper_id not in cache


def send_email_notification(subject, content):
    """
    发送邮件通知
    """
    sender = SENDER_EMAIL
    auth_code = AUTH_CODE
    receiver = RECEIVER_EMAIL

    message = MIMEText(content, 'plain', 'utf-8')
    # 修复之前的 553 错误：确保展示名后紧跟正确的邮箱地址
    message['From'] = formataddr((str(Header('科研助手', 'utf-8')), sender))
    message['To'] = receiver
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL("smtp.sina.com", 465)
        smtp.login(sender, auth_code)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


import subprocess
import base64
import httpx
from pdf2image import convert_from_path
from .config import ONEBOT_HTTP_URL, ONEBOT_ACCESS_TOKEN, TEMP_IMAGE_DIR

async def render_md_to_pngs(md_path: str) -> list:
    """
    Render Markdown to multiple PNGs using Pandoc + Typst
    """
    pdf_path = md_path.replace(".md", ".pdf")
    if not os.path.exists(TEMP_IMAGE_DIR):
        os.makedirs(TEMP_IMAGE_DIR)
    
    # 1. Use Pandoc to convert MD to PDF via Typst engine
    subprocess.run([
        "pandoc", md_path, 
        "-o", pdf_path, 
        "--pdf-engine=typst",
        # Optionally add a font setting for Chinese support
        "-V", "mainfont=Source Han Sans" 
    ], check=True)

    # 2. Convert PDF pages to PNG images
    images = convert_from_path(pdf_path)
    png_paths = []
    for i, image in enumerate(images):
        png_path = os.path.join(TEMP_IMAGE_DIR, f"report_page_{i}.png")
        image.save(png_path, "PNG")
        png_paths.append(png_path)
    
    return png_paths

async def send_onebot_img(group_id: int, img_path: str):
    """
    Send a local image via OneBot using Base64
    """
    with open(img_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    url = f"{ONEBOT_HTTP_URL}/send_group_msg"
    headers = {"Authorization": f"Bearer {ONEBOT_ACCESS_TOKEN}"}
    payload = {
        "group_id": group_id,
        "message": f"[CQ:image,file=base64://{img_base64}]"
    }

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)
import os
from typing import Dict, Any

from botpy import BotAPI
from botpy.http import BotHttp

from daily_paper_agent.state import PaperState
from daily_paper_agent.config import QQ_BOT_APPID, QQ_BOT_SECRET, QQ_USER_ID

async def notify_node(state: PaperState) -> Dict[str, Any]:
    print("--- SENDING NOTIFICATION ---")
    report_path = state.get("report_path")
    
    if not report_path or not os.path.exists(report_path):
        print("No report file found to notify.")
        return {"notification_sent": False}
        
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading report: {e}")
        return {"notification_sent": False}

    if not QQ_BOT_APPID or not QQ_BOT_SECRET:
        print("QQ_BOT_APPID or QQ_BOT_SECRET is not set. Skipping QQ bot notification.")
        # If onebot is configured, we could fallback, but user explicitly asked for qq-bot.
        return {"notification_sent": False}

    print(f"Read {len(content)} characters from report. Preparing to send...")

    # Initialize bot API directly
    http = BotHttp(timeout=10, is_sandbox=False, app_id=QQ_BOT_APPID, secret=QQ_BOT_SECRET)
    api = BotAPI(http=http)

    openid = str(QQ_USER_ID)
    
    # QQ bot messages might be limited to around 2000 chars. Let's chunk if necessary or just send.
    max_length = 2000
    chunks = [content[i:i + max_length] for i in range(0, len(content), max_length)]
    
    success = False
    for i, chunk in enumerate(chunks):
        try:
            res = await api.post_c2c_message(
                openid=openid,
                msg_type=0,
                content=chunk
            )
            print(f"Successfully sent message chunk {i+1}/{len(chunks)}")
            success = True
        except Exception as e:
            print(f"Failed to send message chunk {i+1}/{len(chunks)}: {repr(e)}")
            # If the first chunk fails, we might still want to try next or stop. Usually stop.
            break

    return {"notification_sent": success}

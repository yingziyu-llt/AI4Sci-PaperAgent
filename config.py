# Configuration for the Daily Paper Agent
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Settings
# You can use "gemini", "openai", or "placeholder"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "siliconCloud")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini") # or gpt-3.5-turbo

SiliconCloud_API_KEY = os.getenv("SILICONCLOUD_API_KEY", "")
SiliconCloud_MODEL = os.getenv("SILICONCLOUD_MODEL", "Pro/deepseek-ai/DeepSeek-V3.2")
# For Gemini API (if not using CLI)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

# For Vertex AI
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT", "")  # Your GCP Project ID
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
VERTEX_MODEL = os.getenv("VERTEX_MODEL", "gemini-3.1-pro-preview")

# Filtering Settings
MAX_PAPERS_PER_BATCH = 10 # Number of papers to send to LLM in one filtering prompt
MIN_RELEVANCE_SCORE = 6   # 1-10 scale

# Pre-filtering Settings
ENABLE_PRE_FILTER = True
PRE_FILTER_KEYWORD_THRESHOLD = 2 # Number of keywords required to pass the pre-filter

# Output Settings
REPORT_OUTPUT_DIR = "reports"
REPORT_FILENAME_FORMAT = "Daily_Paper_Report_%Y%m%d.md"
DB_PATH = os.getenv("DB_PATH", "papers.db")

# Embedding Settings
# Recommended: BAAI/bge-m3 or BAAI/bge-large-zh-v1.5 on SiliconCloud
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "siliconCloud") 
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", SiliconCloud_API_KEY)
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")
AUTH_CODE = os.getenv("AUTH_CODE", "")

ONEBOT_HTTP_URL = os.getenv("ONEBOT_HTTP_URL", "http://localhost:3000")
ONEBOT_ACCESS_TOKEN = os.getenv("ONEBOT_ACCESS_TOKEN", "")  # 填入你测试成功的 Token
QQ_USER_ID = os.getenv("QQ_USER_ID", "12345678")       # 接收简报的用户QQ/OpenID
TEMP_IMAGE_DIR = os.getenv("TEMP_IMAGE_DIR", "temp_images")

QQ_BOT_APPID = os.getenv("QQ_BOT_APPID", "")
QQ_BOT_SECRET = os.getenv("QQ_BOT_SECRET", "")
import streamlit as st
import os
import sys
import re
import numpy as np
from datetime import datetime

# Ensure the current directory's parent is in sys.path so we can import daily_paper_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from daily_paper_agent.database import save_feedback, get_paper, get_all_feedback

# 配置页面
st.set_page_config(
    page_title="Daily Paper Intelligence Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 样式美化
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMarkdown h1 {
        color: #1f77b4;
        text-align: center;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    .stMarkdown h2 {
        color: #2c3e50;
        border-left: 5px solid #1f77b4;
        padding-left: 10px;
        margin-top: 30px;
    }
    .stMarkdown h3 {
        color: #e67e22;
        background-color: #fdf2e9;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_report_list():
    """获取所有报告文件并按日期降序排列"""
    report_dir = "reports"
    if not os.path.exists(report_dir):
        return []
    
    files = [f for f in os.listdir(report_dir) if f.endswith(".md")]
    reports = []
    for f in files:
        # 匹配 Daily_Paper_Report_YYYYMMDD.md
        match = re.search(r"Daily_Paper_Report_(\d{8})\.md", f)
        if match:
            date_str = match.group(1)
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                reports.append({
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "filename": f,
                    "raw_date": date_str
                })
            except ValueError:
                continue
    
    # 按日期降序排列
    reports.sort(key=lambda x: x["raw_date"], reverse=True)
    return reports

def handle_feedback(paper_id: str, label: int):
    """Handle like/dislike button click."""
    paper = get_paper(paper_id)
    if paper:
        # Convert blob back to numpy if needed
        embedding = np.frombuffer(paper['embedding'], dtype=np.float32) if paper['embedding'] else None
        save_feedback(
            paper_id=paper_id,
            title=paper['title'],
            abstract=paper['abstract'],
            label=label,
            embedding=embedding
        )
        st.success(f"已反馈偏好: {paper['title'][:30]}...")
    else:
        st.error("找不到该论文信息，无法记录反馈。")

def main():
    st.sidebar.title("📚 论文追踪系统")
    st.sidebar.markdown("---")
    
    reports = get_report_list()
    
    if not reports:
        st.error("未找到任何报告文件。请确保 `reports/` 目录下有生成的 Markdown 报告。")
        return

    # 日期选择
    report_dates = [r["date"] for r in reports]
    selected_date_str = st.sidebar.selectbox("选择日期", report_dates)
    
    selected_report = next(r for r in reports if r["date"] == selected_date_str)
    report_path = os.path.join("reports", selected_report["filename"])

    # 显示报告内容
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 侧边栏快速跳转
        st.sidebar.markdown("### 快速导航")
        if "## 🤖 AI 最新进展" in content:
            st.sidebar.markdown("- [AI 最新进展](#ai)")
        if "## 🧬 AI for Science 生物相关进展" in content:
            st.sidebar.markdown("- [AI4S 生物相关进展](#ai4s)")

        # --- 增强的渲染逻辑：支持 Human-in-the-loop ---
        # 简单切分章节或论文
        parts = re.split(r"(?=<!-- paper_id: .*? -->)", content)
        
        # 显示头部 (第一部分通常是标题和统计)
        st.markdown(parts[0], unsafe_allow_html=True)
        
        # 显示带反馈按钮的论文
        for i, part in enumerate(parts[1:]):
            # 提取 paper_id
            match = re.search(r"<!-- paper_id: (.*?) -->", part)
            if match:
                paper_id = match.group(1)
                # 移除注释，渲染 Markdown
                paper_md = re.sub(r"<!-- paper_id: .*? -->", "", part)
                st.markdown(paper_md, unsafe_allow_html=True)
                
                # 添加反馈按钮
                col1, col2, _ = st.columns([1.5, 1.5, 7])
                with col1:
                    if st.button("👍 赞", key=f"like_{paper_id}_{i}"):
                        handle_feedback(paper_id, 1)
                with col2:
                    if st.button("👎 踩", key=f"dislike_{paper_id}_{i}"):
                        handle_feedback(paper_id, -1)
                st.markdown("---")
            else:
                # 兜底：渲染 Markdown
                st.markdown(part, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"读取报告出错: {e}")

    st.sidebar.markdown("---")
    # 显示当前的反馈统计
    feedbacks = get_all_feedback()
    if feedbacks:
        likes = sum(1 for f in feedbacks if f['label'] > 0)
        dislikes = sum(1 for f in feedbacks if f['label'] < 0)
        st.sidebar.metric("积累偏好数据", f"{len(feedbacks)} 篇")
        st.sidebar.text(f"👍 赞: {likes} | 👎 踩: {dislikes}")
    
    st.sidebar.info("已启用演化推荐：系统将基于您的历史偏好自动优化后续文章推荐。")

if __name__ == "__main__":
    main()

import streamlit as st
import os
import re
from datetime import datetime

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
            
        # 侧边栏快速跳转 (通过标题锚点)
        st.sidebar.markdown("### 快速导航")
        if "## 🤖 AI 最新进展" in content:
            st.sidebar.markdown("- [AI 最新进展](#ai)")
        if "## 🧬 AI for Science 生物相关进展" in content:
            st.sidebar.markdown("- [AI4S 生物相关进展](#ai4s)")
        if "## 📚 其他扫描论文" in content:
            st.sidebar.markdown("- [其他扫描论文](#6013e903)")

        # 渲染正文
        st.markdown(content, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"读取报告出错: {e}")

    st.sidebar.markdown("---")
    st.sidebar.info("基于 DeepSeek-R1 驱动的 AI4S 论文追踪系统")

if __name__ == "__main__":
    main()

import asyncio
import os
import sys

# 方案：手动将项目根目录加入路径 (临时解决导入问题)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily_paper_agent.nodes.notify import notify_node

async def test():
    # 验证你提到的文件是否存在
    report_file = "daily_paper_agent/reports/Daily_Paper_Report_20260310.md"
    
    if not os.path.exists(report_file):
        # 尝试绝对路径或相对项目根目录的路径
        report_file = "reports/Daily_Paper_Report_20260310.md"

    if not os.path.exists(report_file):
        print(f"❌ 错误：在预定位置找不到测试文件 {report_file}")
        return

    # 模拟 LangGraph 的状态字典
    state = {
        "report_path": report_file, 
        "bio_papers": [], 
        "ai_papers": []
    }
    
    print(f"🚀 开始测试 notify_node... 使用文件: {report_file}")
    await notify_node(state)
    print("🏁 测试流程结束。")

if __name__ == "__main__":
    asyncio.run(test())
import sys
import os
import asyncio

# Ensure the current directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily_paper_agent.graph import create_graph
from daily_paper_agent.state import PaperState

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,smtp.sina.com'

async def main():
    print("🚀 Starting Daily Paper Intelligence Agent (LangChain/LangGraph version)...")
    
    # Initialize the graph
    app = create_graph()
    
    # Initial state
    initial_state = {
        "all_papers": [],
        "new_papers": [],
        "scored_papers": [],
        "top_papers": [],
        "ai_papers": [],
        "bio_papers": [],
        "report_path": ""
    }
    
    # Run the graph
    try:
        final_state = await app.ainvoke(initial_state)
        print(f"✅ Finished! Report generated at: {final_state['report_path']}")
    except Exception as e:
        print(f"❌ Error during graph execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

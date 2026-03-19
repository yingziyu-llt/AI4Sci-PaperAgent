import sys
import os
import feedparser
import re

# Ensure we can import from the daily_paper_agent module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.nature import NatureFetcher
from keywords import KEYWORDS

def run_diagnostics():
    print("🔍 运行 Nature RSS 数据源诊断...")
    fetcher = NatureFetcher(KEYWORDS)
    
    # 我们先测试前 3 个最具代表性的期刊
    test_journals = {
        k: fetcher.NATURE_FEEDS[k] 
        for k in ["Nature", "Nature Biotechnology", "Nature Machine Intelligence"]
    }
    
    total_entries = 0
    total_research = 0
    total_matched = 0
    
    for journal, url in test_journals.items():
        print(f"\n{'='*50}")
        print(f"📰 正在测试: {journal}")
        print(f"🔗 链接: {url}")
        
        try:
            feed = feedparser.parse(url)
            entries = feed.entries
            print(f"✅ 成功获取 Feed，共包含 {len(entries)} 篇文章。")
            
            research_count = 0
            match_count = 0
            
            # 打印最新的 5 篇文章作为样本分析
            print("\n  👀 样本分析 (最新 5 篇):")
            for i, entry in enumerate(entries[:5]):
                title = entry.title
                link = entry.link
                is_research = fetcher.is_research_article(entry)
                
                print(f"    {i+1}. 标题: {title}")
                print(f"       是否被判定为Research文章? {'✅是' if is_research else '❌否(News/Editorial等被过滤)'}")
                
                if is_research:
                    research_count += 1
                    summary = entry.get('summary', '') or entry.get('description', '')
                    clean_summary = re.sub(r'<[^>]+>', '', summary)
                    search_text = f"{title} {clean_summary}"
                    
                    matches = fetcher.get_matches(search_text)
                    if matches:
                        print(f"       命中关键词: {matches}")
                        match_count += 1
                    else:
                        print(f"       未能命中任何关注的关键词。")
                        print(f"       [摘要文本长度: {len(clean_summary)} 字符. 可能摘要过短？]")
                print("    " + "-"*40)
            
            # 完整扫描整个 Feed 的统计
            for entry in entries:
                total_entries += 1
                if fetcher.is_research_article(entry):
                    total_research += 1
                    summary = entry.get('summary', '') or entry.get('description', '')
                    clean_summary = re.sub(r'<[^>]+>', '', summary)
                    if fetcher.get_matches(f"{entry.title} {clean_summary}"):
                        total_matched += 1
                        match_count += 1 # just for this journal's final print
                        
            print(f"📊 {journal} 统计 (全部 {len(entries)} 篇):")
            print(f"   - 被判定为科研文章的数量: {sum(1 for e in entries if fetcher.is_research_article(e))}")
            print(f"   - 最终命中关键词的文章数量: {match_count}")
                
        except Exception as e:
            print(f"❌ 获取或解析失败: {e}")

    print(f"\n{'='*50}")
    print(f"📈 总体诊断统计:")
    print(f"总计获取文章数: {total_entries}")
    print(f"过滤掉新闻/社论后的科研文章数: {total_research}")
    print(f"命中关键词的最终保留数: {total_matched}")
    
    if total_matched == 0 and total_research > 0:
        print("\n⚠️ 诊断结论: Nature 源能正常获取科研文章，但【全军覆没于关键词匹配】。")
        print("可能的原因：")
        print("1. Nature RSS Feed 提供的摘要 (Summary) 通常只有一两句话（极短），不像 arXiv 包含完整摘要。")
        print("2. 你的 keywords.py 里的特定专业词汇在这短短一句话里根本没有出现。")
        print("建议：对 Nature 源考虑放宽或者跳过硬性关键词匹配，直接全量送给全能的 LLM 进行判断（在 filter.py 预过滤处为 Nature 开绿灯）。")

if __name__ == "__main__":
    run_diagnostics()

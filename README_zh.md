# AI4Sci Daily Paper Agent

这是一个专为 **AI for Science (Bio + Chem)** 领域量身定制的论文自动追踪与智能筛选系统。

该项目基于 **LangGraph** 构建了有状态工作流，每天自动从顶级学术源拉取最新论文，使用大型语言模型进行评分过滤，并为你生成深度沉淀的每日摘要报告，让你不再错过单细胞组学、AI大分子药物设计 (AIDD)、几何深度学习等前沿方向的任何重要突破。

## 🌟 核心功能

- **多源智能对冲检索**: 自动抓取并解析 arXiv, bioRxiv 以及 Nature 子刊（包含 Nature Biotechnology, Nature Machine Intelligence 等）的最新论文。
- **大模型深度评估**: 以 DeepSeek-R1 (通过 SiliconCloud) 作为底座评分引擎，根据设定的关注领域提取论文核心（如 Flow Matching 生成、PROTAC、蛋白质折叠等），输出 1-10 的相关性打分。只保留 7 分以上的高价值成果。
- **自动多维总结**: 对精选后的论文重新阅读，生成包含“核心贡献”、“技术路线”、“主要创新点”的结构化总结。
- **本地化 Markdown 报告**: 每批次运行结束后自动在 `reports/` 目录下生成排版精美的 Markdown 日报，方便阅读与归档。

## ⚙️ 系统架构

处理管线(Pipeline) 完全由 **LangGraph** 实现，节点分布清晰且高度解耦：
1. **Fetch 节点**: 信息抓取与预过滤。
2. **Filter 节点**: 控制批处理大小 (batch_size=10)，进行大语言模型并行打分。
3. **Summarize 节点**: 深度解读已选出的高分论文。
4. **Report 节点**: 格式化输出为最终的汇报文档。

## 🚀 快速开始

### 环境依赖

本项目推荐使用 [`pixi`](https://pixi.sh/) 进行包管理：
```bash
pixi install
```
也可以传统方式安装：
```bash
pip install -r requirements.txt
```

### 配置指南

1. 复制环境变量模板：
```bash
cp .env.example .env
```
2. 使用你顺手的编辑器打开 `.env` 文件，填入你的 `SILICONCLOUD_API_KEY` 及其他所需要的参数。

### 运行程序

配置完成后，一键启动管线：
```bash
python main.py
```

## 🛠️ 技术栈
- **Langchain / LangGraph**: 核心代理工作流框架
- **DeepSeek-R1**: 逻辑推理与摘要提炼模型
- **python-dotenv**: 环境安全管理
- **feedparser**: RSS 源解析

## 🤝 参与贡献
随时欢迎你在 GitHub 提交 Issue 和 Pull Request，一起来让属于 AI for Science 的效率工具越来越好！

## 📄 License
本项目采用 MIT 开源许可证。

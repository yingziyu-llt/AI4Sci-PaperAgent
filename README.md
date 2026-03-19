# AI4Sci Daily Paper Agent

An automated, AI-driven daily paper tracking and intelligent filtering system tailored for the **AI for Science (Bio + Chem)** domain. 

This project utilizes a stateful workflow built with **LangGraph** to automatically fetch, score, and summarize the latest research from top sources, ensuring you never miss a critical breakthrough in geometric deep learning, AIDD, single-cell omics, and protein structure.

## 🌟 Key Features

- **Multi-source Fetching**: Automatically parses the latest daily papers from arXiv, bioRxiv, and select Nature journals (e.g., Nature Biotechnology, Nature Machine Intelligence).
- **Intelligent LLM Filtering**: Powered by DeepSeek-R1, the system evaluates and scores papers on a 1-10 scale based on relevance to predefined core subjects (e.g., GNNs, Flow Matching, Perturb-seq, Molecular Glue). Only high-quality papers (score >= 7) pass the filter.
- **Automated Summarization**: For papers that pass the threshold, the agent generates multidimensional summaries covering the core contributions, technical routes, and innovations.
- **Markdown Reports**: Automatically compiles an easy-to-read daily Markdown report into the `reports/` directory.

## ⚙️ Architecture

The pipeline is implemented as a **LangGraph StateGraph** to guarantee structured, predictable, and fully automated processing:
1. **Fetch Node**: Retrieves feed data.
2. **Filter Node**: Runs batch inferences to score abstract relevance.
3. **Summarize Node**: Provides in-depth analysis on valid papers.
4. **Report Node**: Generates the markdown output and saves it locally.

## 🚀 Getting Started

### Prerequisites

We recommend using [`pixi`](https://pixi.sh/) for dependency management:
```bash
pixi install
```
Alternatively, use `pip`:
```bash
pip install -r requirements.txt
```

### Configuration

1. Copy the environment configuration template:
```bash
cp .env.example .env
```
2. Fill in the required API keys (e.g., your SiliconCloud/DeepSeek API key) and email configurations in your newly created `.env` file.

### Running the Agent

Start the agent pipeline by simply running:
```bash
python main.py
```
*(Ensure that your `main.py` entrypoint executes the LangGraph workflow.)*

## 🛠️ Tech Stack
- **Langchain & LangGraph**: Workflow management and orchestration
- **DeepSeek-R1**: Core reasoning and selection engine
- **Python-dotenv**: Environment and secrets management
- **Feedparser**: RSS and feed processing

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📄 License
This project is licensed under the MIT License.

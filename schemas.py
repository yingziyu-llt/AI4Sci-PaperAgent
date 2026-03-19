from typing import List, Optional
from pydantic import BaseModel, Field

class PaperEvaluation(BaseModel):
    id: int = Field(description="The index/ID of the paper in the batch")
    innovation_score: int = Field(description="Innovation score from 1 to 10. 严厉惩罚缺乏算法层面创新的极度增量工作(堆工作量)，高度奖励具备新颖性和前沿范式的方法论。")
    paper_quality_score: int = Field(description="Overall paper quality score from 1 to 10")
    idea_quality_score: int = Field(description="Idea quality score from 1 to 10. 给有趣、有启发性的核心突破打高分。")
    ai_relevance_score: int = Field(description="Relevance to general AI/ML Methodologies from 1 to 10 (e.g. Foundation Models, Generative matching, GNNs). 纯数据分析或纯湿实验文章必须给 0 分。")
    bio_relevance_score: int = Field(description="Relevance to AI for Science (Bio) from 1 to 10 (e.g. Single-cell generative models, AI Drug Design, Structure Prediction). 纯数据分析或纯湿实验文章必须给 0 分。")

class BatchEvaluation(BaseModel):
    evaluations: List[PaperEvaluation]

class PaperSummary(BaseModel):
    innovation: str = Field(description="Core Innovation. Output value in Chinese. KEEP THE JSON KEY AS 'innovation'.")
    methodology: str = Field(description="Methodology used. Output value in Chinese. KEEP THE JSON KEY AS 'methodology'.")
    key_result: str = Field(description="Key result or conclusion. Output value in Chinese. KEEP THE JSON KEY AS 'key_result'.")

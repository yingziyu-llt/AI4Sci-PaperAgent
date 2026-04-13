from typing import List, Optional
from pydantic import BaseModel, Field

class PaperEvaluation(BaseModel):
    id: int = Field(description="The index/ID of the paper in the batch")
    innovation_score: int = Field(description="Innovation score (1-10). 严厉惩罚缺乏算法创新的增量工作，高度奖励新颖架构（如Flow Matching, GNN, SE(3)）或基础模型。")
    paper_quality_score: int = Field(description="Overall paper quality score (1-10). 考虑通讯作者和机构的背景（如顶级AI/Bio实验室），以及行文的专业度。")
    idea_quality_score: int = Field(description="Idea quality score (1-10). 给有趣、有启发性、能解决核心痛点（如单细胞扰动预测、分子胶设计）的核心突破打高分。")
    ai_relevance_score: int = Field(description="Relevance to AI Methodologies (1-10) like Geometric Deep Learning, Pre-trained Models, Diffusion. 纯数据分析/纯湿实验/无新模型的应用文章必须0分。")
    bio_relevance_score: int = Field(description="Relevance to AI4Science(Bio/Chem) (1-10) like Single-cell/Spatial Omics, AIDD(PROTAC, Molecular Glue), Structure Simulation, or Automated Lab. 纯实验或非AI指导的文章必须0分。")

class BatchEvaluation(BaseModel):
    evaluations: List[PaperEvaluation]

class PaperSummary(BaseModel):
    innovation: str = Field(description="Core Innovation. Output value in Chinese. KEEP THE JSON KEY AS 'innovation'.")
    methodology: str = Field(description="Methodology used. Output value in Chinese. KEEP THE JSON KEY AS 'methodology'.")
    key_result: str = Field(description="Key result or conclusion. Output value in Chinese. KEEP THE JSON KEY AS 'key_result'.")

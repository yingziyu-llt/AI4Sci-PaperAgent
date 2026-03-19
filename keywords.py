# Broad keywords for inclusive filtering across all sources
# Based on interests defined in GEMINI.md

KEYWORDS = {
    "Omics": [
        "single-cell", "scRNA", "scATAC", "spatial transcriptomics", "spatial omics", 
        "multi-modal", "CITE-seq", "cell-cell communication", "perturb-seq", 
        "transcriptome", "genomics", "proteomics", "metabolomics", "atlas", "sequencing",
        "spatial reconstruction", "snRNA", "spatial", "Stereo-seq", "MERFISH", "seqFISH", 
        "smFISH", "cellular dynamics", "trajectory", "scRNA-seq"
    ],
    "Drug_Discovery_Chem": [
        "drug design", "SBDD", "protein-ligand", "molecular glue", "PROTAC", 
        "molecule generation", "binding affinity", "docking", "small molecule",
        "cheminformatics", "pharmacology", "target discovery", "lead optimization",
        "medicinal chemistry", "chemical space", "drug discovery", "ADME", "toxicity",
        "molecular dynamics", "virtual screening", "QSAR", "ADMET", "generative chemistry", 
        "de novo design", "fragment-based", "hit identification", "geometric generation"
    ],
    "AI_ML_Methodology": [
        "deep learning", "machine learning", "neural network", "GNN", "graph",
        "geometric", "equivariant", "SE(3)", "diffusion", "flow matching",
        "generative", "foundation model", "large language model", "LLM", 
        "transformer", "attention mechanism", "pLM", "ESM", "scGPT", "Geneformer",
        "reinforcement learning", "active learning", "artificial intelligence", "AI",
        "pre-training", "fine-tuning", "transfer learning", "Bayesian", "optimization",
        "Discrete Diffusion", "Riemannian Flow", "Flow Matching", "Symmetry", "Invariant Networks",
        "graph neural network", "message passing", "score-based", "optimal transport",
        "multi-modal", "contrastive learning", "representation learning", "autoencoder"
    ],
    "Bio_Structures_General": [
        "protein structure", "folding", "alphafold", "cryo-EM", "conformation",
        "enzyme", "antibody", "peptide", "docking", "geometry", "structural biology",
        "biophysics", "molecular dynamics", "simulation", "computational biology",
        "protein design", "inverse folding", "protein language model", "rosetta", 
        "allostery", "protein-protein interaction", "PPI"
    ]
}

def get_all_keywords():
    all_kws = []
    for kws in KEYWORDS.values():
        all_kws.extend(kws)
    return list(set(all_kws))

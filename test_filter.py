from nodes.filter import filter_node
import config

# Disable actual LLM scoring to only test pre-filtering
def mock_llm_invoke(*args, **kwargs):
    from schemas import BatchEvaluation
    return BatchEvaluation(evaluations=[])

# Mock state
mock_state = {
    "new_papers": [
        {
            "title": "A novel deeply learned single-cell method",
            "summary": "This uses scRNA-seq to study trajectory.",
        },
        {
            "title": "An irrelevant paper about black holes",
            "summary": "This astrophysics paper mentions nothing about biology or ML.",
        },
        {
            "title": "Equivariant Graph Neural Networks for Molecule Binding",
            "summary": "We propose a new GNN and SE(3) invariant approach for SBDD.",
        }
    ]
}

# we need to patch get_llm inside nodes.filter
import nodes.filter
class MockLLM:
    def with_structured_output(self, *args, **kwargs):
        class StructuredLLM:
            def invoke(self, *a, **k):
                class DummyResponse:
                    evaluations = []
                return DummyResponse()
        return StructuredLLM()

nodes.filter.get_llm = lambda: MockLLM()

print("Testing filter_node...")
res = filter_node(mock_state)
print("Finished testing filter_node.")

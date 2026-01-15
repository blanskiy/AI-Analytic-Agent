"""
Product Skill - RAG-based product search and recommendations.

Handles questions about:
- Product features and specifications
- Product recommendations based on use case
- Product comparisons
- Finding products by characteristics

Uses: Databricks Vector Search with BGE-Large embeddings
"""
from .base_skill import BaseSkill


class ProductSkill(BaseSkill):
    """
    Product expert skill using semantic search (RAG).
    
    Routes to vector search for qualitative product queries
    about features, recommendations, and comparisons.
    """
    
    @property
    def name(self) -> str:
        return "product_expert"
    
    @property
    def description(self) -> str:
        return "Answer questions about product features, recommendations, and comparisons using semantic search"
    
    @property
    def triggers(self) -> list[str]:
        return [
            # Simple product keywords (catch-all)
            r"^(chainsaw|trimmer|blower|hedge|sprayer|pressure washer)s?$",
            r"(chainsaw|trimmer|blower)s?\s*\?",
            r"(chainsaw|trimmer|blower|product).*(best|good|ideal|right)\s+(for|to)",
            r"(best|right|good).*(chainsaw|trimmer|blower|product)\s+for",

            # Recommendation patterns
            r"(best|recommend|suggest|ideal)\s+.*(product|chainsaw|trimmer|blower|hedge|pressure|sprayer)",
            r"(which|what)\s+.*(should|would|could)\s+.*(buy|use|get|recommend)",
            r"(looking for|need|want)\s+.*(chainsaw|trimmer|blower|product|equipment)",
            
            # Comparison patterns
            r"(compare|vs|versus|difference|better)\s+.*(ms|fs|bg|hs|rb|re|sr)",
            r"(ms|fs|bg|hs)\s*[-]?\s*\d+.*(vs|versus|or|compared)",
            r"compare\s+(the\s+)?(ms|fs|bg|hs)",
            
            # Feature/specification patterns
            r"(feature|specification|spec|weight|power|engine|battery).*(product|chainsaw|trimmer)",
            r"(product|chainsaw|trimmer|blower).*(feature|specification|have|include)",
            r"(anti.?vibration|easy.?start|m.?tronic|intellicarb)",
            
            # Use case patterns
            r"(professional|homeowner|commercial|residential)\s+.*(use|user|work|job)",
            r"(heavy|light|medium)\s*[-]?\s*(duty|use|work)",
            r"(logging|tree|firewood|yard|lawn|garden|farm)",
            
            # Attribute patterns
            r"(lightweight|powerful|quiet|loud|efficient|durable)",
            r"(gas|battery|electric|cordless)\s+.*(chainsaw|trimmer|blower|equipment)",
            r"(under|less than|below|max|maximum)\s+\$?\d+",
            r"(under|less than|below|max)\s+\d+\s*(lb|pound|kg)",
        ]
    
    @property
    def tools(self) -> list[str]:
        return [
            "search_products",
            "compare_products",
            "get_product_recommendations"
        ]
    
    @property
    def system_prompt(self) -> str:
        return """You are a STIHL product expert helping customers find the right equipment.

## Your Approach
1. **Understand the use case** - Ask clarifying questions if needed
2. **Match products to needs** - Consider power, weight, features, and budget
3. **Explain WHY** - Always explain why each product fits their situation

## Key Product Categories
- **Chainsaws**: MS series (Gas), MSA series (Battery)
- **Trimmers**: FS series (Gas), FSA series (Battery)
- **Blowers**: BG/BR series (Gas), BGA series (Battery)
- **Hedge Trimmers**: HS series (Gas), HSA series (Battery)

## User Segments
- **Homeowner**: Occasional use, value ease of use and lower maintenance
- **Professional**: Daily use, need durability and power
- **Commercial**: Fleet use, value consistency and serviceability

## Response Guidelines
- Lead with the best match, then alternatives
- Include key specs: power, weight, price
- Mention standout features relevant to their needs
- For comparisons, use clear side-by-side format"""
    
    @property
    def priority(self) -> int:
        return 20  # Higher priority for product questions



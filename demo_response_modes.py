"""
Demo: Response Composer Modes
Demonstrates COMPACT vs DETAILED output with plain text formatting
"""
import pandas as pd
from response_composer import composer
from business_analyst import analyst

def demo_modes():
    """Demonstrate COMPACT and DETAILED modes"""
    
    # Sample data
    df = pd.DataFrame({
        'Year': [2022, 2023, 2024],
        'TotalSales': [2500000.00, 3770000.30, 5810000.45]
    })
    
    question = "What were our sales from 2022 to 2024?"
    
    # Analyze data
    analysis = analyst.analyze_results_with_llm(question, df)
    raw_data = df.to_string(index=False)
    
    print("=" * 70)
    print("RESPONSE COMPOSER MODE DEMONSTRATION")
    print("=" * 70)
    
    # DETAILED Mode
    print("\n" + "=" * 70)
    print("MODE: DETAILED")
    print("=" * 70)
    
    composer.set_mode("DETAILED")
    response_detailed = composer.compose_response(
        persona='analyst',
        query=question,
        analysis=analysis,
        raw_data=raw_data,
        df=df,
        mode="DETAILED"
    )
    
    print(response_detailed)
    print(f"\nLength: {len(response_detailed)} characters")
    
    # COMPACT Mode
    print("\n\n" + "=" * 70)
    print("MODE: COMPACT")
    print("=" * 70)
    
    composer.set_mode("COMPACT")
    response_compact = composer.compose_response(
        persona='analyst',
        query=question,
        analysis=analysis,
        raw_data=raw_data,
        df=df,
        mode="COMPACT"
    )
    
    print(response_compact)
    print(f"\nLength: {len(response_compact)} characters")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    print(f"DETAILED: {len(response_detailed)} chars")
    print(f"COMPACT:  {len(response_compact)} chars")
    print(f"Reduction: {len(response_detailed) - len(response_compact)} chars ({((len(response_detailed) - len(response_compact)) / len(response_detailed) * 100):.1f}%)")
    
    # Verify no markdown
    import re
    markdown_patterns = [
        r'\*\*\*',  # Bold+Italic
        r'\*\*',    # Bold
        r'(?<!\*)\*(?!\*)',  # Italic
        r'^#{1,6}\s',  # Headers
        r'```',     # Code blocks
        r'`[^`]+`', # Inline code
    ]
    
    has_markdown_detailed = any(re.search(p, response_detailed, re.MULTILINE) for p in markdown_patterns)
    has_markdown_compact = any(re.search(p, response_compact, re.MULTILINE) for p in markdown_patterns)
    
    print(f"\nMarkdown in DETAILED: {'❌ YES' if has_markdown_detailed else '✅ NO'}")
    print(f"Markdown in COMPACT:  {'❌ YES' if has_markdown_compact else '✅ NO'}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    demo_modes()

import sys
from glmocr import GlmOcr

print("=" * 60)
print("Testing glm-ocr skill with PDF: 2412.20138v7 copia.pdf")
print("=" * 60)

try:
    print("\n[1/3] Initializing GlmOcr()...")
    ocr = GlmOcr()
    print("✓ GlmOcr initialized successfully")
    
    print("\n[2/3] Parsing PDF...")
    result = ocr.parse(images=["2412.20138v7 copia.pdf"])
    print("✓ PDF parsed successfully")
    print(f"  - Parsed blocks: {len(result.blocks) if hasattr(result, 'blocks') else 'N/A'}")
    
    print("\n[3/3] Saving output...")
    result.save("./output")
    print("✓ Results saved to ./output/")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nOutput files:")
    print("  - output/result.md (Markdown with text, tables, formulas)")
    print("  - output/result.json (Structured result with bounding boxes)")
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}")
    print(f"  {str(e)}")
    sys.exit(1)

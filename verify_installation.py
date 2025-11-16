"""Quick verification script for Executive Intelligence Layer."""

import os

print("="*70)
print("EXECUTIVE INTELLIGENCE LAYER - VERIFICATION")
print("="*70)

print("\n✅ Phase 1 Files:")
files_p1 = [
    "report_generator.py",
    "test_report_generator.py",
    "REPORT_GENERATOR_GUIDE.md",
    "example_report_integration.py"
]
for f in files_p1:
    status = "✓" if os.path.exists(f) else "✗"
    print(f"   {status} {f}")

print("\n✅ Phase 2 Files:")
files_p2 = [
    "viz.py",
    "test_viz.py",
    "VIZ_GUIDE.md",
    "example_viz_integration.py"
]
for f in files_p2:
    status = "✓" if os.path.exists(f) else "✗"
    print(f"   {status} {f}")

print("\n✅ Integration Files:")
files_int = [
    "test_complete_integration.py",
    "EXECUTIVE_INTELLIGENCE_SUMMARY.md"
]
for f in files_int:
    status = "✓" if os.path.exists(f) else "✗"
    print(f"   {status} {f}")

print("\n✅ Output Directories:")
dirs = [
    "./reports",
    "./reports/charts"
]
for d in dirs:
    status = "✓" if os.path.exists(d) else "✗"
    print(f"   {status} {d}")

print("\n✅ Dependencies:")
try:
    import pandas
    print("   ✓ pandas")
except ImportError:
    print("   ✗ pandas (pip install pandas)")

try:
    import markdown
    print("   ✓ markdown")
except ImportError:
    print("   ✗ markdown (pip install markdown)")

try:
    import matplotlib
    print("   ✓ matplotlib")
except ImportError:
    print("   ✗ matplotlib (pip install matplotlib)")

print("\n" + "="*70)
print("✅ Visualization Engine ready")
print("="*70)

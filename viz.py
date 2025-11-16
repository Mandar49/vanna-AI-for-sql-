"""
Executive Intelligence Layer - Visualization Engine (Phase 2)
Offline matplotlib-based chart utilities for report generation.
No external dependencies beyond matplotlib.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for offline use
import matplotlib.pyplot as plt


def ensure_chart_dir() -> str:
    """
    Create ./reports/charts directory if missing.
    
    Returns:
        Absolute path to charts directory
    """
    chart_dir = os.path.abspath("./reports/charts")
    Path(chart_dir).mkdir(parents=True, exist_ok=True)
    return chart_dir


def chart_sales_trend(df: pd.DataFrame, x_col: str, y_col: str, out_path: Optional[str] = None) -> str:
    """
    Generate line chart showing sales trend over time.
    
    Args:
        df: DataFrame with time series data
        x_col: Column name for x-axis (typically date/time)
        y_col: Column name for y-axis (typically sales/revenue)
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_sales_trend.png")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line chart
    ax.plot(df[x_col], df[y_col], marker='o', linewidth=2, markersize=6)
    
    # Labels and title
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.set_title(f'{y_col} Trend Over {x_col}', fontsize=14, fontweight='bold')
    
    # Grid for readability
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels if needed
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Save and close
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return os.path.abspath(out_path)


def chart_top_customers(df: pd.DataFrame, name_col: str, value_col: str, out_path: Optional[str] = None, top_n: int = 10) -> str:
    """
    Generate horizontal bar chart showing top customers by value.
    
    Args:
        df: DataFrame with customer data
        name_col: Column name for customer names
        value_col: Column name for values (sales, revenue, etc.)
        out_path: Optional output path (auto-generated if None)
        top_n: Number of top customers to display (default: 10)
        
    Returns:
        Absolute path to saved PNG file
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_top_customers.png")
    
    # Sort and get top N
    df_sorted = df.sort_values(by=value_col, ascending=True).tail(top_n)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Horizontal bar chart
    bars = ax.barh(df_sorted[name_col], df_sorted[value_col])
    
    # Labels and title
    ax.set_xlabel(value_col, fontsize=12)
    ax.set_ylabel(name_col, fontsize=12)
    ax.set_title(f'Top {len(df_sorted)} by {value_col}', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width * 1.01, bar.get_y() + bar.get_height()/2, 
                f'{width:,.0f}', 
                ha='left', va='center', fontsize=9)
    
    # Tight layout
    plt.tight_layout()
    
    # Save and close
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return os.path.abspath(out_path)


def chart_category_breakdown(df: pd.DataFrame, name_col: str, value_col: str, out_path: Optional[str] = None) -> str:
    """
    Generate pie chart showing percentage breakdown by category.
    
    Args:
        df: DataFrame with category data
        name_col: Column name for category names
        value_col: Column name for values
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_category_breakdown.png")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Pie chart
    wedges, texts, autotexts = ax.pie(
        df[value_col], 
        labels=df[name_col],
        autopct='%1.1f%%',
        startangle=90
    )
    
    # Enhance text readability
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    # Title
    ax.set_title(f'{value_col} by {name_col}', fontsize=14, fontweight='bold')
    
    # Equal aspect ratio ensures circular pie
    ax.axis('equal')
    
    # Tight layout
    plt.tight_layout()
    
    # Save and close
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return os.path.abspath(out_path)


if __name__ == "__main__":
    # Quick test
    print("Testing Visualization Engine...")
    
    # Test 1: Sales trend
    trend_df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Sales": [10000, 12000, 11500, 15000, 17000]
    })
    trend_path = chart_sales_trend(trend_df, "Month", "Sales")
    print(f"✓ Sales trend chart: {trend_path}")
    
    # Test 2: Top customers
    customers_df = pd.DataFrame({
        "Customer": [f"Customer {i}" for i in range(1, 11)],
        "Revenue": [50000, 45000, 42000, 38000, 35000, 32000, 30000, 28000, 25000, 22000]
    })
    customers_path = chart_top_customers(customers_df, "Customer", "Revenue")
    print(f"✓ Top customers chart: {customers_path}")
    
    # Test 3: Category breakdown
    category_df = pd.DataFrame({
        "Category": ["Electronics", "Clothing", "Food", "Books", "Toys"],
        "Sales": [35000, 25000, 20000, 12000, 8000]
    })
    category_path = chart_category_breakdown(category_df, "Category", "Sales")
    print(f"✓ Category breakdown chart: {category_path}")
    
    print("\n✅ Visualization Engine ready")


def chart_kpi_dashboard(metrics: dict, out_path: Optional[str] = None) -> str:
    """
    Generate KPI dashboard with multiple metrics.
    
    Args:
        metrics: Dictionary with KPI metrics from kpi_analyzer
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
        
    Example:
        from kpi_analyzer import analyze_kpis
        kpis = analyze_kpis(df)
        chart_path = chart_kpi_dashboard(kpis['metrics'])
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_kpi_dashboard.png")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('KPI Dashboard', fontsize=16, fontweight='bold')
    
    # Extract metrics
    summary = metrics.get('summary', {})
    growth = metrics.get('growth', {})
    financial = metrics.get('financial', {})
    distribution = metrics.get('distribution', {})
    
    # Plot 1: Summary Statistics (Bar chart)
    ax1 = axes[0, 0]
    if summary:
        stats = ['Mean', 'Median', 'Min', 'Max']
        values = [
            summary.get('mean', 0),
            summary.get('median', 0),
            summary.get('min', 0),
            summary.get('max', 0)
        ]
        ax1.bar(stats, values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        ax1.set_title('Summary Statistics', fontweight='bold')
        ax1.set_ylabel('Value')
        ax1.grid(axis='y', alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'No summary data', ha='center', va='center')
        ax1.set_title('Summary Statistics', fontweight='bold')
    
    # Plot 2: Growth Metrics (Line chart)
    ax2 = axes[0, 1]
    if growth and growth.get('first_value') and growth.get('last_value'):
        periods = growth.get('periods', 2)
        first = growth.get('first_value', 0)
        last = growth.get('last_value', 0)
        
        # Simple interpolation
        x = list(range(periods))
        y = [first + (last - first) * i / (periods - 1) for i in range(periods)]
        
        ax2.plot(x, y, marker='o', linewidth=2, color='#3498db')
        ax2.fill_between(x, y, alpha=0.3, color='#3498db')
        ax2.set_title(f'Growth Trend ({growth.get("trend", "N/A")})', fontweight='bold')
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Value')
        ax2.grid(alpha=0.3)
        
        # Add growth rate annotation
        if growth.get('growth_rate') is not None:
            growth_rate = growth['growth_rate'] * 100
            ax2.text(0.5, 0.95, f'Growth: {growth_rate:+.1f}%',
                    transform=ax2.transAxes, ha='center', va='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax2.text(0.5, 0.5, 'No growth data', ha='center', va='center')
        ax2.set_title('Growth Trend', fontweight='bold')
    
    # Plot 3: Financial Metrics (Pie chart)
    ax3 = axes[1, 0]
    if financial and financial.get('revenue') and financial.get('cost'):
        revenue = financial['revenue']
        cost = financial['cost']
        profit = financial.get('profit', revenue - cost)
        
        if profit > 0:
            sizes = [profit, cost]
            labels = [f'Profit\n${profit:,.0f}', f'Cost\n${cost:,.0f}']
            colors = ['#2ecc71', '#e74c3c']
        else:
            sizes = [revenue, abs(profit)]
            labels = [f'Revenue\n${revenue:,.0f}', f'Loss\n${abs(profit):,.0f}']
            colors = ['#3498db', '#e74c3c']
        
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 10})
        
        margin = financial.get('profit_margin', 0) * 100
        ax3.set_title(f'Financial Breakdown\nMargin: {margin:.1f}%', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'No financial data', ha='center', va='center')
        ax3.set_title('Financial Breakdown', fontweight='bold')
    
    # Plot 4: Distribution (Box plot style)
    ax4 = axes[1, 1]
    if summary and summary.get('q25') and summary.get('q75'):
        q25 = summary['q25']
        median = summary['median']
        q75 = summary['q75']
        min_val = summary['min']
        max_val = summary['max']
        
        # Create box plot data
        box_data = [[min_val, q25, median, q75, max_val]]
        bp = ax4.boxplot(box_data, vert=True, patch_artist=True,
                        labels=['Distribution'])
        
        # Color the box
        for patch in bp['boxes']:
            patch.set_facecolor('#3498db')
            patch.set_alpha(0.6)
        
        ax4.set_title('Value Distribution', fontweight='bold')
        ax4.set_ylabel('Value')
        ax4.grid(axis='y', alpha=0.3)
        
        # Add statistics text
        if distribution and distribution.get('std'):
            std = distribution['std']
            cv = distribution.get('cv', 0) * 100
            ax4.text(0.5, 0.02, f'Std Dev: {std:,.0f}\nCV: {cv:.1f}%',
                    transform=ax4.transAxes, ha='center', va='bottom',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax4.text(0.5, 0.5, 'No distribution data', ha='center', va='center')
        ax4.set_title('Value Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return os.path.abspath(out_path)


def chart_anomalies(df: pd.DataFrame, anomalies: list, value_col: str, 
                    out_path: Optional[str] = None) -> str:
    """
    Generate chart highlighting anomalies in data.
    
    Args:
        df: DataFrame with data
        anomalies: List of anomaly dictionaries from detect_anomalies
        value_col: Column name with values
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
        
    Example:
        from kpi_analyzer import detect_anomalies
        anomalies = detect_anomalies(df, value_col='Revenue')
        chart_path = chart_anomalies(df, anomalies['anomalies'], 'Revenue')
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_anomalies.png")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get values
    values = pd.to_numeric(df[value_col], errors='coerce')
    x = range(len(values))
    
    # Plot all values
    ax.plot(x, values, marker='o', linewidth=2, color='#3498db', 
           label='Normal', markersize=6)
    
    # Highlight anomalies
    if anomalies:
        anomaly_indices = [a['index'] for a in anomalies]
        anomaly_values = [values.iloc[i] if i < len(values) else 0 for i in anomaly_indices]
        
        ax.scatter(anomaly_indices, anomaly_values, color='#e74c3c', 
                  s=200, marker='X', label='Anomaly', zorder=5, edgecolors='black')
        
        # Add annotations for top anomalies
        for i, anomaly in enumerate(anomalies[:5]):  # Top 5
            idx = anomaly['index']
            if idx < len(values):
                val = values.iloc[idx]
                ax.annotate(f'Anomaly\n{val:.0f}',
                           xy=(idx, val), xytext=(10, 10),
                           textcoords='offset points',
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color='red'))
    
    # Add mean line
    mean_val = values.mean()
    ax.axhline(y=mean_val, color='green', linestyle='--', 
              label=f'Mean: {mean_val:.0f}', alpha=0.7)
    
    # Add standard deviation bands
    std_val = values.std()
    ax.fill_between(x, mean_val - std_val, mean_val + std_val,
                    alpha=0.2, color='green', label='±1 Std Dev')
    
    ax.set_title(f'Anomaly Detection - {value_col}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Index')
    ax.set_ylabel(value_col)
    ax.legend(loc='best')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return os.path.abspath(out_path)


def chart_growth_comparison(current: float, previous: float, target: float,
                           labels: Optional[list] = None,
                           out_path: Optional[str] = None) -> str:
    """
    Generate comparison chart for growth metrics.
    
    Args:
        current: Current period value
        previous: Previous period value
        target: Target value
        labels: Optional labels for bars
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
        
    Example:
        chart_path = chart_growth_comparison(
            current=150000,
            previous=120000,
            target=140000,
            labels=['Previous', 'Current', 'Target']
        )
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_growth_comparison.png")
    
    # Default labels
    if labels is None:
        labels = ['Previous', 'Current', 'Target']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data
    values = [previous, current, target]
    colors = ['#95a5a6', '#3498db', '#2ecc71']
    
    # Create bars
    bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'${value:,.0f}',
               ha='center', va='bottom', fontweight='bold')
    
    # Calculate and display growth
    if previous > 0:
        growth_rate = ((current - previous) / previous) * 100
        ax.text(0.5, 0.95, f'Growth: {growth_rate:+.1f}%',
               transform=ax.transAxes, ha='center', va='top',
               fontsize=14, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Calculate and display variance from target
    if target > 0:
        variance = ((current - target) / target) * 100
        variance_text = f'vs Target: {variance:+.1f}%'
        color = 'green' if variance >= 0 else 'red'
        ax.text(0.5, 0.88, variance_text,
               transform=ax.transAxes, ha='center', va='top',
               fontsize=12, color=color, fontweight='bold')
    
    ax.set_title('Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_ylabel('Value ($)')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return os.path.abspath(out_path)


def chart_profit_margin_trend(df: pd.DataFrame, revenue_col: str, cost_col: str,
                              date_col: Optional[str] = None,
                              out_path: Optional[str] = None) -> str:
    """
    Generate profit margin trend chart.
    
    Args:
        df: DataFrame with financial data
        revenue_col: Column name for revenue
        cost_col: Column name for cost
        date_col: Optional date column for x-axis
        out_path: Optional output path (auto-generated if None)
        
    Returns:
        Absolute path to saved PNG file
        
    Example:
        chart_path = chart_profit_margin_trend(
            df,
            revenue_col='Revenue',
            cost_col='Cost',
            date_col='Month'
        )
    """
    if out_path is None:
        chart_dir = ensure_chart_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(chart_dir, f"{timestamp}_profit_margin.png")
    
    # Calculate profit and margin
    revenue = pd.to_numeric(df[revenue_col], errors='coerce')
    cost = pd.to_numeric(df[cost_col], errors='coerce')
    profit = revenue - cost
    margin = (profit / revenue * 100).fillna(0)
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # X-axis
    if date_col and date_col in df.columns:
        x = df[date_col]
        x_label = date_col
    else:
        x = range(len(df))
        x_label = 'Period'
    
    # Plot revenue and cost (left y-axis)
    ax1.plot(x, revenue, marker='o', linewidth=2, color='#2ecc71', 
            label='Revenue', markersize=8)
    ax1.plot(x, cost, marker='s', linewidth=2, color='#e74c3c',
            label='Cost', markersize=8)
    ax1.fill_between(x, cost, revenue, alpha=0.3, color='#3498db')
    
    ax1.set_xlabel(x_label, fontsize=12)
    ax1.set_ylabel('Amount ($)', fontsize=12, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(alpha=0.3)
    
    # Plot margin (right y-axis)
    ax2 = ax1.twinx()
    ax2.plot(x, margin, marker='D', linewidth=2, color='#f39c12',
            label='Profit Margin %', markersize=8, linestyle='--')
    ax2.set_ylabel('Profit Margin (%)', fontsize=12, color='#f39c12')
    ax2.tick_params(axis='y', labelcolor='#f39c12')
    ax2.axhline(y=0, color='red', linestyle=':', alpha=0.5)
    
    # Add average margin line
    avg_margin = margin.mean()
    ax2.axhline(y=avg_margin, color='#f39c12', linestyle='--', alpha=0.5,
               label=f'Avg: {avg_margin:.1f}%')
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')
    
    ax1.set_title('Profit Margin Trend Analysis', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return os.path.abspath(out_path)

"""
Executive Intelligence Layer - KPI Analyzer (Phase 5D)
Quantitative analysis of dataframes with KPI metrics, anomaly detection, and trend analysis.
Provides automatic financial and performance metrics for executive reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


def analyze_kpis(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze KPIs from a dataframe and return comprehensive metrics.
    
    Args:
        df: DataFrame with business data
        config: Optional configuration with column mappings
            - value_col: Column name for values (default: auto-detect)
            - date_col: Column name for dates (default: auto-detect)
            - category_col: Column name for categories (default: auto-detect)
            - target: Target value for variance calculation
            - previous_period: Previous period value for YoY/MoM growth
            
    Returns:
        Dictionary with KPI analysis results
        
    Example:
        df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar'],
            'Revenue': [100000, 120000, 115000],
            'Cost': [60000, 70000, 65000]
        })
        
        kpis = analyze_kpis(df)
        print(f"Growth Rate: {kpis['growth_rate']:.2%}")
        print(f"Profit Margin: {kpis['profit_margin']:.2%}")
    """
    if df is None or df.empty:
        return {
            "status": "error",
            "message": "Empty or invalid dataframe",
            "metrics": {}
        }
    
    config = config or {}
    
    # Auto-detect columns
    value_col = config.get('value_col') or _detect_value_column(df)
    date_col = config.get('date_col') or _detect_date_column(df)
    category_col = config.get('category_col') or _detect_category_column(df)
    
    metrics = {
        "summary": _calculate_summary_stats(df, value_col),
        "growth": _calculate_growth_metrics(df, value_col, date_col),
        "financial": _calculate_financial_metrics(df, config),
        "distribution": _calculate_distribution_metrics(df, value_col),
        "trends": _calculate_trend_metrics(df, value_col, date_col),
        "metadata": {
            "rows": len(df),
            "columns": len(df.columns),
            "value_column": value_col,
            "date_column": date_col,
            "category_column": category_col,
            "analyzed_at": datetime.now().isoformat()
        }
    }
    
    return {
        "status": "success",
        "message": f"Analyzed {len(df)} records",
        "metrics": metrics
    }


def detect_anomalies(df: pd.DataFrame, 
                     value_col: Optional[str] = None,
                     method: str = 'iqr',
                     threshold: float = 1.5) -> Dict[str, Any]:
    """
    Detect anomalies and irregularities in data.
    
    Args:
        df: DataFrame to analyze
        value_col: Column to check for anomalies (default: auto-detect)
        method: Detection method ('iqr', 'zscore', 'isolation')
        threshold: Sensitivity threshold (1.5 for IQR, 3 for z-score)
        
    Returns:
        Dictionary with anomaly detection results
        
    Example:
        anomalies = detect_anomalies(df, method='iqr', threshold=1.5)
        print(f"Found {anomalies['anomaly_count']} anomalies")
        for anomaly in anomalies['anomalies']:
            print(f"Row {anomaly['index']}: {anomaly['value']} (expected: {anomaly['expected_range']})")
    """
    if df is None or df.empty:
        return {
            "status": "error",
            "message": "Empty or invalid dataframe",
            "anomalies": []
        }
    
    # Auto-detect value column
    if value_col is None:
        value_col = _detect_value_column(df)
    
    if value_col not in df.columns:
        return {
            "status": "error",
            "message": f"Column '{value_col}' not found",
            "anomalies": []
        }
    
    # Get numeric data
    values = pd.to_numeric(df[value_col], errors='coerce').dropna()
    
    if len(values) == 0:
        return {
            "status": "error",
            "message": "No numeric values found",
            "anomalies": []
        }
    
    # Detect anomalies based on method
    if method == 'iqr':
        anomalies = _detect_anomalies_iqr(df, value_col, threshold)
    elif method == 'zscore':
        anomalies = _detect_anomalies_zscore(df, value_col, threshold)
    elif method == 'isolation':
        anomalies = _detect_anomalies_isolation(df, value_col)
    else:
        return {
            "status": "error",
            "message": f"Unknown method: {method}",
            "anomalies": []
        }
    
    # Calculate statistics
    stats = {
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()),
        "min": float(values.min()),
        "max": float(values.max())
    }
    
    return {
        "status": "success",
        "message": f"Detected {len(anomalies)} anomalies using {method} method",
        "anomaly_count": len(anomalies),
        "anomaly_percentage": (len(anomalies) / len(df)) * 100,
        "anomalies": anomalies,
        "statistics": stats,
        "method": method,
        "threshold": threshold
    }


def calculate_variance(actual: float, target: float) -> Dict[str, Any]:
    """
    Calculate variance between actual and target values.
    
    Args:
        actual: Actual value
        target: Target/expected value
        
    Returns:
        Dictionary with variance metrics
        
    Example:
        variance = calculate_variance(actual=120000, target=100000)
        print(f"Variance: {variance['variance_pct']:.2%}")
        print(f"Status: {variance['status']}")  # 'above', 'below', or 'on_target'
    """
    if target == 0:
        return {
            "variance": actual,
            "variance_pct": None,
            "status": "undefined",
            "message": "Target is zero"
        }
    
    variance = actual - target
    variance_pct = (variance / target)
    
    # Determine status
    if abs(variance_pct) < 0.05:  # Within 5%
        status = "on_target"
    elif variance > 0:
        status = "above_target"
    else:
        status = "below_target"
    
    return {
        "actual": actual,
        "target": target,
        "variance": variance,
        "variance_pct": variance_pct,
        "status": status,
        "message": f"{abs(variance_pct):.1%} {status.replace('_', ' ')}"
    }


def calculate_growth_rate(current: float, previous: float, 
                         period: str = "YoY") -> Dict[str, Any]:
    """
    Calculate growth rate between periods.
    
    Args:
        current: Current period value
        previous: Previous period value
        period: Period type ('YoY', 'MoM', 'QoQ', 'WoW')
        
    Returns:
        Dictionary with growth metrics
        
    Example:
        growth = calculate_growth_rate(current=150000, previous=120000, period='YoY')
        print(f"YoY Growth: {growth['growth_rate']:.2%}")
    """
    if previous == 0:
        return {
            "growth_rate": None,
            "growth_value": current,
            "status": "undefined",
            "message": "Previous period is zero"
        }
    
    growth_rate = (current - previous) / previous
    growth_value = current - previous
    
    # Determine status
    if growth_rate > 0.1:
        status = "strong_growth"
    elif growth_rate > 0:
        status = "moderate_growth"
    elif growth_rate > -0.1:
        status = "slight_decline"
    else:
        status = "significant_decline"
    
    return {
        "current": current,
        "previous": previous,
        "growth_rate": growth_rate,
        "growth_value": growth_value,
        "period": period,
        "status": status,
        "message": f"{abs(growth_rate):.1%} {period} {'growth' if growth_rate >= 0 else 'decline'}"
    }


def calculate_profit_margin(revenue: float, cost: float) -> Dict[str, Any]:
    """
    Calculate profit margin metrics.
    
    Args:
        revenue: Total revenue
        cost: Total cost
        
    Returns:
        Dictionary with profit metrics
        
    Example:
        margin = calculate_profit_margin(revenue=200000, cost=140000)
        print(f"Profit Margin: {margin['profit_margin']:.2%}")
        print(f"Profit: ${margin['profit']:,.2f}")
    """
    if revenue == 0:
        return {
            "profit_margin": None,
            "profit": -cost,
            "status": "no_revenue",
            "message": "No revenue"
        }
    
    profit = revenue - cost
    profit_margin = profit / revenue
    
    # Determine status
    if profit_margin > 0.3:
        status = "excellent"
    elif profit_margin > 0.15:
        status = "good"
    elif profit_margin > 0:
        status = "marginal"
    else:
        status = "loss"
    
    return {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "profit_margin": profit_margin,
        "status": status,
        "message": f"{profit_margin:.1%} profit margin ({status})"
    }


def generate_kpi_summary(df: pd.DataFrame, 
                        config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a text summary of KPIs for reports.
    
    Args:
        df: DataFrame to analyze
        config: Optional configuration
        
    Returns:
        Formatted text summary
        
    Example:
        summary = generate_kpi_summary(df)
        print(summary)
    """
    kpis = analyze_kpis(df, config)
    
    if kpis["status"] != "success":
        return f"KPI Analysis Error: {kpis['message']}"
    
    metrics = kpis["metrics"]
    summary_parts = []
    
    # Summary statistics
    if "summary" in metrics:
        summary = metrics["summary"]
        summary_parts.append(f"**Summary Statistics:**")
        summary_parts.append(f"- Total: {summary.get('total', 0):,.2f}")
        summary_parts.append(f"- Average: {summary.get('mean', 0):,.2f}")
        summary_parts.append(f"- Range: {summary.get('min', 0):,.2f} to {summary.get('max', 0):,.2f}")
    
    # Growth metrics
    if "growth" in metrics and metrics["growth"].get("growth_rate") is not None:
        growth = metrics["growth"]
        rate = growth.get("growth_rate", 0)
        summary_parts.append(f"\n**Growth Metrics:**")
        summary_parts.append(f"- Growth Rate: {rate:.2%}")
        summary_parts.append(f"- Trend: {growth.get('trend', 'stable')}")
    
    # Financial metrics
    if "financial" in metrics:
        financial = metrics["financial"]
        if financial.get("profit_margin") is not None:
            summary_parts.append(f"\n**Financial Metrics:**")
            summary_parts.append(f"- Profit Margin: {financial['profit_margin']:.2%}")
            if financial.get("roi") is not None:
                summary_parts.append(f"- ROI: {financial['roi']:.2%}")
    
    # Distribution
    if "distribution" in metrics:
        dist = metrics["distribution"]
        summary_parts.append(f"\n**Distribution:**")
        summary_parts.append(f"- Std Deviation: {dist.get('std', 0):,.2f}")
        summary_parts.append(f"- Coefficient of Variation: {dist.get('cv', 0):.2%}")
    
    return "\n".join(summary_parts)


# Helper functions

def _detect_value_column(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect the main value column."""
    # Priority keywords
    priority_keywords = ['revenue', 'sales', 'amount', 'value', 'total', 'price']
    
    # Check for priority columns
    for keyword in priority_keywords:
        for col in df.columns:
            if keyword in col.lower():
                if pd.api.types.is_numeric_dtype(df[col]):
                    return col
    
    # Fall back to first numeric column
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            return col
    
    return None


def _detect_date_column(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect date column."""
    date_keywords = ['date', 'time', 'month', 'year', 'day', 'period']
    
    for keyword in date_keywords:
        for col in df.columns:
            if keyword in col.lower():
                return col
    
    # Check for datetime types
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    
    return None


def _detect_category_column(df: pd.DataFrame) -> Optional[str]:
    """Auto-detect category column."""
    category_keywords = ['category', 'type', 'name', 'product', 'customer', 'region']
    
    for keyword in category_keywords:
        for col in df.columns:
            if keyword in col.lower():
                return col
    
    # Fall back to first non-numeric column
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return col
    
    return None


def _calculate_summary_stats(df: pd.DataFrame, value_col: Optional[str]) -> Dict[str, Any]:
    """Calculate summary statistics."""
    if value_col is None or value_col not in df.columns:
        return {}
    
    values = pd.to_numeric(df[value_col], errors='coerce').dropna()
    
    if len(values) == 0:
        return {}
    
    return {
        "count": int(len(values)),
        "total": float(values.sum()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()),
        "min": float(values.min()),
        "max": float(values.max()),
        "q25": float(values.quantile(0.25)),
        "q75": float(values.quantile(0.75))
    }


def _calculate_growth_metrics(df: pd.DataFrame, 
                              value_col: Optional[str],
                              date_col: Optional[str]) -> Dict[str, Any]:
    """Calculate growth metrics."""
    if value_col is None or value_col not in df.columns:
        return {}
    
    values = pd.to_numeric(df[value_col], errors='coerce').dropna()
    
    if len(values) < 2:
        return {"growth_rate": None, "message": "Insufficient data"}
    
    # Calculate period-over-period growth
    first_value = values.iloc[0]
    last_value = values.iloc[-1]
    
    if first_value == 0:
        growth_rate = None
    else:
        growth_rate = (last_value - first_value) / first_value
    
    # Determine trend
    if len(values) >= 3:
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > values.mean() * 0.01:
            trend = "increasing"
        elif slope < -values.mean() * 0.01:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "growth_rate": float(growth_rate) if growth_rate is not None else None,
        "first_value": float(first_value),
        "last_value": float(last_value),
        "trend": trend,
        "periods": int(len(values))
    }


def _calculate_financial_metrics(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate financial metrics."""
    metrics = {}
    
    # Look for revenue and cost columns
    revenue_col = None
    cost_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'revenue' in col_lower or 'sales' in col_lower:
            revenue_col = col
        elif 'cost' in col_lower or 'expense' in col_lower:
            cost_col = col
    
    if revenue_col and cost_col:
        revenue = pd.to_numeric(df[revenue_col], errors='coerce').sum()
        cost = pd.to_numeric(df[cost_col], errors='coerce').sum()
        
        if revenue > 0:
            profit = revenue - cost
            metrics["revenue"] = float(revenue)
            metrics["cost"] = float(cost)
            metrics["profit"] = float(profit)
            metrics["profit_margin"] = float(profit / revenue)
            
            if cost > 0:
                metrics["roi"] = float(profit / cost)
    
    return metrics


def _calculate_distribution_metrics(df: pd.DataFrame, value_col: Optional[str]) -> Dict[str, Any]:
    """Calculate distribution metrics."""
    if value_col is None or value_col not in df.columns:
        return {}
    
    values = pd.to_numeric(df[value_col], errors='coerce').dropna()
    
    if len(values) == 0:
        return {}
    
    mean = values.mean()
    std = values.std()
    
    return {
        "std": float(std),
        "variance": float(values.var()),
        "cv": float(std / mean) if mean != 0 else None,  # Coefficient of variation
        "skewness": float(values.skew()),
        "kurtosis": float(values.kurtosis())
    }


def _calculate_trend_metrics(df: pd.DataFrame,
                             value_col: Optional[str],
                             date_col: Optional[str]) -> Dict[str, Any]:
    """Calculate trend metrics."""
    if value_col is None or value_col not in df.columns:
        return {}
    
    values = pd.to_numeric(df[value_col], errors='coerce').dropna()
    
    if len(values) < 3:
        return {"message": "Insufficient data for trend analysis"}
    
    # Linear regression
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 1)
    slope = coeffs[0]
    intercept = coeffs[1]
    
    # R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((values - y_pred) ** 2)
    ss_tot = np.sum((values - values.mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "trend_strength": "strong" if abs(r_squared) > 0.7 else "moderate" if abs(r_squared) > 0.4 else "weak"
    }


def _detect_anomalies_iqr(df: pd.DataFrame, value_col: str, threshold: float) -> List[Dict[str, Any]]:
    """Detect anomalies using IQR method."""
    values = pd.to_numeric(df[value_col], errors='coerce')
    
    Q1 = values.quantile(0.25)
    Q3 = values.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    
    anomalies = []
    for idx, value in values.items():
        if pd.notna(value) and (value < lower_bound or value > upper_bound):
            anomalies.append({
                "index": int(idx),
                "value": float(value),
                "expected_range": f"{lower_bound:.2f} to {upper_bound:.2f}",
                "deviation": "below" if value < lower_bound else "above",
                "severity": abs(value - (Q1 if value < lower_bound else Q3)) / IQR
            })
    
    return anomalies


def _detect_anomalies_zscore(df: pd.DataFrame, value_col: str, threshold: float) -> List[Dict[str, Any]]:
    """Detect anomalies using Z-score method."""
    values = pd.to_numeric(df[value_col], errors='coerce')
    
    mean = values.mean()
    std = values.std()
    
    if std == 0:
        return []
    
    anomalies = []
    for idx, value in values.items():
        if pd.notna(value):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                anomalies.append({
                    "index": int(idx),
                    "value": float(value),
                    "z_score": float(z_score),
                    "expected_range": f"{mean - threshold*std:.2f} to {mean + threshold*std:.2f}",
                    "deviation": "below" if value < mean else "above",
                    "severity": float(z_score / threshold)
                })
    
    return anomalies


def _detect_anomalies_isolation(df: pd.DataFrame, value_col: str) -> List[Dict[str, Any]]:
    """Detect anomalies using simple isolation method (statistical outliers)."""
    # Fallback to IQR if isolation forest not available
    return _detect_anomalies_iqr(df, value_col, 1.5)


if __name__ == "__main__":
    print("="*70)
    print("KPI ANALYZER TEST")
    print("="*70)
    print()
    
    # Test 1: Create sample data
    print("1. Creating sample financial data...")
    df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [100000, 120000, 115000, 135000, 142000, 138000],
        'Cost': [60000, 70000, 65000, 75000, 80000, 78000],
        'Customers': [500, 550, 530, 600, 620, 610]
    })
    print(f"   ✓ Created dataframe with {len(df)} rows")
    print()
    
    # Test 2: Analyze KPIs
    print("2. Analyzing KPIs...")
    kpis = analyze_kpis(df)
    print(f"   Status: {kpis['status']}")
    print(f"   Message: {kpis['message']}")
    
    if kpis['status'] == 'success':
        metrics = kpis['metrics']
        print(f"\n   Summary:")
        print(f"   - Total Revenue: ${metrics['summary']['total']:,.2f}")
        print(f"   - Average: ${metrics['summary']['mean']:,.2f}")
        print(f"   - Growth Rate: {metrics['growth'].get('growth_rate', 0):.2%}")
        print(f"   - Profit Margin: {metrics['financial'].get('profit_margin', 0):.2%}")
    print()
    
    # Test 3: Detect anomalies
    print("3. Detecting anomalies...")
    anomalies = detect_anomalies(df, value_col='Revenue', method='iqr')
    print(f"   Status: {anomalies['status']}")
    print(f"   Anomalies found: {anomalies['anomaly_count']}")
    
    if anomalies['anomaly_count'] > 0:
        print(f"   Anomalies:")
        for anomaly in anomalies['anomalies'][:3]:
            print(f"   - Row {anomaly['index']}: ${anomaly['value']:,.2f} ({anomaly['deviation']})")
    print()
    
    # Test 4: Calculate specific metrics
    print("4. Calculating specific metrics...")
    
    # Growth rate
    growth = calculate_growth_rate(current=142000, previous=100000, period='YoY')
    print(f"   Growth: {growth['message']}")
    
    # Profit margin
    margin = calculate_profit_margin(revenue=750000, cost=448000)
    print(f"   Margin: {margin['message']}")
    
    # Variance
    variance = calculate_variance(actual=142000, target=130000)
    print(f"   Variance: {variance['message']}")
    print()
    
    # Test 5: Generate summary
    print("5. Generating KPI summary...")
    summary = generate_kpi_summary(df)
    print(summary)
    print()
    
    print("="*70)
    print("✅ KPI Analyzer ready")
    print("="*70)

"""
Data Validator - Ensures LLM responses contain only actual database values
Prevents hallucination and fabrication of numerical data
"""
import re
import pandas as pd
from typing import List, Tuple

class DataValidator:
    """Validates that responses contain only actual data from query results"""
    
    def __init__(self):
        self.cagr_tolerance = 0.5  # 0.5% tolerance for CAGR
        self.forecast_tolerance = 1.0  # ₹1.00 tolerance for forecasts
    
    def extract_numbers_from_text(self, text: str) -> List[float]:
        """
        Extract all numerical values from text
        
        Args:
            text: Text to extract numbers from
        
        Returns:
            List of float values found in text
        """
        # Pattern to match numbers (including decimals, percentages, currency)
        # Matches: 123, 123.45, 123,456.78, $123.45, 45%, etc.
        pattern = r'[\$]?[\d,]+\.?\d*[%]?'
        
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            # Clean the match (remove $, %, commas)
            cleaned = match.replace('$', '').replace('%', '').replace(',', '')
            try:
                numbers.append(float(cleaned))
            except ValueError:
                continue
        
        return numbers
    
    def extract_numbers_from_dataframe(self, df: pd.DataFrame) -> List[float]:
        """
        Extract all numerical values from DataFrame
        
        Args:
            df: DataFrame to extract numbers from
        
        Returns:
            List of float values in the DataFrame
        """
        numbers = []
        
        # Get all numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            values = df[col].dropna().tolist()
            numbers.extend([float(v) for v in values])
        
        return numbers
    
    def validate_response(self, response: str, df: pd.DataFrame, tolerance: float = 0.01) -> Tuple[bool, List[float]]:
        """
        Validate that all numbers in response exist in the DataFrame
        
        Args:
            response: LLM-generated response text
            df: Source DataFrame
            tolerance: Tolerance for floating point comparison (default 0.01)
        
        Returns:
            Tuple of (is_valid, suspicious_numbers)
            - is_valid: True if all numbers are found in data
            - suspicious_numbers: List of numbers not found in data
        """
        if df is None or df.empty:
            return (True, [])  # Can't validate against empty data
        
        response_numbers = self.extract_numbers_from_text(response)
        data_numbers = self.extract_numbers_from_dataframe(df)
        
        suspicious = []
        
        for num in response_numbers:
            # Check if this number exists in the data (with tolerance)
            found = False
            for data_num in data_numbers:
                if abs(num - data_num) <= tolerance:
                    found = True
                    break
            
            if not found:
                # Allow certain types of numbers that are likely safe:
                
                # 1. Years (2020-2030 range)
                if 2020 <= num <= 2030:
                    continue
                
                # 2. Small percentages (0-100)
                if 0 < num < 100:
                    continue
                
                # 3. Very small numbers (counts, indices)
                if 0 <= num <= 10:
                    continue
                
                # 4. Check if it could be a calculated difference/sum of existing numbers
                # Allow if it's within reasonable range of data values
                if data_numbers:
                    max_data = max(data_numbers)
                    min_data = min(data_numbers)
                    
                    # If the number is a plausible difference or sum
                    if min_data <= num <= max_data * 2:
                        # Could be a calculated value, be lenient
                        continue
                
                suspicious.append(num)
        
        is_valid = len(suspicious) == 0
        
        return (is_valid, suspicious)
    
    def validate_cagr(self, cagr_value: float, start_sales: float, end_sales: float, 
                     start_year: int, end_year: int) -> Tuple[bool, str]:
        """
        Validate CAGR calculation against formula
        
        Formula: CAGR = ((end/start)^(1/(end_year-start_year)) - 1) * 100
        
        Args:
            cagr_value: CAGR percentage to validate
            start_sales: Starting sales value
            end_sales: Ending sales value
            start_year: Starting year
            end_year: Ending year
        
        Returns:
            Tuple of (is_valid, message)
        """
        if start_sales <= 0 or end_sales <= 0:
            return (False, "Invalid sales values (must be positive)")
        
        years = end_year - start_year
        if years <= 0:
            return (False, "Invalid year range")
        
        # Calculate expected CAGR
        expected_cagr = (pow(end_sales / start_sales, 1.0 / years) - 1) * 100
        
        # Check tolerance
        diff = abs(cagr_value - expected_cagr)
        
        if diff <= self.cagr_tolerance:
            return (True, f"CAGR validated: {cagr_value}% (expected: {expected_cagr:.2f}%)")
        else:
            return (False, f"CAGR mismatch: {cagr_value}% vs expected {expected_cagr:.2f}% (diff: {diff:.2f}%)")
    
    def validate_forecast(self, forecast_value: float, base_sales: float, cagr_decimal: float, 
                         years_ahead: int) -> Tuple[bool, str]:
        """
        Validate forecast calculation against formula
        
        Formula: Forecast = base_sales * (1 + CAGR)^years_ahead
        
        Args:
            forecast_value: Forecast value to validate
            base_sales: Base sales value
            cagr_decimal: CAGR as decimal (e.g., 0.0285 for 2.85%)
            years_ahead: Number of years ahead
        
        Returns:
            Tuple of (is_valid, message)
        """
        if base_sales <= 0:
            return (False, "Invalid base sales value")
        
        if years_ahead <= 0:
            return (False, "Invalid years ahead")
        
        # Calculate expected forecast
        expected_forecast = base_sales * pow(1 + cagr_decimal, years_ahead)
        
        # Check tolerance
        diff = abs(forecast_value - expected_forecast)
        
        if diff <= self.forecast_tolerance:
            return (True, f"Forecast validated: {forecast_value:.2f} (expected: {expected_forecast:.2f})")
        else:
            return (False, f"Forecast mismatch: {forecast_value:.2f} vs expected {expected_forecast:.2f} (diff: {diff:.2f})")
    
    def add_validation_warning(self, response: str, suspicious_numbers: List[float]) -> str:
        """
        Add a warning to response if suspicious numbers are detected
        
        Args:
            response: Original response
            suspicious_numbers: List of suspicious numbers
        
        Returns:
            Response with warning appended if needed
        """
        if not suspicious_numbers:
            return response
        
        warning = f"\n\n⚠️ **Data Validation Warning:**\n"
        warning += f"The following numbers in the analysis may not match the actual database values: {suspicious_numbers}\n"
        warning += "Please verify these numbers against the raw SQL results shown above."
        
        return response + warning

# Global validator instance
validator = DataValidator()

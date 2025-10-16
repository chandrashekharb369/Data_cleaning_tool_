"""
Utility functions for Smart Data Cleaner
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import re
from pathlib import Path

def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def format_number(number: Union[int, float]) -> str:
    """Format number with commas for thousands separator"""
    if isinstance(number, (int, float)):
        if number >= 1000:
            return f"{number:,.0f}" if isinstance(number, int) else f"{number:,.2f}"
        else:
            return str(number) if isinstance(number, int) else f"{number:.2f}"
    return str(number)

def detect_delimiter(file_path: str, encoding: str = 'utf-8') -> str:
    """Detect CSV delimiter by analyzing the first few lines"""
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            first_line = file.readline()
            
        # Common delimiters to test
        delimiters = [',', ';', '\t', '|', ':']
        delimiter_counts = {}
        
        for delimiter in delimiters:
            delimiter_counts[delimiter] = first_line.count(delimiter)
        
        # Return delimiter with highest count
        return max(delimiter_counts, key=delimiter_counts.get)
        
    except Exception:
        return ','  # Default to comma

def detect_encoding(file_path: str) -> str:
    """Detect file encoding"""
    try:
        import chardet
        
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            return result['encoding'] if result['encoding'] else 'utf-8'
            
    except ImportError:
        # If chardet not available, try common encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    file.read(1000)  # Try to read first 1KB
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default fallback

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names to be more standardized"""
    df = df.copy()
    
    # Clean column names
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    df.columns = df.columns.str.replace(r'[^\w\s]', '_', regex=True)  # Replace special chars
    df.columns = df.columns.str.replace(r'\s+', '_', regex=True)  # Replace spaces with underscores
    df.columns = df.columns.str.lower()  # Convert to lowercase
    
    # Handle duplicate column names
    seen = set()
    new_columns = []
    
    for col in df.columns:
        if col in seen:
            counter = 1
            new_col = f"{col}_{counter}"
            while new_col in seen:
                counter += 1
                new_col = f"{col}_{counter}"
            new_columns.append(new_col)
            seen.add(new_col)
        else:
            new_columns.append(col)
            seen.add(col)
    
    df.columns = new_columns
    return df

def infer_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """Infer optimal data types for columns"""
    type_suggestions = {}
    
    for column in df.columns:
        col_data = df[column].dropna()
        
        if col_data.empty:
            type_suggestions[column] = 'object'
            continue
        
        # Try to convert to numeric
        try:
            pd.to_numeric(col_data, errors='raise')
            
            # Check if integers
            if col_data.apply(lambda x: float(x).is_integer()).all():
                # Check range for optimal integer type
                min_val, max_val = col_data.min(), col_data.max()
                if -128 <= min_val and max_val <= 127:
                    type_suggestions[column] = 'int8'
                elif -32768 <= min_val and max_val <= 32767:
                    type_suggestions[column] = 'int16'
                elif -2147483648 <= min_val and max_val <= 2147483647:
                    type_suggestions[column] = 'int32'
                else:
                    type_suggestions[column] = 'int64'
            else:
                type_suggestions[column] = 'float64'
                
        except (ValueError, TypeError):
            # Try datetime
            try:
                pd.to_datetime(col_data, errors='raise', infer_datetime_format=True)
                type_suggestions[column] = 'datetime64[ns]'
            except (ValueError, TypeError):
                # Check if boolean
                unique_values = col_data.str.lower().unique()
                bool_values = {'true', 'false', 't', 'f', 'yes', 'no', 'y', 'n', '1', '0'}
                
                if len(unique_values) <= 2 and all(val in bool_values for val in unique_values):
                    type_suggestions[column] = 'bool'
                else:
                    # Check if categorical (low cardinality)
                    if len(unique_values) / len(col_data) < 0.5 and len(unique_values) < 100:
                        type_suggestions[column] = 'category'
                    else:
                        type_suggestions[column] = 'object'
    
    return type_suggestions

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate data quality and return issues"""
    issues = {
        'critical': [],
        'warnings': [],
        'info': []
    }
    
    # Check for completely empty columns
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        issues['critical'].append(f"Completely empty columns: {empty_cols}")
    
    # Check for columns with single value
    single_value_cols = []
    for col in df.columns:
        if df[col].nunique() == 1:
            single_value_cols.append(col)
    
    if single_value_cols:
        issues['warnings'].append(f"Columns with single value: {single_value_cols}")
    
    # Check for high missing data percentage
    high_missing_cols = []
    for col in df.columns:
        missing_pct = (df[col].isnull().sum() / len(df)) * 100
        if missing_pct > 50:
            high_missing_cols.append((col, missing_pct))
    
    if high_missing_cols:
        issues['warnings'].append(f"Columns with >50% missing data: {high_missing_cols}")
    
    # Check for potential ID columns
    potential_id_cols = []
    for col in df.columns:
        if df[col].nunique() == len(df) and len(df) > 10:
            potential_id_cols.append(col)
    
    if potential_id_cols:
        issues['info'].append(f"Potential ID columns: {potential_id_cols}")
    
    # Check for numeric columns with negative values where inappropriate
    negative_value_issues = []
    suspicious_cols = ['age', 'price', 'amount', 'quantity', 'count', 'size', 'weight', 'height']
    
    for col in df.select_dtypes(include=[np.number]).columns:
        col_lower = col.lower()
        if any(suspicious in col_lower for suspicious in suspicious_cols):
            if (df[col] < 0).any():
                negative_count = (df[col] < 0).sum()
                negative_value_issues.append((col, negative_count))
    
    if negative_value_issues:
        issues['warnings'].append(f"Columns with unexpected negative values: {negative_value_issues}")
    
    return issues

def generate_sample_data() -> pd.DataFrame:
    """Generate sample data for testing purposes"""
    np.random.seed(42)
    
    n_samples = 1000
    
    data = {
        'id': range(1, n_samples + 1),
        'name': [f"Person_{i}" for i in range(1, n_samples + 1)],
        'age': np.random.randint(18, 80, n_samples),
        'salary': np.random.normal(50000, 15000, n_samples),
        'department': np.random.choice(['HR', 'Engineering', 'Sales', 'Marketing', 'Finance'], n_samples),
        'start_date': pd.date_range(start='2020-01-01', periods=n_samples, freq='D'),
        'performance_score': np.random.uniform(1, 10, n_samples),
        'is_manager': np.random.choice([True, False], n_samples, p=[0.2, 0.8])
    }
    
    df = pd.DataFrame(data)
    
    # Introduce some missing values
    missing_indices = np.random.choice(df.index, size=int(0.1 * len(df)), replace=False)
    df.loc[missing_indices, 'salary'] = np.nan
    
    missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
    df.loc[missing_indices, 'performance_score'] = np.nan
    
    # Introduce some duplicates
    duplicate_indices = np.random.choice(df.index, size=20, replace=False)
    for idx in duplicate_indices:
        if idx + 1 < len(df):
            df.loc[idx + 1] = df.loc[idx]
    
    return df

def create_data_backup(df: pd.DataFrame, backup_dir: str = "backups") -> str:
    """Create a backup of the current data"""
    try:
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"data_backup_{timestamp}.pkl"
        
        df.to_pickle(backup_file)
        return str(backup_file)
        
    except Exception as e:
        raise Exception(f"Error creating backup: {str(e)}")

def load_data_backup(backup_file: str) -> pd.DataFrame:
    """Load data from backup file"""
    try:
        return pd.read_pickle(backup_file)
    except Exception as e:
        raise Exception(f"Error loading backup: {str(e)}")

def estimate_processing_time(df: pd.DataFrame, operation: str) -> str:
    """Estimate processing time for different operations"""
    n_rows, n_cols = df.shape
    
    # Rough estimates based on data size
    estimates = {
        'load': max(1, n_rows * n_cols / 100000),
        'clean': max(2, n_rows * n_cols / 50000),
        'analyze': max(3, n_rows * n_cols / 30000),
        'export': max(1, n_rows * n_cols / 80000),
        'visualize': max(2, n_rows / 10000)
    }
    
    time_seconds = estimates.get(operation, 1)
    
    if time_seconds < 60:
        return f"~{time_seconds:.0f} seconds"
    elif time_seconds < 3600:
        return f"~{time_seconds/60:.1f} minutes"
    else:
        return f"~{time_seconds/3600:.1f} hours"

class ProgressTracker:
    """Simple progress tracking utility"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.callbacks = []
    
    def add_callback(self, callback):
        """Add callback function to be called on progress update"""
        self.callbacks.append(callback)
    
    def update(self, step: int = None, message: str = None):
        """Update progress"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        progress_pct = (self.current_step / self.total_steps) * 100
        
        status = {
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress_pct': progress_pct,
            'message': message or f"{self.description} - Step {self.current_step}/{self.total_steps}"
        }
        
        # Call all registered callbacks
        for callback in self.callbacks:
            try:
                callback(status)
            except Exception:
                pass  # Ignore callback errors
    
    def finish(self, message: str = "Completed"):
        """Mark as finished"""
        self.current_step = self.total_steps
        self.update(message=message)
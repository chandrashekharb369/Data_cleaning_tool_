"""
Data Processor - Core data handling and processing logic
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

class DataProcessor:
    """Main data processing class for Smart Data Cleaner"""
    
    def __init__(self):
        self.data = None
        self.original_data = None
        self.metadata = {}
        self.processing_log = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, file_path: str) -> bool:
        """Load data from CSV or Excel file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            # Determine file type and load accordingly
            if file_path.suffix.lower() == '.csv':
                self.data = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            else:
                self.logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            # Store original data
            self.original_data = self.data.copy()
            
            # Initialize metadata
            self._update_metadata()
            self._log_action(f"Loaded data from {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _update_metadata(self):
        """Update metadata about the current dataset"""
        if self.data is not None:
            self.metadata = {
                'shape': self.data.shape,
                'columns': list(self.data.columns),
                'dtypes': dict(self.data.dtypes),
                'missing_values': dict(self.data.isnull().sum()),
                'memory_usage': self.data.memory_usage(deep=True).sum(),
                'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.data.select_dtypes(include=['object']).columns),
                'duplicates': self.data.duplicated().sum()
            }
    
    def _log_action(self, action: str):
        """Log an action performed on the data"""
        self.processing_log.append(action)
        self.logger.info(action)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        if self.data is None:
            return {}
        
        summary = {
            'basic_info': {
                'rows': self.data.shape[0],
                'columns': self.data.shape[1],
                'memory_usage': f"{self.metadata['memory_usage'] / 1024:.2f} KB",
                'duplicates': self.metadata['duplicates']
            },
            'column_types': {
                'numeric': len(self.metadata['numeric_columns']),
                'categorical': len(self.metadata['categorical_columns'])
            },
            'missing_data': {
                'total_missing': self.data.isnull().sum().sum(),
                'columns_with_missing': len([col for col, count in self.metadata['missing_values'].items() if count > 0])
            },
            'data_types': self.metadata['dtypes']
        }
        
        return summary
    
    def get_column_info(self) -> Dict[str, Dict]:
        """Get detailed information about each column"""
        if self.data is None:
            return {}
        
        column_info = {}
        
        for col in self.data.columns:
            info = {
                'dtype': str(self.data[col].dtype),
                'missing_count': self.data[col].isnull().sum(),
                'missing_percentage': (self.data[col].isnull().sum() / len(self.data)) * 100,
                'unique_values': self.data[col].nunique(),
                'is_numeric': col in self.metadata['numeric_columns']
            }
            
            if info['is_numeric']:
                info.update({
                    'mean': self.data[col].mean(),
                    'std': self.data[col].std(),
                    'min': self.data[col].min(),
                    'max': self.data[col].max(),
                    'q25': self.data[col].quantile(0.25),
                    'q50': self.data[col].quantile(0.50),
                    'q75': self.data[col].quantile(0.75)
                })
            else:
                # For categorical columns
                value_counts = self.data[col].value_counts().head(10)
                info.update({
                    'top_values': dict(value_counts),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None
                })
            
            column_info[col] = info
        
        return column_info
    
    def get_processing_log(self) -> List[str]:
        """Get the processing log"""
        return self.processing_log.copy()
    
    def reset_data(self):
        """Reset data to original state"""
        if self.original_data is not None:
            self.data = self.original_data.copy()
            self._update_metadata()
            self._log_action("Reset data to original state")
    
    def get_data_preview(self, rows: int = 10) -> pd.DataFrame:
        """Get a preview of the data"""
        if self.data is None:
            return pd.DataFrame()
        return self.data.head(rows)
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the current data"""
        return self.data.copy() if self.data is not None else None
    
    def set_data(self, data: pd.DataFrame):
        """Set new data and update metadata"""
        self.data = data
        self._update_metadata()
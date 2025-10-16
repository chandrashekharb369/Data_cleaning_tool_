"""
Data Cleaner - Core data cleaning functions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
import logging

class DataCleaner:
    """Data cleaning functionality for Smart Data Cleaner"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.logger = logging.getLogger(__name__)
    
    def remove_duplicates(self, keep: str = 'first') -> bool:
        """Remove duplicate rows from the dataset"""
        try:
            if self.data_processor.data is None:
                return False
            
            initial_rows = len(self.data_processor.data)
            self.data_processor.data = self.data_processor.data.drop_duplicates(keep=keep)
            removed_rows = initial_rows - len(self.data_processor.data)
            
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Removed {removed_rows} duplicate rows (keep='{keep}')")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}")
            return False
    
    def handle_missing_values(self, strategy: Dict[str, str]) -> bool:
        """
        Handle missing values with different strategies per column
        
        Strategies:
        - 'drop': Drop rows with missing values
        - 'mean': Fill with mean (numeric only)
        - 'median': Fill with median (numeric only)
        - 'mode': Fill with mode
        - 'forward_fill': Forward fill
        - 'backward_fill': Backward fill
        - 'constant': Fill with a constant value
        - 'knn': Use KNN imputation
        """
        try:
            if self.data_processor.data is None:
                return False
            
            data = self.data_processor.data.copy()
            
            for column, method in strategy.items():
                if column not in data.columns:
                    continue
                
                if method == 'drop':
                    data = data.dropna(subset=[column])
                
                elif method == 'mean' and data[column].dtype in ['int64', 'float64']:
                    data[column].fillna(data[column].mean(), inplace=True)
                
                elif method == 'median' and data[column].dtype in ['int64', 'float64']:
                    data[column].fillna(data[column].median(), inplace=True)
                
                elif method == 'mode':
                    mode_value = data[column].mode()
                    if len(mode_value) > 0:
                        data[column].fillna(mode_value[0], inplace=True)
                
                elif method == 'forward_fill':
                    data[column].fillna(method='ffill', inplace=True)
                
                elif method == 'backward_fill':
                    data[column].fillna(method='bfill', inplace=True)
                
                elif method.startswith('constant:'):
                    constant_value = method.split(':', 1)[1]
                    data[column].fillna(constant_value, inplace=True)
                
                elif method == 'knn':
                    self._apply_knn_imputation(data, [column])
            
            self.data_processor.data = data
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Applied missing value strategies: {strategy}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling missing values: {str(e)}")
            return False
    
    def _apply_knn_imputation(self, data: pd.DataFrame, columns: List[str]):
        """Apply KNN imputation to specified columns"""
        try:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            target_cols = [col for col in columns if col in numeric_cols]
            
            if target_cols:
                imputer = KNNImputer(n_neighbors=5)
                data[target_cols] = imputer.fit_transform(data[target_cols])
                
        except Exception as e:
            self.logger.error(f"Error in KNN imputation: {str(e)}")
    
    def detect_and_handle_outliers(self, method: str = 'iqr', columns: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Detect and handle outliers using IQR or Z-score method
        
        Methods:
        - 'iqr': Interquartile Range method
        - 'zscore': Z-score method
        """
        try:
            if self.data_processor.data is None:
                return {}
            
            data = self.data_processor.data.copy()
            outlier_counts = {}
            
            # Get numeric columns to process
            if columns is None:
                columns = self.data_processor.metadata['numeric_columns']
            else:
                columns = [col for col in columns if col in self.data_processor.metadata['numeric_columns']]
            
            for column in columns:
                initial_count = len(data)
                
                if method == 'iqr':
                    Q1 = data[column].quantile(0.25)
                    Q3 = data[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = (data[column] < lower_bound) | (data[column] > upper_bound)
                
                elif method == 'zscore':
                    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                    outliers = z_scores > 3
                
                else:
                    continue
                
                # Remove outliers
                data = data[~outliers]
                outlier_counts[column] = initial_count - len(data)
            
            self.data_processor.data = data
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Removed outliers using {method} method: {outlier_counts}")
            
            return outlier_counts
            
        except Exception as e:
            self.logger.error(f"Error handling outliers: {str(e)}")
            return {}
    
    def create_dummy_variables(self, columns: Optional[List[str]] = None, drop_first: bool = True) -> bool:
        """Create dummy variables for categorical columns"""
        try:
            if self.data_processor.data is None:
                return False
            
            data = self.data_processor.data.copy()
            
            # Get categorical columns to process
            if columns is None:
                columns = self.data_processor.metadata['categorical_columns']
            else:
                columns = [col for col in columns if col in self.data_processor.metadata['categorical_columns']]
            
            if not columns:
                return True
            
            # Create dummy variables
            dummy_data = pd.get_dummies(data, columns=columns, drop_first=drop_first, prefix=columns)
            
            self.data_processor.data = dummy_data
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Created dummy variables for columns: {columns}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating dummy variables: {str(e)}")
            return False
    
    def normalize_numeric_columns(self, columns: Optional[List[str]] = None, method: str = 'standard') -> bool:
        """
        Normalize numeric columns
        
        Methods:
        - 'standard': StandardScaler (mean=0, std=1)
        - 'minmax': Min-Max scaling (0-1)
        """
        try:
            if self.data_processor.data is None:
                return False
            
            data = self.data_processor.data.copy()
            
            # Get numeric columns to process
            if columns is None:
                columns = self.data_processor.metadata['numeric_columns']
            else:
                columns = [col for col in columns if col in self.data_processor.metadata['numeric_columns']]
            
            if not columns:
                return True
            
            if method == 'standard':
                scaler = StandardScaler()
                data[columns] = scaler.fit_transform(data[columns])
            
            elif method == 'minmax':
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                data[columns] = scaler.fit_transform(data[columns])
            
            self.data_processor.data = data
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Normalized columns using {method} scaling: {columns}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error normalizing columns: {str(e)}")
            return False
    
    def convert_data_types(self, type_mapping: Dict[str, str]) -> bool:
        """Convert column data types"""
        try:
            if self.data_processor.data is None:
                return False
            
            data = self.data_processor.data.copy()
            
            for column, new_type in type_mapping.items():
                if column not in data.columns:
                    continue
                
                try:
                    if new_type == 'numeric':
                        data[column] = pd.to_numeric(data[column], errors='coerce')
                    elif new_type == 'datetime':
                        data[column] = pd.to_datetime(data[column], errors='coerce')
                    elif new_type == 'category':
                        data[column] = data[column].astype('category')
                    elif new_type == 'string':
                        data[column] = data[column].astype('string')
                    else:
                        data[column] = data[column].astype(new_type)
                        
                except Exception as e:
                    self.logger.warning(f"Could not convert {column} to {new_type}: {str(e)}")
            
            self.data_processor.data = data
            self.data_processor._update_metadata()
            self.data_processor._log_action(f"Converted data types: {type_mapping}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting data types: {str(e)}")
            return False
    
    def auto_clean(self) -> Dict[str, Any]:
        """Perform automatic data cleaning with sensible defaults"""
        try:
            if self.data_processor.data is None:
                return {}
            
            results = {}
            
            # 1. Remove duplicates
            duplicate_result = self.remove_duplicates()
            results['duplicates_removed'] = duplicate_result
            
            # 2. Handle missing values with smart defaults
            missing_strategy = {}
            for col in self.data_processor.data.columns:
                missing_count = self.data_processor.data[col].isnull().sum()
                if missing_count > 0:
                    if col in self.data_processor.metadata['numeric_columns']:
                        # Use median for numeric columns
                        missing_strategy[col] = 'median'
                    else:
                        # Use mode for categorical columns
                        missing_strategy[col] = 'mode'
            
            if missing_strategy:
                missing_result = self.handle_missing_values(missing_strategy)
                results['missing_values_handled'] = missing_result
            
            # 3. Detect outliers (but don't remove automatically)
            outlier_counts = self.detect_and_handle_outliers(method='iqr')
            results['outliers_detected'] = outlier_counts
            
            # 4. Convert data types where obvious
            type_conversions = {}
            for col in self.data_processor.data.columns:
                if col in self.data_processor.metadata['categorical_columns']:
                    # Try to convert string columns that look like numbers
                    try:
                        pd.to_numeric(self.data_processor.data[col].dropna(), errors='raise')
                        type_conversions[col] = 'numeric'
                    except:
                        pass
            
            if type_conversions:
                type_result = self.convert_data_types(type_conversions)
                results['types_converted'] = type_result
            
            results['auto_clean_completed'] = True
            self.data_processor._log_action("Completed automatic data cleaning")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in auto clean: {str(e)}")
            return {'error': str(e)}
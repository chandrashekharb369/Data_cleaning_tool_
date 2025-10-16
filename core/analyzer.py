"""
Data Analyzer - Advanced data analysis and insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import LabelEncoder
import logging

class DataAnalyzer:
    """Advanced data analysis functionality"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.logger = logging.getLogger(__name__)
    
    def correlation_analysis(self, method: str = 'pearson') -> Dict[str, Any]:
        """Perform correlation analysis on numeric columns"""
        try:
            if self.data_processor.data is None:
                return {}
            
            numeric_data = self.data_processor.data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {'error': 'No numeric columns found for correlation analysis'}
            
            # Calculate correlation matrix
            correlation_matrix = numeric_data.corr(method=method)
            
            # Find highly correlated pairs
            high_corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Threshold for high correlation
                        high_corr_pairs.append({
                            'variable1': correlation_matrix.columns[i],
                            'variable2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            # Sort by absolute correlation value
            high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            return {
                'correlation_matrix': correlation_matrix,
                'high_correlations': high_corr_pairs,
                'method': method,
                'summary': {
                    'total_pairs': len(high_corr_pairs),
                    'max_correlation': max([abs(pair['correlation']) for pair in high_corr_pairs]) if high_corr_pairs else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {str(e)}")
            return {'error': str(e)}
    
    def feature_importance_analysis(self, target_column: str, problem_type: str = 'auto') -> Dict[str, Any]:
        """
        Analyze feature importance using Random Forest
        
        problem_type: 'regression', 'classification', or 'auto'
        """
        try:
            if self.data_processor.data is None or target_column not in self.data_processor.data.columns:
                return {'error': 'Invalid target column or no data available'}
            
            data = self.data_processor.data.copy()
            
            # Prepare features (numeric only for simplicity)
            feature_columns = [col for col in data.select_dtypes(include=[np.number]).columns 
                             if col != target_column]
            
            if len(feature_columns) == 0:
                return {'error': 'No numeric features found for analysis'}
            
            X = data[feature_columns].fillna(data[feature_columns].mean())
            y = data[target_column].fillna(data[target_column].mean() if data[target_column].dtype in ['int64', 'float64'] 
                                         else data[target_column].mode()[0] if len(data[target_column].mode()) > 0 else 0)
            
            # Determine problem type
            if problem_type == 'auto':
                unique_values = data[target_column].nunique()
                if data[target_column].dtype in ['int64', 'float64'] and unique_values > 10:
                    problem_type = 'regression'
                else:
                    problem_type = 'classification'
            
            # Train model and get feature importance
            if problem_type == 'regression':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                # For classification, encode target if necessary
                if data[target_column].dtype == 'object':
                    le = LabelEncoder()
                    y = le.fit_transform(y.astype(str))
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            model.fit(X, y)
            feature_importance = model.feature_importances_
            
            # Create feature importance ranking
            importance_df = pd.DataFrame({
                'feature': feature_columns,
                'importance': feature_importance
            }).sort_values('importance', ascending=False)
            
            # Calculate mutual information
            if problem_type == 'regression':
                mi_scores = mutual_info_regression(X, y, random_state=42)
            else:
                mi_scores = mutual_info_classif(X, y, random_state=42)
            
            mutual_info_df = pd.DataFrame({
                'feature': feature_columns,
                'mutual_info': mi_scores
            }).sort_values('mutual_info', ascending=False)
            
            return {
                'problem_type': problem_type,
                'feature_importance': importance_df,
                'mutual_information': mutual_info_df,
                'top_features': list(importance_df.head(5)['feature']),
                'model_score': model.score(X, y)
            }
            
        except Exception as e:
            self.logger.error(f"Error in feature importance analysis: {str(e)}")
            return {'error': str(e)}
    
    def data_quality_assessment(self) -> Dict[str, Any]:
        """Comprehensive data quality assessment"""
        try:
            if self.data_processor.data is None:
                return {}
            
            data = self.data_processor.data
            assessment = {}
            
            # Completeness
            total_cells = data.shape[0] * data.shape[1]
            missing_cells = data.isnull().sum().sum()
            completeness = ((total_cells - missing_cells) / total_cells) * 100
            
            # Consistency (detect potential inconsistencies)
            consistency_issues = []
            for col in data.select_dtypes(include=['object']).columns:
                # Check for similar values that might be inconsistent
                values = data[col].dropna().astype(str).str.lower().value_counts()
                similar_values = []
                for i, val1 in enumerate(values.index):
                    for val2 in values.index[i+1:]:
                        if self._similarity_score(val1, val2) > 0.8:  # High similarity threshold
                            similar_values.append((val1, val2))
                
                if similar_values:
                    consistency_issues.append({
                        'column': col,
                        'similar_values': similar_values[:5]  # Limit to top 5
                    })
            
            # Validity (basic checks)
            validity_issues = []
            for col in data.columns:
                col_issues = []
                
                # Check for negative values where they shouldn't be
                if col.lower() in ['age', 'price', 'count', 'quantity', 'amount']:
                    if data[col].dtype in ['int64', 'float64']:
                        negative_count = (data[col] < 0).sum()
                        if negative_count > 0:
                            col_issues.append(f"{negative_count} negative values")
                
                # Check for unrealistic values
                if data[col].dtype in ['int64', 'float64']:
                    q99 = data[col].quantile(0.99)
                    extreme_values = (data[col] > q99 * 10).sum()
                    if extreme_values > 0:
                        col_issues.append(f"{extreme_values} extreme outliers")
                
                if col_issues:
                    validity_issues.append({
                        'column': col,
                        'issues': col_issues
                    })
            
            # Uniqueness
            uniqueness_stats = {}
            for col in data.columns:
                unique_ratio = data[col].nunique() / len(data)
                uniqueness_stats[col] = {
                    'unique_count': data[col].nunique(),
                    'unique_ratio': unique_ratio,
                    'is_potentially_unique_id': unique_ratio > 0.95 and data[col].nunique() > 100
                }
            
            assessment = {
                'completeness': {
                    'percentage': completeness,
                    'missing_cells': missing_cells,
                    'total_cells': total_cells
                },
                'consistency': {
                    'issues_found': len(consistency_issues),
                    'details': consistency_issues
                },
                'validity': {
                    'issues_found': len(validity_issues),
                    'details': validity_issues
                },
                'uniqueness': uniqueness_stats,
                'overall_score': self._calculate_quality_score(completeness, consistency_issues, validity_issues)
            }
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error in data quality assessment: {str(e)}")
            return {'error': str(e)}
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Jaccard similarity"""
        try:
            set1 = set(str1.split())
            set2 = set(str2.split())
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            return intersection / union if union > 0 else 0
        except:
            return 0
    
    def _calculate_quality_score(self, completeness: float, consistency_issues: List, validity_issues: List) -> float:
        """Calculate overall data quality score (0-100)"""
        try:
            # Start with completeness score
            score = completeness
            
            # Deduct points for consistency issues
            consistency_penalty = min(len(consistency_issues) * 5, 20)  # Max 20 points deduction
            score -= consistency_penalty
            
            # Deduct points for validity issues
            validity_penalty = min(len(validity_issues) * 3, 15)  # Max 15 points deduction
            score -= validity_penalty
            
            return max(0, min(100, score))
        except:
            return 0
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate AI-assisted insights about the data"""
        try:
            if self.data_processor.data is None:
                return {}
            
            data = self.data_processor.data
            insights = []
            
            # Basic insights
            insights.append(f"Dataset contains {data.shape[0]:,} rows and {data.shape[1]} columns")
            
            # Missing data insights
            missing_cols = [col for col, count in self.data_processor.metadata['missing_values'].items() if count > 0]
            if missing_cols:
                worst_col = max(missing_cols, key=lambda x: self.data_processor.metadata['missing_values'][x])
                missing_pct = (self.data_processor.metadata['missing_values'][worst_col] / data.shape[0]) * 100
                insights.append(f"Column '{worst_col}' has the most missing values ({missing_pct:.1f}%)")
            
            # Duplicate insights
            if self.data_processor.metadata['duplicates'] > 0:
                dup_pct = (self.data_processor.metadata['duplicates'] / data.shape[0]) * 100
                insights.append(f"Found {self.data_processor.metadata['duplicates']} duplicate rows ({dup_pct:.1f}%)")
            
            # Data type insights
            numeric_cols = len(self.data_processor.metadata['numeric_columns'])
            categorical_cols = len(self.data_processor.metadata['categorical_columns'])
            insights.append(f"Data mix: {numeric_cols} numeric and {categorical_cols} categorical columns")
            
            # Correlation insights
            correlation_result = self.correlation_analysis()
            if 'high_correlations' in correlation_result and correlation_result['high_correlations']:
                top_corr = correlation_result['high_correlations'][0]
                insights.append(f"Highest correlation: {top_corr['variable1']} and {top_corr['variable2']} ({top_corr['correlation']:.3f})")
            
            # Memory usage insight
            memory_mb = self.data_processor.metadata['memory_usage'] / (1024 * 1024)
            insights.append(f"Dataset memory usage: {memory_mb:.2f} MB")
            
            # Recommendations
            recommendations = []
            
            if missing_cols:
                recommendations.append("Consider handling missing values before analysis")
            
            if self.data_processor.metadata['duplicates'] > 0:
                recommendations.append("Remove duplicate rows to improve data quality")
            
            if len(self.data_processor.metadata['categorical_columns']) > 0:
                recommendations.append("Consider creating dummy variables for categorical data")
            
            # Check for potential outliers
            for col in self.data_processor.metadata['numeric_columns']:
                if data[col].std() > 0:  # Avoid division by zero
                    z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                    outliers = (z_scores > 3).sum()
                    if outliers > data.shape[0] * 0.05:  # More than 5% outliers
                        recommendations.append(f"Column '{col}' has many potential outliers - consider outlier treatment")
                        break
            
            return {
                'key_insights': insights,
                'recommendations': recommendations,
                'data_summary': self.data_processor.get_data_summary(),
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {'error': str(e)}
    
    def statistical_summary(self) -> Dict[str, Any]:
        """Generate comprehensive statistical summary"""
        try:
            if self.data_processor.data is None:
                return {}
            
            data = self.data_processor.data
            summary = {}
            
            # Numeric columns summary
            numeric_summary = data.describe()
            summary['numeric_statistics'] = numeric_summary
            
            # Categorical columns summary
            categorical_summary = {}
            for col in self.data_processor.metadata['categorical_columns']:
                categorical_summary[col] = {
                    'unique_values': data[col].nunique(),
                    'top_value': data[col].mode().iloc[0] if len(data[col].mode()) > 0 else None,
                    'top_value_frequency': data[col].value_counts().iloc[0] if len(data[col].value_counts()) > 0 else 0,
                    'value_counts': data[col].value_counts().head(10).to_dict()
                }
            
            summary['categorical_statistics'] = categorical_summary
            
            # Distribution characteristics
            distribution_analysis = {}
            for col in self.data_processor.metadata['numeric_columns']:
                if data[col].std() > 0:  # Avoid division by zero
                    skewness = data[col].skew()
                    kurtosis = data[col].kurtosis()
                    distribution_analysis[col] = {
                        'skewness': skewness,
                        'kurtosis': kurtosis,
                        'distribution_type': self._classify_distribution(skewness, kurtosis)
                    }
            
            summary['distribution_analysis'] = distribution_analysis
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in statistical summary: {str(e)}")
            return {'error': str(e)}
    
    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """Classify distribution based on skewness and kurtosis"""
        if abs(skewness) < 0.5:
            skew_type = "approximately symmetric"
        elif skewness > 0.5:
            skew_type = "right-skewed"
        else:
            skew_type = "left-skewed"
        
        if kurtosis < -1:
            kurt_type = "platykurtic (flat)"
        elif kurtosis > 1:
            kurt_type = "leptokurtic (peaked)"
        else:
            kurt_type = "mesokurtic (normal-like)"
        
        return f"{skew_type}, {kurt_type}"
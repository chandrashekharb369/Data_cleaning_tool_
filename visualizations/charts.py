"""
Charts - Chart generation for data visualization
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path

class ChartGenerator:
    """Generate various charts for data visualization"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.logger = logging.getLogger(__name__)
        
        # Set up matplotlib and seaborn styling
        plt.style.use('default')
        sns.set_palette("husl")
        
    def create_correlation_heatmap(self, figsize: Tuple[int, int] = (10, 8), save_path: Optional[str] = None) -> bool:
        """Create correlation heatmap for numeric columns"""
        try:
            if self.data_processor.data is None:
                return False
            
            numeric_data = self.data_processor.data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                self.logger.warning("No numeric columns found for correlation heatmap")
                return False
            
            # Calculate correlation matrix
            correlation_matrix = numeric_data.corr()
            
            # Create heatmap
            plt.figure(figsize=figsize)
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            
            sns.heatmap(
                correlation_matrix,
                mask=mask,
                annot=True,
                cmap='coolwarm',
                center=0,
                square=True,
                fmt='.2f',
                cbar_kws={"shrink": .8}
            )
            
            plt.title('Correlation Matrix Heatmap', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating correlation heatmap: {str(e)}")
            return False
    
    def create_distribution_plots(self, columns: Optional[List[str]] = None, 
                                figsize: Tuple[int, int] = (15, 10), 
                                save_path: Optional[str] = None) -> bool:
        """Create distribution plots for numeric columns"""
        try:
            if self.data_processor.data is None:
                return False
            
            if columns is None:
                columns = self.data_processor.metadata['numeric_columns']
            
            if not columns:
                self.logger.warning("No numeric columns found for distribution plots")
                return False
            
            # Calculate grid size
            n_cols = min(3, len(columns))
            n_rows = (len(columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            for i, column in enumerate(columns):
                if i < len(axes):
                    data_to_plot = self.data_processor.data[column].dropna()
                    
                    # Create histogram with KDE
                    sns.histplot(data_to_plot, kde=True, ax=axes[i], stat='density')
                    axes[i].set_title(f'Distribution of {column}', fontweight='bold')
                    axes[i].set_xlabel(column)
                    axes[i].set_ylabel('Density')
            
            # Hide empty subplots
            for i in range(len(columns), len(axes)):
                axes[i].set_visible(False)
            
            plt.suptitle('Data Distribution Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating distribution plots: {str(e)}")
            return False
    
    def create_missing_data_chart(self, figsize: Tuple[int, int] = (12, 6), 
                                save_path: Optional[str] = None) -> bool:
        """Create missing data visualization"""
        try:
            if self.data_processor.data is None:
                return False
            
            missing_data = self.data_processor.data.isnull().sum()
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
            
            if missing_data.empty:
                self.logger.info("No missing data found")
                return False
            
            # Calculate missing percentage
            missing_percentage = (missing_data / len(self.data_processor.data)) * 100
            
            # Create bar plot
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            # Missing count
            missing_data.plot(kind='bar', ax=ax1, color='salmon')
            ax1.set_title('Missing Values Count', fontweight='bold')
            ax1.set_xlabel('Columns')
            ax1.set_ylabel('Missing Count')
            ax1.tick_params(axis='x', rotation=45)
            
            # Missing percentage
            missing_percentage.plot(kind='bar', ax=ax2, color='lightcoral')
            ax2.set_title('Missing Values Percentage', fontweight='bold')
            ax2.set_xlabel('Columns')
            ax2.set_ylabel('Missing Percentage (%)')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.suptitle('Missing Data Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating missing data chart: {str(e)}")
            return False
    
    def create_categorical_charts(self, columns: Optional[List[str]] = None, 
                                max_categories: int = 10,
                                figsize: Tuple[int, int] = (15, 10),
                                save_path: Optional[str] = None) -> bool:
        """Create bar charts for categorical columns"""
        try:
            if self.data_processor.data is None:
                return False
            
            if columns is None:
                columns = self.data_processor.metadata['categorical_columns']
            
            if not columns:
                self.logger.warning("No categorical columns found")
                return False
            
            # Filter columns with reasonable number of categories
            columns = [col for col in columns 
                      if self.data_processor.data[col].nunique() <= max_categories]
            
            if not columns:
                self.logger.warning("No categorical columns with reasonable number of categories")
                return False
            
            # Calculate grid size
            n_cols = min(2, len(columns))
            n_rows = (len(columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            for i, column in enumerate(columns):
                if i < len(axes):
                    value_counts = self.data_processor.data[column].value_counts().head(max_categories)
                    
                    value_counts.plot(kind='bar', ax=axes[i], color='skyblue')
                    axes[i].set_title(f'Distribution of {column}', fontweight='bold')
                    axes[i].set_xlabel(column)
                    axes[i].set_ylabel('Count')
                    axes[i].tick_params(axis='x', rotation=45)
            
            # Hide empty subplots
            for i in range(len(columns), len(axes)):
                axes[i].set_visible(False)
            
            plt.suptitle('Categorical Data Distribution', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating categorical charts: {str(e)}")
            return False
    
    def create_outlier_boxplots(self, columns: Optional[List[str]] = None,
                              figsize: Tuple[int, int] = (15, 8),
                              save_path: Optional[str] = None) -> bool:
        """Create box plots to visualize outliers"""
        try:
            if self.data_processor.data is None:
                return False
            
            if columns is None:
                columns = self.data_processor.metadata['numeric_columns']
            
            if not columns:
                self.logger.warning("No numeric columns found for box plots")
                return False
            
            # Limit to first 6 columns for readability
            columns = columns[:6]
            
            fig, axes = plt.subplots(2, 3, figsize=figsize)
            axes = axes.flatten()
            
            for i, column in enumerate(columns):
                if i < len(axes):
                    self.data_processor.data.boxplot(column=column, ax=axes[i])
                    axes[i].set_title(f'Box Plot: {column}', fontweight='bold')
                    axes[i].set_ylabel(column)
            
            # Hide empty subplots
            for i in range(len(columns), len(axes)):
                axes[i].set_visible(False)
            
            plt.suptitle('Outlier Detection - Box Plots', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating outlier box plots: {str(e)}")
            return False
    
    def create_data_overview_chart(self, figsize: Tuple[int, int] = (12, 8),
                                 save_path: Optional[str] = None) -> bool:
        """Create comprehensive data overview chart"""
        try:
            if self.data_processor.data is None:
                return False
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # 1. Data types distribution
            type_counts = {
                'Numeric': len(self.data_processor.metadata['numeric_columns']),
                'Categorical': len(self.data_processor.metadata['categorical_columns'])
            }
            ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
                   colors=['lightblue', 'lightcoral'])
            ax1.set_title('Column Types Distribution', fontweight='bold')
            
            # 2. Missing data overview
            missing_data = self.data_processor.data.isnull().sum()
            non_missing = len(self.data_processor.data) - missing_data
            
            if missing_data.sum() > 0:
                missing_summary = {
                    'Complete': non_missing.sum(),
                    'Missing': missing_data.sum()
                }
                ax2.pie(missing_summary.values(), labels=missing_summary.keys(), 
                       autopct='%1.1f%%', colors=['lightgreen', 'salmon'])
            else:
                ax2.text(0.5, 0.5, 'No Missing Data', ha='center', va='center',
                        transform=ax2.transAxes, fontsize=14, fontweight='bold')
            ax2.set_title('Data Completeness', fontweight='bold')
            
            # 3. Dataset size info
            size_info = [
                f"Rows: {self.data_processor.data.shape[0]:,}",
                f"Columns: {self.data_processor.data.shape[1]}",
                f"Memory: {self.data_processor.metadata['memory_usage']/1024:.1f} KB",
                f"Duplicates: {self.data_processor.metadata['duplicates']}"
            ]
            ax3.text(0.1, 0.9, '\n'.join(size_info), transform=ax3.transAxes,
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            ax3.set_title('Dataset Information', fontweight='bold')
            ax3.axis('off')
            
            # 4. Column names (first 10)
            columns_text = '\n'.join(self.data_processor.data.columns[:10])
            if len(self.data_processor.data.columns) > 10:
                columns_text += f'\n... and {len(self.data_processor.data.columns) - 10} more'
            
            ax4.text(0.1, 0.9, columns_text, transform=ax4.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax4.set_title('Column Names', fontweight='bold')
            ax4.axis('off')
            
            plt.suptitle('Data Overview Dashboard', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating data overview chart: {str(e)}")
            return False
    
    def save_all_charts(self, output_dir: str) -> Dict[str, bool]:
        """Generate and save all available charts"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results = {}
            
            # Generate all charts
            chart_functions = [
                ('correlation_heatmap', self.create_correlation_heatmap),
                ('distribution_plots', self.create_distribution_plots),
                ('missing_data_chart', self.create_missing_data_chart),
                ('categorical_charts', self.create_categorical_charts),
                ('outlier_boxplots', self.create_outlier_boxplots),
                ('data_overview', self.create_data_overview_chart)
            ]
            
            for chart_name, chart_function in chart_functions:
                save_path = output_path / f"{chart_name}.png"
                try:
                    results[chart_name] = chart_function(save_path=str(save_path))
                    plt.close('all')  # Close all figures to free memory
                except Exception as e:
                    self.logger.error(f"Error creating {chart_name}: {str(e)}")
                    results[chart_name] = False
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error saving all charts: {str(e)}")
            return {}
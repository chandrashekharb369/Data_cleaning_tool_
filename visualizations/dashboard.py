"""
Dashboard - Interactive visualization dashboard
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

class VisualizationDashboard:
    """Interactive visualization dashboard for data exploration"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.logger = logging.getLogger(__name__)
        self.current_figure = None
        
        # Set up styling
        plt.style.use('default')
        sns.set_palette("husl")
    
    def create_dashboard_figure(self, chart_type: str, **kwargs) -> plt.Figure:
        """Create a figure for the dashboard based on chart type"""
        try:
            if self.data_processor.data is None:
                return self._create_empty_figure("No data loaded")
            
            if chart_type == 'overview':
                return self._create_overview_dashboard()
            elif chart_type == 'correlation':
                return self._create_correlation_dashboard()
            elif chart_type == 'distribution':
                return self._create_distribution_dashboard(**kwargs)
            elif chart_type == 'missing':
                return self._create_missing_data_dashboard()
            elif chart_type == 'categorical':
                return self._create_categorical_dashboard(**kwargs)
            elif chart_type == 'outliers':
                return self._create_outliers_dashboard()
            else:
                return self._create_empty_figure("Unknown chart type")
                
        except Exception as e:
            self.logger.error(f"Error creating dashboard figure: {str(e)}")
            return self._create_empty_figure(f"Error: {str(e)}")
    
    def _create_empty_figure(self, message: str) -> plt.Figure:
        """Create an empty figure with a message"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, fontsize=16, fontweight='bold')
        ax.axis('off')
        return fig
    
    def _create_overview_dashboard(self) -> plt.Figure:
        """Create comprehensive overview dashboard"""
        fig = plt.figure(figsize=(12, 8))
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Dataset info
        ax1 = fig.add_subplot(gs[0, 0])
        info_text = [
            f"Rows: {self.data_processor.data.shape[0]:,}",
            f"Columns: {self.data_processor.data.shape[1]}",
            f"Memory: {self.data_processor.metadata['memory_usage']/1024:.1f} KB",
            f"Duplicates: {self.data_processor.metadata['duplicates']}",
            f"Missing cells: {self.data_processor.data.isnull().sum().sum():,}"
        ]
        ax1.text(0.1, 0.9, '\n'.join(info_text), transform=ax1.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax1.set_title('Dataset Summary', fontweight='bold')
        ax1.axis('off')
        
        # 2. Column types
        ax2 = fig.add_subplot(gs[0, 1])
        type_counts = {
            'Numeric': len(self.data_processor.metadata['numeric_columns']),
            'Categorical': len(self.data_processor.metadata['categorical_columns'])
        }
        if sum(type_counts.values()) > 0:
            ax2.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
                   colors=['lightblue', 'lightcoral'])
        ax2.set_title('Column Types', fontweight='bold')
        
        # 3. Data completeness
        ax3 = fig.add_subplot(gs[0, 2])
        total_cells = self.data_processor.data.shape[0] * self.data_processor.data.shape[1]
        missing_cells = self.data_processor.data.isnull().sum().sum()
        complete_cells = total_cells - missing_cells
        
        completeness_data = {'Complete': complete_cells, 'Missing': missing_cells}
        if missing_cells > 0:
            ax3.pie(completeness_data.values(), labels=completeness_data.keys(),
                   autopct='%1.1f%%', colors=['lightgreen', 'salmon'])
        else:
            ax3.text(0.5, 0.5, 'Complete Data\n100%', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        ax3.set_title('Data Completeness', fontweight='bold')
        
        # 4. Missing data by column (if any)
        ax4 = fig.add_subplot(gs[1, :])
        missing_by_col = self.data_processor.data.isnull().sum()
        missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=True)
        
        if not missing_by_col.empty:
            missing_by_col.plot(kind='barh', ax=ax4, color='salmon')
            ax4.set_title('Missing Values by Column', fontweight='bold')
            ax4.set_xlabel('Missing Count')
        else:
            ax4.text(0.5, 0.5, 'No Missing Data Found', ha='center', va='center',
                    transform=ax4.transAxes, fontsize=14, fontweight='bold')
            ax4.axis('off')
        
        plt.suptitle('Data Overview Dashboard', fontsize=16, fontweight='bold')
        return fig
    
    def _create_correlation_dashboard(self) -> plt.Figure:
        """Create correlation analysis dashboard"""
        numeric_data = self.data_processor.data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            return self._create_empty_figure("No numeric columns for correlation analysis")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Correlation heatmap
        correlation_matrix = numeric_data.corr()
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm',
                   center=0, square=True, fmt='.2f', ax=ax1, cbar_kws={"shrink": .8})
        ax1.set_title('Correlation Matrix', fontweight='bold')
        
        # High correlations
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:
                    high_corr_pairs.append({
                        'pair': f"{correlation_matrix.columns[i]} - {correlation_matrix.columns[j]}",
                        'correlation': corr_value
                    })
        
        if high_corr_pairs:
            high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
            pairs = [pair['pair'] for pair in high_corr_pairs[:10]]
            correlations = [pair['correlation'] for pair in high_corr_pairs[:10]]
            
            colors = ['red' if abs(c) > 0.8 else 'orange' if abs(c) > 0.6 else 'yellow' for c in correlations]
            ax2.barh(pairs, correlations, color=colors)
            ax2.set_title('High Correlations (|r| > 0.5)', fontweight='bold')
            ax2.set_xlabel('Correlation Coefficient')
        else:
            ax2.text(0.5, 0.5, 'No High Correlations Found', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=12, fontweight='bold')
            ax2.axis('off')
        
        plt.suptitle('Correlation Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def _create_distribution_dashboard(self, columns: Optional[List[str]] = None) -> plt.Figure:
        """Create distribution analysis dashboard"""
        if columns is None:
            columns = self.data_processor.metadata['numeric_columns'][:6]  # Limit to 6 for readability
        
        if not columns:
            return self._create_empty_figure("No numeric columns for distribution analysis")
        
        n_cols = min(3, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
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
                axes[i].set_title(f'{column}\nMean: {data_to_plot.mean():.2f}, Std: {data_to_plot.std():.2f}',
                                fontweight='bold')
                axes[i].set_xlabel(column)
                axes[i].set_ylabel('Density')
        
        # Hide empty subplots
        for i in range(len(columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Distribution Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def _create_missing_data_dashboard(self) -> plt.Figure:
        """Create missing data analysis dashboard"""
        missing_data = self.data_processor.data.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if missing_data.empty:
            return self._create_empty_figure("No missing data found")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Missing count
        missing_data.plot(kind='bar', ax=ax1, color='salmon')
        ax1.set_title('Missing Values Count by Column', fontweight='bold')
        ax1.set_xlabel('Columns')
        ax1.set_ylabel('Missing Count')
        ax1.tick_params(axis='x', rotation=45)
        
        # Missing percentage
        missing_percentage = (missing_data / len(self.data_processor.data)) * 100
        missing_percentage.plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('Missing Values Percentage by Column', fontweight='bold')
        ax2.set_xlabel('Columns')
        ax2.set_ylabel('Missing Percentage (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.suptitle('Missing Data Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def _create_categorical_dashboard(self, columns: Optional[List[str]] = None, max_categories: int = 10) -> plt.Figure:
        """Create categorical data analysis dashboard"""
        if columns is None:
            columns = self.data_processor.metadata['categorical_columns']
        
        # Filter columns with reasonable number of categories
        columns = [col for col in columns 
                  if self.data_processor.data[col].nunique() <= max_categories][:4]  # Limit to 4
        
        if not columns:
            return self._create_empty_figure("No categorical columns with reasonable number of categories")
        
        n_cols = min(2, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 6*n_rows))
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
                axes[i].set_title(f'{column}\nUnique Values: {self.data_processor.data[column].nunique()}',
                                fontweight='bold')
                axes[i].set_xlabel(column)
                axes[i].set_ylabel('Count')
                axes[i].tick_params(axis='x', rotation=45)
        
        # Hide empty subplots
        for i in range(len(columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Categorical Data Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def _create_outliers_dashboard(self) -> plt.Figure:
        """Create outlier detection dashboard"""
        numeric_columns = self.data_processor.metadata['numeric_columns'][:6]  # Limit to 6
        
        if not numeric_columns:
            return self._create_empty_figure("No numeric columns for outlier analysis")
        
        n_cols = min(3, len(numeric_columns))
        n_rows = (len(numeric_columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        for i, column in enumerate(numeric_columns):
            if i < len(axes):
                # Create box plot
                self.data_processor.data.boxplot(column=column, ax=axes[i])
                
                # Calculate outlier statistics
                Q1 = self.data_processor.data[column].quantile(0.25)
                Q3 = self.data_processor.data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((self.data_processor.data[column] < lower_bound) | 
                           (self.data_processor.data[column] > upper_bound)).sum()
                
                axes[i].set_title(f'{column}\nOutliers: {outliers} ({outliers/len(self.data_processor.data)*100:.1f}%)',
                                fontweight='bold')
                axes[i].set_ylabel(column)
        
        # Hide empty subplots
        for i in range(len(numeric_columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Outlier Detection Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def create_canvas_widget(self, parent, chart_type: str, **kwargs) -> FigureCanvasTkAgg:
        """Create a Tkinter canvas widget with the specified chart"""
        try:
            # Clear previous figure if exists
            if self.current_figure:
                plt.close(self.current_figure)
            
            # Create new figure
            self.current_figure = self.create_dashboard_figure(chart_type, **kwargs)
            
            # Create canvas
            canvas = FigureCanvasTkAgg(self.current_figure, parent)
            canvas.draw()
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Error creating canvas widget: {str(e)}")
            # Return empty canvas on error
            fig = self._create_empty_figure(f"Error creating chart: {str(e)}")
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            return canvas
    
    def update_chart(self, canvas: FigureCanvasTkAgg, chart_type: str, **kwargs):
        """Update existing chart canvas"""
        try:
            # Clear previous figure
            if self.current_figure:
                plt.close(self.current_figure)
            
            # Create new figure
            self.current_figure = self.create_dashboard_figure(chart_type, **kwargs)
            
            # Update canvas
            canvas.figure = self.current_figure
            canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error updating chart: {str(e)}")
    
    def close_figures(self):
        """Close all figures to free memory"""
        try:
            if self.current_figure:
                plt.close(self.current_figure)
                self.current_figure = None
            plt.close('all')
        except Exception as e:
            self.logger.error(f"Error closing figures: {str(e)}")
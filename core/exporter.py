"""
Data Exporter - Export functionality for processed data
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class DataExporter:
    """Export functionality for Smart Data Cleaner"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.logger = logging.getLogger(__name__)
    
    def export_to_csv(self, file_path: str, include_index: bool = False) -> bool:
        """Export data to CSV file"""
        try:
            if self.data_processor.data is None:
                self.logger.error("No data available for export")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.data_processor.data.to_csv(file_path, index=include_index)
            
            self.data_processor._log_action(f"Exported data to CSV: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_to_excel(self, file_path: str, sheet_name: str = 'Data', include_index: bool = False) -> bool:
        """Export data to Excel file"""
        try:
            if self.data_processor.data is None:
                self.logger.error("No data available for export")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                self.data_processor.data.to_excel(writer, sheet_name=sheet_name, index=include_index)
            
            self.data_processor._log_action(f"Exported data to Excel: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            return False
    
    def export_to_json(self, file_path: str, orient: str = 'records') -> bool:
        """Export data to JSON file"""
        try:
            if self.data_processor.data is None:
                self.logger.error("No data available for export")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert data to JSON
            json_data = self.data_processor.data.to_json(orient=orient, date_format='iso')
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            self.data_processor._log_action(f"Exported data to JSON: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_summary_report(self, file_path: str, include_analysis: bool = True) -> bool:
        """Export comprehensive summary report"""
        try:
            if self.data_processor.data is None:
                self.logger.error("No data available for export")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Gather all information
            report = {
                'metadata': {
                    'generated_at': pd.Timestamp.now().isoformat(),
                    'original_shape': self.data_processor.original_data.shape if self.data_processor.original_data is not None else None,
                    'current_shape': self.data_processor.data.shape,
                    'processing_log': self.data_processor.get_processing_log()
                },
                'data_summary': self.data_processor.get_data_summary(),
                'column_info': self.data_processor.get_column_info()
            }
            
            # Add analysis if requested
            if include_analysis:
                from .analyzer import DataAnalyzer
                analyzer = DataAnalyzer(self.data_processor)
                
                report['analysis'] = {
                    'correlation_analysis': analyzer.correlation_analysis(),
                    'data_quality': analyzer.data_quality_assessment(),
                    'insights': analyzer.generate_insights(),
                    'statistical_summary': analyzer.statistical_summary()
                }
            
            # Convert to JSON and save
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.data_processor._log_action(f"Exported summary report: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting summary report: {str(e)}")
            return False
    
    def export_data_profile(self, file_path: str) -> bool:
        """Export detailed data profile using ydata-profiling"""
        try:
            if self.data_processor.data is None:
                self.logger.error("No data available for export")
                return False
            
            from ydata_profiling import ProfileReport
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate profile report
            profile = ProfileReport(
                self.data_processor.data,
                title="Smart Data Cleaner - Data Profile Report",
                explorative=True
            )
            
            # Save as HTML
            profile.to_file(file_path)
            
            self.data_processor._log_action(f"Exported data profile: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting data profile: {str(e)}")
            return False
    
    def export_multiple_formats(self, base_path: str, formats: List[str] = None) -> Dict[str, bool]:
        """Export data in multiple formats"""
        if formats is None:
            formats = ['csv', 'excel', 'json']
        
        results = {}
        base_path = Path(base_path)
        
        for format_type in formats:
            if format_type == 'csv':
                file_path = base_path.with_suffix('.csv')
                results['csv'] = self.export_to_csv(str(file_path))
            
            elif format_type == 'excel':
                file_path = base_path.with_suffix('.xlsx')
                results['excel'] = self.export_to_excel(str(file_path))
            
            elif format_type == 'json':
                file_path = base_path.with_suffix('.json')
                results['json'] = self.export_to_json(str(file_path))
            
            elif format_type == 'report':
                file_path = base_path.with_name(f"{base_path.stem}_report.json")
                results['report'] = self.export_summary_report(str(file_path))
            
            elif format_type == 'profile':
                file_path = base_path.with_name(f"{base_path.stem}_profile.html")
                results['profile'] = self.export_data_profile(str(file_path))
        
        return results
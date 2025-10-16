"""
Analysis Panel Component - Simplified
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.styles import *

class AnalysisPanel(ctk.CTkFrame):
    """Data analysis panel"""
    
    def __init__(self, parent, data_processor, data_analyzer):
        super().__init__(parent, **WIDGET_STYLES['frame'])
        
        self.data_processor = data_processor
        self.data_analyzer = data_analyzer
        
        self.setup_widgets()
        self.refresh_data()
    
    def setup_widgets(self):
        """Setup analysis panel widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['large'])
        
        title_label = ctk.CTkLabel(header_frame, text="📈 Data Analysis", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.pack(side="left")
        
        # Main content
        content_frame = create_styled_scrollable_frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT['padding']['large'], pady=(0, LAYOUT['padding']['large']))
        
        # Correlation Analysis
        corr_frame = create_styled_frame(content_frame)
        corr_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        corr_label = ctk.CTkLabel(corr_frame, text="Correlation Analysis", font=FONTS['subheading'])
        apply_label_style(corr_label, 'subheading')
        corr_label.pack(pady=LAYOUT['padding']['medium'])
        
        self.corr_btn = ctk.CTkButton(corr_frame, text="Run Correlation Analysis", command=self.run_correlation)
        apply_button_style(self.corr_btn, 'primary')
        self.corr_btn.pack(pady=LAYOUT['spacing']['small'])
        
        self.corr_results = ctk.CTkTextbox(corr_frame, height=150)
        self.corr_results.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        
        # Data Quality Assessment
        quality_frame = create_styled_frame(content_frame)
        quality_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        quality_label = ctk.CTkLabel(quality_frame, text="Data Quality Assessment", font=FONTS['subheading'])
        apply_label_style(quality_label, 'subheading')
        quality_label.pack(pady=LAYOUT['padding']['medium'])
        
        self.quality_btn = ctk.CTkButton(quality_frame, text="Assess Data Quality", command=self.assess_quality)
        apply_button_style(self.quality_btn, 'primary')
        self.quality_btn.pack(pady=LAYOUT['spacing']['small'])
        
        self.quality_results = ctk.CTkTextbox(quality_frame, height=200)
        self.quality_results.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        
        # Insights
        insights_frame = create_styled_frame(content_frame)
        insights_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        insights_label = ctk.CTkLabel(insights_frame, text="AI-Powered Insights", font=FONTS['subheading'])
        apply_label_style(insights_label, 'subheading')
        insights_label.pack(pady=LAYOUT['padding']['medium'])
        
        self.insights_btn = ctk.CTkButton(insights_frame, text="Generate Insights", command=self.generate_insights)
        apply_button_style(self.insights_btn, 'success')
        self.insights_btn.pack(pady=LAYOUT['spacing']['small'])
        
        self.insights_results = ctk.CTkTextbox(insights_frame, height=200)
        self.insights_results.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
    
    def refresh_data(self):
        """Refresh analysis panel"""
        has_data = self.data_processor.data is not None
        
        self.corr_btn.configure(state="normal" if has_data else "disabled")
        self.quality_btn.configure(state="normal" if has_data else "disabled")
        self.insights_btn.configure(state="normal" if has_data else "disabled")
        
        if not has_data:
            self.corr_results.delete("1.0", "end")
            self.corr_results.insert("1.0", "No data loaded")
            self.quality_results.delete("1.0", "end")
            self.quality_results.insert("1.0", "No data loaded")
            self.insights_results.delete("1.0", "end")
            self.insights_results.insert("1.0", "No data loaded")
    
    def run_correlation(self):
        """Run correlation analysis"""
        if self.data_processor.data is None:
            return
        
        def correlation_worker():
            try:
                self.corr_btn.configure(text="Running...", state="disabled")
                
                results = self.data_analyzer.correlation_analysis()
                
                if 'error' in results:
                    result_text = f"Error: {results['error']}"
                else:
                    result_text = f"Correlation Analysis Results:\n\n"
                    result_text += f"Method: {results.get('method', 'pearson')}\n"
                    result_text += f"High correlations found: {results['summary']['total_pairs']}\n\n"
                    
                    if results['high_correlations']:
                        result_text += "Top correlations (|r| > 0.7):\n"
                        for pair in results['high_correlations'][:10]:
                            result_text += f"• {pair['variable1']} ↔ {pair['variable2']}: {pair['correlation']:.3f}\n"
                    else:
                        result_text += "No high correlations found."
                
                self.after(0, lambda: self.corr_results.delete("1.0", "end"))
                self.after(0, lambda: self.corr_results.insert("1.0", result_text))
                
            except Exception as e:
                error_text = f"Error running correlation analysis: {str(e)}"
                self.after(0, lambda: self.corr_results.delete("1.0", "end"))
                self.after(0, lambda: self.corr_results.insert("1.0", error_text))
            finally:
                self.after(0, lambda: self.corr_btn.configure(text="Run Correlation Analysis", state="normal"))
        
        threading.Thread(target=correlation_worker, daemon=True).start()
    
    def assess_quality(self):
        """Assess data quality"""
        if self.data_processor.data is None:
            return
        
        def quality_worker():
            try:
                self.quality_btn.configure(text="Assessing...", state="disabled")
                
                results = self.data_analyzer.data_quality_assessment()
                
                if 'error' in results:
                    result_text = f"Error: {results['error']}"
                else:
                    result_text = "Data Quality Assessment:\n\n"
                    
                    # Completeness
                    completeness = results.get('completeness', {})
                    result_text += f"Data Completeness: {completeness.get('percentage', 0):.2f}%\n"
                    result_text += f"Missing cells: {completeness.get('missing_cells', 0):,}\n\n"
                    
                    # Consistency issues
                    consistency = results.get('consistency', {})
                    result_text += f"Consistency Issues: {consistency.get('issues_found', 0)}\n"
                    if consistency.get('details'):
                        for issue in consistency['details'][:3]:
                            result_text += f"• {issue['column']}: Similar values detected\n"
                    
                    result_text += "\n"
                    
                    # Validity issues
                    validity = results.get('validity', {})
                    result_text += f"Validity Issues: {validity.get('issues_found', 0)}\n"
                    if validity.get('details'):
                        for issue in validity['details'][:3]:
                            result_text += f"• {issue['column']}: {', '.join(issue['issues'])}\n"
                    
                    result_text += f"\nOverall Quality Score: {results.get('overall_score', 0):.1f}/100"
                
                self.after(0, lambda: self.quality_results.delete("1.0", "end"))
                self.after(0, lambda: self.quality_results.insert("1.0", result_text))
                
            except Exception as e:
                error_text = f"Error assessing data quality: {str(e)}"
                self.after(0, lambda: self.quality_results.delete("1.0", "end"))
                self.after(0, lambda: self.quality_results.insert("1.0", error_text))
            finally:
                self.after(0, lambda: self.quality_btn.configure(text="Assess Data Quality", state="normal"))
        
        threading.Thread(target=quality_worker, daemon=True).start()
    
    def generate_insights(self):
        """Generate AI-powered insights"""
        if self.data_processor.data is None:
            return
        
        def insights_worker():
            try:
                self.insights_btn.configure(text="Generating...", state="disabled")
                
                results = self.data_analyzer.generate_insights()
                
                if 'error' in results:
                    result_text = f"Error: {results['error']}"
                else:
                    result_text = "AI-Powered Data Insights:\n\n"
                    
                    # Key insights
                    insights = results.get('key_insights', [])
                    if insights:
                        result_text += "Key Insights:\n"
                        for insight in insights:
                            result_text += f"• {insight}\n"
                        result_text += "\n"
                    
                    # Recommendations
                    recommendations = results.get('recommendations', [])
                    if recommendations:
                        result_text += "Recommendations:\n"
                        for rec in recommendations:
                            result_text += f"• {rec}\n"
                        result_text += "\n"
                    
                    # Data summary
                    summary = results.get('data_summary', {})
                    if summary:
                        basic_info = summary.get('basic_info', {})
                        result_text += f"Dataset: {basic_info.get('rows', 0):,} rows, {basic_info.get('columns', 0)} columns\n"
                        result_text += f"Memory usage: {basic_info.get('memory_usage', 'Unknown')}\n"
                
                self.after(0, lambda: self.insights_results.delete("1.0", "end"))
                self.after(0, lambda: self.insights_results.insert("1.0", result_text))
                
            except Exception as e:
                error_text = f"Error generating insights: {str(e)}"
                self.after(0, lambda: self.insights_results.delete("1.0", "end"))
                self.after(0, lambda: self.insights_results.insert("1.0", error_text))
            finally:
                self.after(0, lambda: self.insights_btn.configure(text="Generate Insights", state="normal"))
        
        threading.Thread(target=insights_worker, daemon=True).start()
"""
Export Panel Component - Simplified
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.styles import *

class ExportPanel(ctk.CTkFrame):
    """Data export panel"""
    
    def __init__(self, parent, data_processor, data_exporter):
        super().__init__(parent, **WIDGET_STYLES['frame'])
        
        self.data_processor = data_processor
        self.data_exporter = data_exporter
        
        self.setup_widgets()
        self.refresh_data()
    
    def setup_widgets(self):
        """Setup export panel widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['large'])
        
        title_label = ctk.CTkLabel(header_frame, text="💾 Export Data", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.pack(side="left")
        
        # Main content
        content_frame = create_styled_scrollable_frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT['padding']['large'], pady=(0, LAYOUT['padding']['large']))
        
        # Data info
        info_frame = create_styled_frame(content_frame)
        info_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        info_label = ctk.CTkLabel(info_frame, text="Export Information", font=FONTS['subheading'])
        apply_label_style(info_label, 'subheading')
        info_label.pack(pady=LAYOUT['padding']['medium'])
        
        self.info_text = ctk.CTkTextbox(info_frame, height=100)
        self.info_text.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        
        # Export formats
        formats_frame = create_styled_frame(content_frame)
        formats_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        formats_label = ctk.CTkLabel(formats_frame, text="Export Formats", font=FONTS['subheading'])
        apply_label_style(formats_label, 'subheading')
        formats_label.pack(pady=LAYOUT['padding']['medium'])
        
        # CSV Export
        csv_frame = ctk.CTkFrame(formats_frame, fg_color="transparent")
        csv_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.csv_btn = ctk.CTkButton(csv_frame, text="📄 Export as CSV", command=self.export_csv)
        apply_button_style(self.csv_btn, 'primary')
        self.csv_btn.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        csv_desc = ctk.CTkLabel(csv_frame, text="Export cleaned data as CSV file", font=FONTS['body_small'])
        csv_desc.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        # Excel Export
        excel_frame = ctk.CTkFrame(formats_frame, fg_color="transparent")
        excel_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.excel_btn = ctk.CTkButton(excel_frame, text="📊 Export as Excel", command=self.export_excel)
        apply_button_style(self.excel_btn, 'primary')
        self.excel_btn.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        excel_desc = ctk.CTkLabel(excel_frame, text="Export cleaned data as Excel file", font=FONTS['body_small'])
        excel_desc.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        # JSON Export
        json_frame = ctk.CTkFrame(formats_frame, fg_color="transparent")
        json_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.json_btn = ctk.CTkButton(json_frame, text="🔗 Export as JSON", command=self.export_json)
        apply_button_style(self.json_btn, 'primary')
        self.json_btn.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        json_desc = ctk.CTkLabel(json_frame, text="Export cleaned data as JSON file", font=FONTS['body_small'])
        json_desc.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        # Report Export
        report_frame = create_styled_frame(content_frame)
        report_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        report_label = ctk.CTkLabel(report_frame, text="Analysis Reports", font=FONTS['subheading'])
        apply_label_style(report_label, 'subheading')
        report_label.pack(pady=LAYOUT['padding']['medium'])
        
        # Summary Report
        summary_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.summary_btn = ctk.CTkButton(summary_frame, text="📋 Export Summary Report", command=self.export_summary)
        apply_button_style(self.summary_btn, 'success')
        self.summary_btn.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        summary_desc = ctk.CTkLabel(summary_frame, text="Export comprehensive analysis report", font=FONTS['body_small'])
        summary_desc.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        # Data Profile
        profile_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        profile_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.profile_btn = ctk.CTkButton(profile_frame, text="📊 Export Data Profile", command=self.export_profile)
        apply_button_style(self.profile_btn, 'success')
        self.profile_btn.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        profile_desc = ctk.CTkLabel(profile_frame, text="Export detailed data profiling report (HTML)", font=FONTS['body_small'])
        profile_desc.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        # Multiple formats
        multi_frame = create_styled_frame(content_frame)
        multi_frame.pack(fill="x", pady=LAYOUT['spacing']['medium'])
        
        multi_label = ctk.CTkLabel(multi_frame, text="Batch Export", font=FONTS['subheading'])
        apply_label_style(multi_label, 'subheading')
        multi_label.pack(pady=LAYOUT['padding']['medium'])
        
        self.multi_btn = ctk.CTkButton(multi_frame, text="🚀 Export All Formats", command=self.export_multiple)
        apply_button_style(self.multi_btn, 'accent')
        self.multi_btn.pack(pady=LAYOUT['spacing']['small'])
        
        multi_desc = ctk.CTkLabel(multi_frame, text="Export data in CSV, Excel, JSON and generate reports", font=FONTS['body_small'])
        multi_desc.pack(pady=LAYOUT['spacing']['small'])
    
    def refresh_data(self):
        """Refresh export panel"""
        has_data = self.data_processor.data is not None
        
        # Enable/disable buttons
        buttons = [self.csv_btn, self.excel_btn, self.json_btn, self.summary_btn, self.profile_btn, self.multi_btn]
        for btn in buttons:
            btn.configure(state="normal" if has_data else "disabled")
        
        # Update info
        self.update_export_info()
    
    def update_export_info(self):
        """Update export information"""
        self.info_text.delete("1.0", "end")
        
        if self.data_processor.data is None:
            self.info_text.insert("1.0", "No data loaded")
            return
        
        info_lines = [
            f"Dataset ready for export:",
            f"• Rows: {len(self.data_processor.data):,}",
            f"• Columns: {len(self.data_processor.data.columns)}",
            f"• Memory usage: {self.data_processor.metadata['memory_usage'] / 1024:.2f} KB",
            f"• Missing values: {self.data_processor.data.isnull().sum().sum():,}",
            f"• Data types: {len(self.data_processor.metadata['numeric_columns'])} numeric, {len(self.data_processor.metadata['categorical_columns'])} categorical"
        ]
        
        self.info_text.insert("1.0", "\\n".join(info_lines))
    
    def export_csv(self):
        """Export data as CSV"""
        if self.data_processor.data is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(self.data_exporter.export_to_csv, file_path, "CSV")
    
    def export_excel(self):
        """Export data as Excel"""
        if self.data_processor.data is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export as Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(self.data_exporter.export_to_excel, file_path, "Excel")
    
    def export_json(self):
        """Export data as JSON"""
        if self.data_processor.data is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(self.data_exporter.export_to_json, file_path, "JSON")
    
    def export_summary(self):
        """Export summary report"""
        if self.data_processor.data is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Summary Report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(
                lambda path: self.data_exporter.export_summary_report(path, include_analysis=True), 
                file_path, 
                "Summary Report"
            )
    
    def export_profile(self):
        """Export data profile"""
        if self.data_processor.data is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Data Profile",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            self.perform_export(self.data_exporter.export_data_profile, file_path, "Data Profile")
    
    def export_multiple(self):
        """Export in multiple formats"""
        if self.data_processor.data is None:
            return
        
        folder_path = filedialog.askdirectory(title="Select Export Folder")
        
        if folder_path:
            base_name = "cleaned_data"
            base_path = Path(folder_path) / base_name
            
            def export_worker():
                try:
                    self.multi_btn.configure(text="Exporting...", state="disabled")
                    
                    results = self.data_exporter.export_multiple_formats(
                        str(base_path), 
                        formats=['csv', 'excel', 'json', 'report', 'profile']
                    )
                    
                    # Show results
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(results)
                    
                    if success_count == total_count:
                        messagebox.showinfo("Export Complete", f"Successfully exported data in {success_count} formats")
                    else:
                        failed_formats = [fmt for fmt, success in results.items() if not success]
                        messagebox.showwarning("Partial Export", f"Exported {success_count}/{total_count} formats. Failed: {', '.join(failed_formats)}")
                    
                except Exception as e:
                    messagebox.showerror("Export Error", f"Error during batch export: {str(e)}")
                finally:
                    self.after(0, lambda: self.multi_btn.configure(text="🚀 Export All Formats", state="normal"))
            
            threading.Thread(target=export_worker, daemon=True).start()
    
    def perform_export(self, export_function, file_path, format_name):
        """Perform export operation in background thread"""
        def export_worker():
            try:
                # Disable relevant button
                self.disable_export_buttons()
                
                success = export_function(file_path)
                
                if success:
                    messagebox.showinfo("Export Complete", f"Data successfully exported as {format_name}")
                else:
                    messagebox.showerror("Export Error", f"Failed to export data as {format_name}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting {format_name}: {str(e)}")
            finally:
                self.after(0, self.enable_export_buttons)
        
        threading.Thread(target=export_worker, daemon=True).start()
    
    def disable_export_buttons(self):
        """Disable all export buttons"""
        buttons = [self.csv_btn, self.excel_btn, self.json_btn, self.summary_btn, self.profile_btn, self.multi_btn]
        for btn in buttons:
            btn.configure(state="disabled")
    
    def enable_export_buttons(self):
        """Enable all export buttons"""
        has_data = self.data_processor.data is not None
        buttons = [self.csv_btn, self.excel_btn, self.json_btn, self.summary_btn, self.profile_btn, self.multi_btn]
        for btn in buttons:
            btn.configure(state="normal" if has_data else "disabled")
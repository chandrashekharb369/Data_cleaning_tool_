"""
Data Preview Frame Component - Clean Version
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.styles import *

class DataPreviewFrame(ctk.CTkFrame):
    """Data preview and basic information frame"""
    
    def __init__(self, parent, data_processor):
        super().__init__(parent, **WIDGET_STYLES['frame'])
        
        self.data_processor = data_processor
        self.current_page = 0
        self.rows_per_page = 50
        
        self.setup_widgets()
        self.refresh_data()
    
    def setup_widgets(self):
        """Setup the preview widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['large'])
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(header_frame, text="📋 Data Preview", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.grid(row=0, column=0, sticky="w")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e")
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(controls_frame, text="🔄 Refresh", command=self.refresh_data)
        apply_button_style(self.refresh_btn, 'secondary')
        self.refresh_btn.pack(side="left", padx=LAYOUT['spacing']['small'])
        
        # Info button
        self.info_btn = ctk.CTkButton(controls_frame, text="ℹ️ Info", command=self.show_data_info)
        apply_button_style(self.info_btn, 'secondary')
        self.info_btn.pack(side="left", padx=LAYOUT['spacing']['small'])
        
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT['padding']['large'], pady=(0, LAYOUT['padding']['large']))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Data info bar
        self.info_frame = ctk.CTkFrame(content_frame, height=40)
        self.info_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        self.info_frame.grid_propagate(False)
        self.info_frame.grid_columnconfigure(1, weight=1)
        
        self.info_label = ctk.CTkLabel(self.info_frame, text="No data loaded", font=FONTS['body'])
        self.info_label.grid(row=0, column=0, padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'], sticky="w")
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        pagination_frame.grid(row=0, column=2, padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        self.prev_btn = ctk.CTkButton(pagination_frame, text="◀", width=40, command=self.prev_page)
        apply_button_style(self.prev_btn, 'secondary')
        self.prev_btn.pack(side="left", padx=LAYOUT['spacing']['small'])
        
        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1", font=FONTS['body_small'])
        self.page_label.pack(side="left", padx=LAYOUT['spacing']['medium'])
        
        self.next_btn = ctk.CTkButton(pagination_frame, text="▶", width=40, command=self.next_page)
        apply_button_style(self.next_btn, 'secondary')
        self.next_btn.pack(side="left", padx=LAYOUT['spacing']['small'])
        
        # Data table frame
        table_frame = ctk.CTkFrame(content_frame)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT['padding']['medium'], pady=(0, LAYOUT['padding']['medium']))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview for data display
        self.create_data_table(table_frame)
    
    def create_data_table(self, parent):
        """Create data table using Treeview"""
        # Create treeview with scrollbars
        self.tree_frame = tk.Frame(parent)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=FONTS['body_small'])
        style.configure("Treeview.Heading", font=FONTS['subheading'])
    
    def refresh_data(self):
        """Refresh the data preview"""
        self.current_page = 0
        self.update_data_display()
        self.update_info_display()
        self.update_pagination_controls()
    
    def update_data_display(self):
        """Update the data table display"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.data_processor.data is None:
            # Show no data message
            self.tree.configure(columns=(), show="tree")
            self.tree.heading("#0", text="No Data Loaded")
            self.tree.insert("", "end", text="Load a dataset to preview data")
            return
        
        # Get current page data
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.data_processor.data.iloc[start_idx:end_idx]
        
        if page_data.empty:
            self.tree.configure(columns=(), show="tree")
            self.tree.heading("#0", text="No Data")
            self.tree.insert("", "end", text="No data available for this page")
            return
        
        # Configure columns
        columns = list(page_data.columns)
        self.tree.configure(columns=columns, show="tree headings")
        
        # Configure column widths and headings
        self.tree.column("#0", width=50, minwidth=50)  # Row index column
        self.tree.heading("#0", text="Index")
        
        for col in columns:
            self.tree.column(col, width=120, minwidth=80)
            self.tree.heading(col, text=str(col))
        
        # Insert data rows
        for idx, (row_idx, row) in enumerate(page_data.iterrows()):
            values = []
            for col in columns:
                value = row[col]
                if pd.isna(value):
                    values.append("<NULL>")
                elif isinstance(value, float):
                    values.append(f"{value:.4g}")
                else:
                    values.append(str(value)[:50])  # Limit cell content length
            
            self.tree.insert("", "end", text=str(row_idx), values=values)
    
    def update_info_display(self):
        """Update the info display"""
        if self.data_processor.data is None:
            self.info_label.configure(text="No data loaded")
            return
        
        total_rows = len(self.data_processor.data)
        total_cols = len(self.data_processor.data.columns)
        start_row = self.current_page * self.rows_per_page + 1
        end_row = min((self.current_page + 1) * self.rows_per_page, total_rows)
        
        info_text = f"Showing rows {start_row:,}-{end_row:,} of {total_rows:,} | {total_cols} columns"
        self.info_label.configure(text=info_text)
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        if self.data_processor.data is None:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            self.page_label.configure(text="Page --")
            return
        
        total_rows = len(self.data_processor.data)
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page
        current_page_display = self.current_page + 1
        
        # Update page label
        self.page_label.configure(text=f"Page {current_page_display} of {total_pages}")
        
        # Update button states
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_data_display()
            self.update_info_display()
            self.update_pagination_controls()
    
    def next_page(self):
        """Go to next page"""
        if self.data_processor.data is not None:
            total_rows = len(self.data_processor.data)
            total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page
            
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.update_data_display()
                self.update_info_display()
                self.update_pagination_controls()
    
    def show_data_info(self):
        """Show detailed data information in a popup"""
        if self.data_processor.data is None:
            return
        
        # Create info window
        info_window = ctk.CTkToplevel(self)
        info_window.title("Data Information")
        info_window.geometry("600x500")
        info_window.transient(self)
        
        # Make window modal
        info_window.grab_set()
        
        # Create scrollable text widget
        text_widget = ctk.CTkTextbox(info_window, font=FONTS['code'])
        text_widget.pack(fill="both", expand=True, padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['large'])
        
        # Generate info text
        info_text = self.generate_data_info_text()
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
        
        # Center the window
        info_window.after(100, lambda: self.center_window(info_window))
    
    def center_window(self, window):
        """Center a window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def generate_data_info_text(self) -> str:
        """Generate detailed data information text"""
        if self.data_processor.data is None:
            return "No data loaded"
        
        df = self.data_processor.data
        
        # Basic info
        info_lines = [
            "=== DATA INFORMATION ===",
            f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
            f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            "",
            "=== COLUMN INFORMATION ==="
        ]
        
        # Column details
        for i, col in enumerate(df.columns):
            col_info = [
                f"{i+1}. {col}",
                f"   Type: {df[col].dtype}",
                f"   Non-null: {df[col].count():,} ({(df[col].count()/len(df)*100):.1f}%)",
                f"   Unique: {df[col].nunique():,}"
            ]
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.extend([
                    f"   Min: {df[col].min():.4g}",
                    f"   Max: {df[col].max():.4g}",
                    f"   Mean: {df[col].mean():.4g}"
                ])
            else:
                top_value = df[col].mode()
                if len(top_value) > 0:
                    col_info.append(f"   Most frequent: {top_value.iloc[0]}")
            
            info_lines.extend(col_info)
            info_lines.append("")
        
        # Data quality summary
        missing_data = df.isnull().sum()
        duplicates = df.duplicated().sum()
        
        info_lines.extend([
            "=== DATA QUALITY SUMMARY ===",
            f"Missing values: {missing_data.sum():,} ({(missing_data.sum()/(len(df)*len(df.columns))*100):.2f}%)",
            f"Duplicate rows: {duplicates:,} ({(duplicates/len(df)*100):.2f}%)",
            "",
            "=== MISSING VALUES BY COLUMN ==="
        ])
        
        missing_by_col = missing_data[missing_data > 0]
        if len(missing_by_col) > 0:
            for col, count in missing_by_col.items():
                pct = (count / len(df)) * 100
                info_lines.append(f"{col}: {count:,} ({pct:.2f}%)")
        else:
            info_lines.append("No missing values found")
        
        return "\n".join(info_lines)
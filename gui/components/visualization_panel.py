"""
Visualization Panel Component - Simplified
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.styles import *

class VisualizationPanel(ctk.CTkFrame):
    """Data visualization panel"""
    
    def __init__(self, parent, data_processor, visualization_dashboard):
        super().__init__(parent, **WIDGET_STYLES['frame'])
        
        self.data_processor = data_processor
        self.visualization_dashboard = visualization_dashboard
        self.current_canvas = None
        
        self.setup_widgets()
        self.refresh_data()
    
    def setup_widgets(self):
        """Setup visualization panel widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with controls
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['large'])
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="📊 Data Visualization", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.grid(row=0, column=0, sticky="w")
        
        # Chart selection
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e")
        
        chart_label = ctk.CTkLabel(controls_frame, text="Chart Type:", font=FONTS['body'])
        chart_label.pack(side="left", padx=(0, LAYOUT['spacing']['small']))
        
        self.chart_type = ctk.CTkOptionMenu(
            controls_frame, 
            values=["overview", "correlation", "distribution", "missing", "categorical", "outliers"],
            command=self.update_chart
        )
        self.chart_type.pack(side="left", padx=LAYOUT['spacing']['small'])
        self.chart_type.set("overview")
        
        # Visualization area
        self.viz_frame = create_styled_frame(self)
        self.viz_frame.grid(row=1, column=0, sticky="nsew", padx=LAYOUT['padding']['large'], pady=(0, LAYOUT['padding']['large']))
        self.viz_frame.grid_columnconfigure(0, weight=1)
        self.viz_frame.grid_rowconfigure(0, weight=1)
        
        # Initial message
        self.create_initial_message()
    
    def create_initial_message(self):
        """Create initial message when no data is loaded"""
        message_label = ctk.CTkLabel(
            self.viz_frame, 
            text="Load data to view visualizations", 
            font=FONTS['heading']
        )
        message_label.grid(row=0, column=0)
    
    def refresh_data(self):
        """Refresh visualization panel"""
        has_data = self.data_processor.data is not None
        
        self.chart_type.configure(state="normal" if has_data else "disabled")
        
        if has_data:
            self.update_chart()
        else:
            self.clear_visualization()
            self.create_initial_message()
    
    def clear_visualization(self):
        """Clear current visualization"""
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        if self.current_canvas:
            self.current_canvas = None
    
    def update_chart(self, chart_type=None):
        """Update the current chart"""
        if self.data_processor.data is None:
            return
        
        if chart_type is None:
            chart_type = self.chart_type.get()
        
        def chart_worker():
            try:
                # Clear previous chart
                self.after(0, self.clear_visualization)
                
                # Create new chart
                canvas = self.visualization_dashboard.create_canvas_widget(
                    self.viz_frame, 
                    chart_type
                )
                
                # Update UI on main thread
                def update_ui():
                    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
                    self.current_canvas = canvas
                
                self.after(0, update_ui)
                
            except Exception as e:
                error_msg = f"Error creating visualization: {str(e)}"
                
                def show_error():
                    error_label = ctk.CTkLabel(
                        self.viz_frame, 
                        text=error_msg, 
                        font=FONTS['body']
                    )
                    error_label.grid(row=0, column=0)
                
                self.after(0, show_error)
        
        threading.Thread(target=chart_worker, daemon=True).start()
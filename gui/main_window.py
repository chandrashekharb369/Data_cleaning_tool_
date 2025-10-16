"""
Main Application Window for Smart Data Cleaner
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_processor import DataProcessor
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.exporter import DataExporter
from visualizations.dashboard import VisualizationDashboard
from utils.helpers import format_bytes, format_number, ProgressTracker
from utils.validators import DataValidator
from gui.styles import *
from gui.components.data_preview import DataPreviewFrame
from gui.components.cleaning_panel import CleaningPanel
from gui.components.analysis_panel import AnalysisPanel
from gui.components.visualization_panel import VisualizationPanel
from gui.components.export_panel import ExportPanel

class SmartDataCleanerApp(ctk.CTk):
    """Main application class for Smart Data Cleaner"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.data_processor = DataProcessor()
        self.data_cleaner = DataCleaner(self.data_processor)
        self.data_analyzer = DataAnalyzer(self.data_processor)
        self.data_exporter = DataExporter(self.data_processor)
        self.visualization_dashboard = VisualizationDashboard(self.data_processor)
        self.data_validator = DataValidator()
        
        # Initialize UI
        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        
        # Status variables
        self.current_file = None
        self.processing_thread = None
        
    def setup_window(self):
        """Configure main window"""
        self.title("Smart Data Cleaner - Revolutionizing Data Preprocessing")
        self.geometry(f"{LAYOUT['window']['default_width']}x{LAYOUT['window']['default_height']}")
        self.minsize(LAYOUT['window']['min_width'], LAYOUT['window']['min_height'])
        
        # Center window on screen
        self.center_window()
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Create main toolbar
        self.create_toolbar()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area with tabs
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create main toolbar"""
        self.toolbar = create_styled_frame(self, height=LAYOUT['toolbar_height'])
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=LAYOUT['padding']['medium'], pady=(LAYOUT['padding']['medium'], 0))
        self.toolbar.grid_columnconfigure(2, weight=1)
        
        # App title
        title_label = ctk.CTkLabel(self.toolbar, text="🧹 Smart Data Cleaner", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.grid(row=0, column=0, padx=LAYOUT['padding']['large'], pady=LAYOUT['padding']['medium'])
        
        # File operations
        file_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        file_frame.grid(row=0, column=1, padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['small'])
        
        self.load_button = ctk.CTkButton(file_frame, text="📁 Load Data", command=self.load_data)
        apply_button_style(self.load_button, 'primary')
        self.load_button.pack(side="left", padx=(0, LAYOUT['spacing']['small']))
        
        self.sample_button = ctk.CTkButton(file_frame, text="🎲 Sample Data", command=self.load_sample_data)
        apply_button_style(self.sample_button, 'secondary')
        self.sample_button.pack(side="left", padx=LAYOUT['spacing']['small'])
        
        # Progress bar (initially hidden)
        self.progress_var = ctk.StringVar(value="Ready")
        self.progress_label = ctk.CTkLabel(self.toolbar, textvariable=self.progress_var, font=FONTS['body_small'])
        self.progress_label.grid(row=0, column=2, sticky="e", padx=LAYOUT['padding']['medium'])
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = create_styled_frame(self, width=LAYOUT['sidebar_width'])
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(LAYOUT['padding']['medium'], 0), pady=LAYOUT['padding']['medium'])
        self.sidebar.grid_propagate(False)
        
        # Data summary section
        summary_label = ctk.CTkLabel(self.sidebar, text="📊 Data Summary", font=FONTS['subheading'])
        apply_label_style(summary_label, 'subheading')
        summary_label.pack(pady=(LAYOUT['padding']['large'], LAYOUT['padding']['medium']))
        
        # Data info frame
        self.data_info_frame = create_styled_scrollable_frame(self.sidebar, height=200)
        self.data_info_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['small'])
        
        self.update_data_summary()
        
        # Navigation buttons
        nav_label = ctk.CTkLabel(self.sidebar, text="🧭 Navigation", font=FONTS['subheading'])
        apply_label_style(nav_label, 'subheading')
        nav_label.pack(pady=(LAYOUT['padding']['large'], LAYOUT['padding']['medium']))
        
        # Tab navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("📋 Data Preview", "preview"),
            ("🧹 Data Cleaning", "cleaning"),
            ("📈 Analysis", "analysis"),
            ("📊 Visualization", "visualization"),
            ("💾 Export", "export")
        ]
        
        for text, tab_id in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=text, command=lambda t=tab_id: self.switch_tab(t))
            apply_button_style(btn, 'secondary')
            btn.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
            self.nav_buttons[tab_id] = btn
        
        # Processing log section
        log_label = ctk.CTkLabel(self.sidebar, text="📝 Processing Log", font=FONTS['subheading'])
        apply_label_style(log_label, 'subheading')
        log_label.pack(pady=(LAYOUT['padding']['large'], LAYOUT['padding']['medium']))
        
        self.log_text = ctk.CTkTextbox(self.sidebar, height=150, font=FONTS['body_small'])
        self.log_text.pack(fill="both", expand=True, padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['small'])
        
        # Clear log button
        clear_log_btn = ctk.CTkButton(self.sidebar, text="Clear Log", command=self.clear_log)
        apply_button_style(clear_log_btn, 'secondary')
        clear_log_btn.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
    
    def create_main_content(self):
        """Create main content area with tabs"""
        self.main_frame = create_styled_frame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=LAYOUT['padding']['medium'], pady=LAYOUT['padding']['medium'])
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create tab frames
        self.tab_frames = {}
        
        # Data Preview Tab
        self.tab_frames['preview'] = DataPreviewFrame(self.main_frame, self.data_processor)
        
        # Data Cleaning Tab
        self.tab_frames['cleaning'] = CleaningPanel(self.main_frame, self.data_processor, self.data_cleaner, self.update_ui_after_processing)
        
        # Analysis Tab
        self.tab_frames['analysis'] = AnalysisPanel(self.main_frame, self.data_processor, self.data_analyzer)
        
        # Visualization Tab
        self.tab_frames['visualization'] = VisualizationPanel(self.main_frame, self.data_processor, self.visualization_dashboard)
        
        # Export Tab
        self.tab_frames['export'] = ExportPanel(self.main_frame, self.data_processor, self.data_exporter)
        
        # Show default tab
        self.current_tab = 'preview'
        self.switch_tab('preview')
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = create_styled_frame(self, height=30)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=LAYOUT['padding']['medium'], pady=(0, LAYOUT['padding']['medium']))
        self.status_bar.grid_columnconfigure(1, weight=1)
        
        # Status text
        self.status_var = ctk.StringVar(value="Ready - Load data to begin")
        status_label = ctk.CTkLabel(self.status_bar, textvariable=self.status_var, font=FONTS['body_small'])
        status_label.grid(row=0, column=0, padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
        
        # Memory usage
        self.memory_var = ctk.StringVar(value="Memory: --")
        memory_label = ctk.CTkLabel(self.status_bar, textvariable=self.memory_var, font=FONTS['body_small'])
        memory_label.grid(row=0, column=2, padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
    
    def setup_layout(self):
        """Setup layout and bindings"""
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Update UI state
        self.update_ui_state()
    
    def load_data(self):
        """Load data from file"""
        file_types = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=file_types
        )
        
        if file_path:
            self.load_data_async(file_path)
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        try:
            from utils.helpers import generate_sample_data
            
            self.status_var.set("Generating sample data...")
            
            # Generate sample data
            sample_data = generate_sample_data()
            self.data_processor.data = sample_data
            self.data_processor.original_data = sample_data.copy()
            self.data_processor._update_metadata()
            self.data_processor._log_action("Loaded sample dataset")
            
            self.current_file = "Sample Dataset"
            self.update_ui_after_data_load()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sample data: {str(e)}")
            self.status_var.set("Ready")
    
    def load_data_async(self, file_path: str):
        """Load data asynchronously"""
        def load_worker():
            try:
                self.progress_var.set("Validating file...")
                
                # Validate file
                validation_result = self.data_validator.validate_file_format(file_path)
                
                if not validation_result['is_valid']:
                    error_msg = "\n".join(validation_result['errors'])
                    messagebox.showerror("File Validation Error", error_msg)
                    return
                
                if validation_result['warnings']:
                    warning_msg = "\n".join(validation_result['warnings'])
                    if not messagebox.askyesno("File Warnings", f"Warnings found:\n{warning_msg}\n\nContinue loading?"):
                        return
                
                self.progress_var.set("Loading data...")
                
                # Load data
                success = self.data_processor.load_data(file_path)
                
                if success:
                    self.progress_var.set("Validating data...")
                    
                    # Validate loaded data
                    data_validation = self.data_validator.validate_dataframe(self.data_processor.data)
                    
                    if not data_validation['is_valid']:
                        error_msg = "\n".join(data_validation['errors'])
                        messagebox.showerror("Data Validation Error", error_msg)
                        return
                    
                    if data_validation['warnings']:
                        warning_msg = "\n".join(data_validation['warnings'][:5])  # Show first 5 warnings
                        messagebox.showwarning("Data Quality Warnings", f"Data quality issues detected:\n{warning_msg}")
                    
                    self.current_file = Path(file_path).name
                    
                    # Update UI on main thread
                    self.after(0, self.update_ui_after_data_load)
                    
                else:
                    messagebox.showerror("Error", "Failed to load data file")
                    
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading data: {str(e)}")
            
            finally:
                self.after(0, lambda: self.progress_var.set("Ready"))
        
        # Start loading in background thread
        self.processing_thread = threading.Thread(target=load_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def update_ui_after_data_load(self):
        """Update UI after successful data load"""
        self.update_data_summary()
        self.update_processing_log()
        self.update_ui_state()
        
        # Update all tab frames
        for tab_frame in self.tab_frames.values():
            if hasattr(tab_frame, 'refresh_data'):
                tab_frame.refresh_data()
        
        self.status_var.set(f"Loaded: {self.current_file} - {self.data_processor.data.shape[0]:,} rows, {self.data_processor.data.shape[1]} columns")
        
        # Update memory usage
        memory_usage = format_bytes(self.data_processor.metadata['memory_usage'])
        self.memory_var.set(f"Memory: {memory_usage}")
    
    def update_ui_after_processing(self):
        """Update UI after data processing operations"""
        self.update_data_summary()
        self.update_processing_log()
        
        # Update relevant tab frames
        for tab_frame in self.tab_frames.values():
            if hasattr(tab_frame, 'refresh_data'):
                tab_frame.refresh_data()
        
        # Update status
        if self.data_processor.data is not None:
            self.status_var.set(f"Updated: {self.current_file} - {self.data_processor.data.shape[0]:,} rows, {self.data_processor.data.shape[1]} columns")
            memory_usage = format_bytes(self.data_processor.metadata['memory_usage'])
            self.memory_var.set(f"Memory: {memory_usage}")
    
    def update_data_summary(self):
        """Update data summary in sidebar"""
        # Clear existing content
        for widget in self.data_info_frame.winfo_children():
            widget.destroy()
        
        if self.data_processor.data is None:
            no_data_label = ctk.CTkLabel(self.data_info_frame, text="No data loaded", font=FONTS['body_small'])
            no_data_label.pack(pady=LAYOUT['padding']['medium'])
            return
        
        # Display data summary
        summary = self.data_processor.get_data_summary()
        
        info_items = [
            ("📄 File", self.current_file or "Unknown"),
            ("📏 Rows", format_number(summary['basic_info']['rows'])),
            ("📊 Columns", format_number(summary['basic_info']['columns'])),
            ("💾 Memory", summary['basic_info']['memory_usage']),
            ("🔢 Numeric", format_number(summary['column_types']['numeric'])),
            ("📝 Categorical", format_number(summary['column_types']['categorical'])),
            ("❌ Missing", format_number(summary['missing_data']['total_missing'])),
            ("🔄 Duplicates", format_number(summary['basic_info']['duplicates']))
        ]
        
        for label_text, value in info_items:
            item_frame = ctk.CTkFrame(self.data_info_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=LAYOUT['spacing']['small'])
            
            label = ctk.CTkLabel(item_frame, text=label_text, font=FONTS['body_small'])
            label.pack(side="left")
            
            value_label = ctk.CTkLabel(item_frame, text=str(value), font=FONTS['body_small'])
            value_label.pack(side="right")
    
    def update_processing_log(self):
        """Update processing log in sidebar"""
        log_entries = self.data_processor.get_processing_log()
        
        # Clear and update log
        self.log_text.delete("1.0", "end")
        
        for entry in log_entries[-20:]:  # Show last 20 entries
            self.log_text.insert("end", f"• {entry}\n")
        
        # Scroll to bottom
        self.log_text.see("end")
    
    def clear_log(self):
        """Clear processing log"""
        self.log_text.delete("1.0", "end")
    
    def switch_tab(self, tab_id: str):
        """Switch to specified tab"""
        # Hide current tab
        if self.current_tab in self.tab_frames:
            self.tab_frames[self.current_tab].grid_remove()
        
        # Show new tab
        if tab_id in self.tab_frames:
            self.tab_frames[tab_id].grid(row=0, column=0, sticky="nsew")
            self.current_tab = tab_id
            
            # Update navigation button states
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == tab_id:
                    apply_button_style(btn, 'primary')
                else:
                    apply_button_style(btn, 'secondary')
            
            # Refresh tab data if needed
            if hasattr(self.tab_frames[tab_id], 'refresh_data'):
                self.tab_frames[tab_id].refresh_data()
    
    def update_ui_state(self):
        """Update UI state based on data availability"""
        has_data = self.data_processor.data is not None
        
        # Enable/disable navigation buttons based on data availability
        for tab_id, btn in self.nav_buttons.items():
            if tab_id == 'preview' or has_data:
                btn.configure(state="normal")
            else:
                btn.configure(state="disabled")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Close any matplotlib figures
            if hasattr(self, 'visualization_dashboard'):
                self.visualization_dashboard.close_figures()
            
            # Cancel any running threads
            if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.is_alive():
                # Note: In a production app, you'd want to implement proper thread cancellation
                pass
            
            self.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            self.destroy()

if __name__ == "__main__":
    app = SmartDataCleanerApp()
    app.mainloop()
"""Data Cleaning Panel Component"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.styles import *


class CleaningPanel(ctk.CTkFrame):
    """Data cleaning operations panel"""

    def __init__(self, parent, data_processor, data_cleaner, update_callback):
        super().__init__(parent, **WIDGET_STYLES['frame'])

        self.data_processor = data_processor
        self.data_cleaner = data_cleaner
        self.update_callback = update_callback

        self.setup_widgets()
        self.refresh_data()

    def setup_widgets(self):
        """Setup cleaning panel widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['large'],
            pady=LAYOUT['padding']['large']
        )
        header_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(header_frame, text="🧹 Data Cleaning", font=FONTS['heading'])
        apply_label_style(title_label, 'heading')
        title_label.grid(row=0, column=0, sticky="w")

        self.auto_clean_btn = ctk.CTkButton(header_frame, text="✨ Auto Clean", command=self.auto_clean)
        apply_button_style(self.auto_clean_btn, 'success')
        self.auto_clean_btn.grid(row=0, column=2, sticky="e")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=LAYOUT['padding']['large'],
            pady=(0, LAYOUT['padding']['large'])
        )

        self.create_duplicates_tab()
        self.create_missing_values_tab()
        self.create_outliers_tab()
        self.create_data_types_tab()
        self.create_encoding_tab()

    def create_duplicates_tab(self):
        tab = self.tabview.add("🔄 Duplicates")
        tab.grid_columnconfigure(0, weight=1)

        info_frame = create_styled_frame(tab)
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )
        info_frame.grid_columnconfigure(1, weight=1)

        self.duplicates_info_label = ctk.CTkLabel(info_frame, text="No data loaded", font=FONTS['body'])
        self.duplicates_info_label.grid(
            row=0,
            column=0,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

        controls_frame = create_styled_frame(tab)
        controls_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        strategy_label = ctk.CTkLabel(controls_frame, text="Keep strategy:", font=FONTS['subheading'])
        apply_label_style(strategy_label, 'subheading')
        strategy_label.grid(
            row=0,
            column=0,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

        self.keep_strategy = ctk.CTkOptionMenu(controls_frame, values=["first", "last"])
        self.keep_strategy.grid(
            row=0,
            column=1,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )
        self.keep_strategy.set("first")

        self.remove_duplicates_btn = ctk.CTkButton(
            controls_frame,
            text="Remove Duplicates",
            command=self.remove_duplicates
        )
        apply_button_style(self.remove_duplicates_btn, 'danger')
        self.remove_duplicates_btn.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

    def create_missing_values_tab(self):
        tab = self.tabview.add("❌ Missing Values")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        info_frame = create_styled_frame(tab)
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.missing_info_label = ctk.CTkLabel(info_frame, text="No data loaded", font=FONTS['body'])
        self.missing_info_label.pack(
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        strategy_frame = create_styled_scrollable_frame(tab)
        strategy_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=LAYOUT['padding']['medium'],
            pady=(0, LAYOUT['padding']['medium'])
        )

        self.missing_strategies = {}
        self.strategy_frame = strategy_frame

        apply_frame = ctk.CTkFrame(tab, fg_color="transparent")
        apply_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.apply_missing_btn = ctk.CTkButton(
            apply_frame,
            text="Apply Missing Value Strategies",
            command=self.handle_missing_values
        )
        apply_button_style(self.apply_missing_btn, 'primary')
        self.apply_missing_btn.pack()

    def create_outliers_tab(self):
        tab = self.tabview.add("📊 Outliers")
        tab.grid_columnconfigure(0, weight=1)

        info_frame = create_styled_frame(tab)
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.outliers_info_label = ctk.CTkLabel(info_frame, text="No data loaded", font=FONTS['body'])
        self.outliers_info_label.pack(
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        controls_frame = create_styled_frame(tab)
        controls_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        method_label = ctk.CTkLabel(controls_frame, text="Detection method:", font=FONTS['subheading'])
        apply_label_style(method_label, 'subheading')
        method_label.grid(
            row=0,
            column=0,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

        self.outlier_method = ctk.CTkOptionMenu(controls_frame, values=["iqr", "zscore"])
        self.outlier_method.grid(
            row=0,
            column=1,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )
        self.outlier_method.set("iqr")

        self.detect_outliers_btn = ctk.CTkButton(
            controls_frame,
            text="Detect & Remove Outliers",
            command=self.handle_outliers
        )
        apply_button_style(self.detect_outliers_btn, 'warning')
        self.detect_outliers_btn.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

        self.outliers_results_frame = create_styled_frame(tab)
        self.outliers_results_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.outliers_results_label = ctk.CTkLabel(self.outliers_results_frame, text="", font=FONTS['body_small'])
        self.outliers_results_label.pack(
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

    def create_data_types_tab(self):
        tab = self.tabview.add("🔢 Data Types")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        info_frame = create_styled_frame(tab)
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.types_info_label = ctk.CTkLabel(info_frame, text="No data loaded", font=FONTS['body'])
        self.types_info_label.pack(
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        types_frame = create_styled_scrollable_frame(tab)
        types_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=LAYOUT['padding']['medium'],
            pady=(0, LAYOUT['padding']['medium'])
        )

        self.type_conversions = {}
        self.types_frame = types_frame

        apply_frame = ctk.CTkFrame(tab, fg_color="transparent")
        apply_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.apply_types_btn = ctk.CTkButton(apply_frame, text="Apply Type Conversions", command=self.convert_data_types)
        apply_button_style(self.apply_types_btn, 'primary')
        self.apply_types_btn.pack()

    def create_encoding_tab(self):
        tab = self.tabview.add("📝 Encoding")
        tab.grid_columnconfigure(0, weight=1)

        info_frame = create_styled_frame(tab)
        info_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.encoding_info_label = ctk.CTkLabel(info_frame, text="No data loaded", font=FONTS['body'])
        self.encoding_info_label.pack(
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        controls_frame = create_styled_frame(tab)
        controls_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium']
        )

        self.drop_first_var = ctk.BooleanVar(value=True)
        drop_first_check = ctk.CTkCheckBox(
            controls_frame,
            text="Drop first category (avoid multicollinearity)",
            variable=self.drop_first_var
        )
        drop_first_check.grid(
            row=0,
            column=0,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

        self.create_dummies_btn = ctk.CTkButton(
            controls_frame,
            text="Create Dummy Variables",
            command=self.create_dummy_variables
        )
        apply_button_style(self.create_dummies_btn, 'primary')
        self.create_dummies_btn.grid(
            row=1,
            column=0,
            padx=LAYOUT['padding']['medium'],
            pady=LAYOUT['padding']['medium'],
            sticky="w"
        )

    def refresh_data(self):
        """Refresh the cleaning panel with current data"""
        self.update_duplicates_info()
        self.update_missing_values_info()
        self.update_outliers_info()
        self.update_data_types_info()
        self.update_encoding_info()
        self.update_button_states()

    def update_duplicates_info(self):
        """Update duplicates information"""
        if self.data_processor.data is None:
            self.duplicates_info_label.configure(text="No data loaded")
            return

        duplicates = self.data_processor.metadata['duplicates']
        total_rows = len(self.data_processor.data)
        duplicate_pct = (duplicates / total_rows) * 100 if total_rows > 0 else 0

        info_text = f"Found {duplicates:,} duplicate rows ({duplicate_pct:.2f}%) out of {total_rows:,} total rows"
        self.duplicates_info_label.configure(text=info_text)

    def update_missing_values_info(self):
        """Update missing values information and strategy selectors"""
        if self.data_processor.data is None:
            self.missing_info_label.configure(text="No data loaded")
            return

        missing_data = self.data_processor.data.isnull().sum()
        total_missing = missing_data.sum()
        total_cells = len(self.data_processor.data) * len(self.data_processor.data.columns)
        missing_pct = (total_missing / total_cells) * 100 if total_cells > 0 else 0

        info_text = f"Found {total_missing:,} missing values ({missing_pct:.2f}%) across all columns"
        self.missing_info_label.configure(text=info_text)

        for widget in self.strategy_frame.winfo_children():
            widget.destroy()

        self.missing_strategies = {}

        missing_columns = missing_data[missing_data > 0]
        if len(missing_columns) == 0:
            no_missing_label = ctk.CTkLabel(self.strategy_frame, text="No missing values found", font=FONTS['body'])
            no_missing_label.pack(pady=LAYOUT['padding']['large'])
            return

        for column, count in missing_columns.items():
            col_frame = create_styled_frame(self.strategy_frame)
            col_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
            col_frame.grid_columnconfigure(2, weight=1)

            pct = (count / len(self.data_processor.data)) * 100
            col_label = ctk.CTkLabel(col_frame, text=f"{column}:", font=FONTS['subheading'])
            col_label.grid(
                row=0,
                column=0,
                padx=LAYOUT['padding']['medium'],
                pady=LAYOUT['spacing']['small'],
                sticky="w"
            )

            info_label = ctk.CTkLabel(
                col_frame,
                text=f"{count:,} missing ({pct:.1f}%)",
                font=FONTS['body_small']
            )
            info_label.grid(
                row=0,
                column=1,
                padx=LAYOUT['padding']['small'],
                pady=LAYOUT['spacing']['small'],
                sticky="w"
            )

            is_numeric = column in self.data_processor.metadata['numeric_columns']
            if is_numeric:
                strategies = ["drop", "mean", "median", "forward_fill", "backward_fill", "knn"]
            else:
                strategies = ["drop", "mode", "forward_fill", "backward_fill", "constant:Unknown"]

            strategy_menu = ctk.CTkOptionMenu(col_frame, values=strategies)
            strategy_menu.grid(
                row=0,
                column=3,
                padx=LAYOUT['padding']['medium'],
                pady=LAYOUT['spacing']['small'],
                sticky="e"
            )
            strategy_menu.set("median" if is_numeric else "mode")

            self.missing_strategies[column] = strategy_menu

    def update_outliers_info(self):
        """Update outliers information"""
        if self.data_processor.data is None:
            self.outliers_info_label.configure(text="No data loaded")
            return

        numeric_cols = self.data_processor.metadata['numeric_columns']
        info_text = f"Outlier detection available for {len(numeric_cols)} numeric columns"
        self.outliers_info_label.configure(text=info_text)
        self.outliers_results_label.configure(text="")

    def update_data_types_info(self):
        """Update data types information and conversion options"""
        if self.data_processor.data is None:
            self.types_info_label.configure(text="No data loaded")
            return

        numeric_cols = len(self.data_processor.metadata['numeric_columns'])
        categorical_cols = len(self.data_processor.metadata['categorical_columns'])

        info_text = f"{numeric_cols} numeric columns, {categorical_cols} categorical columns"
        self.types_info_label.configure(text=info_text)

        for widget in self.types_frame.winfo_children():
            widget.destroy()

        self.type_conversions = {}

        for column in self.data_processor.data.columns:
            current_type = str(self.data_processor.data[column].dtype)

            col_frame = create_styled_frame(self.types_frame)
            col_frame.pack(fill="x", padx=LAYOUT['padding']['medium'], pady=LAYOUT['spacing']['small'])
            col_frame.grid_columnconfigure(2, weight=1)

            col_label = ctk.CTkLabel(col_frame, text=f"{column}:", font=FONTS['subheading'])
            col_label.grid(
                row=0,
                column=0,
                padx=LAYOUT['padding']['medium'],
                pady=LAYOUT['spacing']['small'],
                sticky="w"
            )

            type_label = ctk.CTkLabel(col_frame, text=f"({current_type})", font=FONTS['body_small'])
            type_label.grid(
                row=0,
                column=1,
                padx=LAYOUT['padding']['small'],
                pady=LAYOUT['spacing']['small'],
                sticky="w"
            )

            type_options = ["no_change", "numeric", "string", "category", "datetime"]
            type_menu = ctk.CTkOptionMenu(col_frame, values=type_options)
            type_menu.grid(
                row=0,
                column=3,
                padx=LAYOUT['padding']['medium'],
                pady=LAYOUT['spacing']['small'],
                sticky="e"
            )
            type_menu.set("no_change")

            self.type_conversions[column] = type_menu

    def update_encoding_info(self):
        """Update encoding information"""
        if self.data_processor.data is None:
            self.encoding_info_label.configure(text="No data loaded")
            return

        categorical_cols = self.data_processor.metadata['categorical_columns']
        info_text = f"{len(categorical_cols)} categorical columns available for encoding"
        self.encoding_info_label.configure(text=info_text)

    def update_button_states(self):
        """Enable or disable buttons based on data availability"""
        has_data = self.data_processor.data is not None

        self.auto_clean_btn.configure(state="normal" if has_data else "disabled")
        self.remove_duplicates_btn.configure(state="normal" if has_data else "disabled")
        self.apply_missing_btn.configure(state="normal" if has_data else "disabled")
        self.detect_outliers_btn.configure(state="normal" if has_data else "disabled")
        self.apply_types_btn.configure(state="normal" if has_data else "disabled")
        self.create_dummies_btn.configure(state="normal" if has_data else "disabled")

    def auto_clean(self):
        """Perform automatic data cleaning"""
        if self.data_processor.data is None:
            return

        def auto_clean_worker():
            try:
                self.auto_clean_btn.configure(text="Processing...", state="disabled")
                results = self.data_cleaner.auto_clean()

                result_messages = []
                if results.get('duplicates_removed'):
                    result_messages.append("✓ Duplicates removed")
                if results.get('missing_values_handled'):
                    result_messages.append("✓ Missing values handled")
                if results.get('outliers_detected'):
                    total_outliers = sum(results['outliers_detected'].values())
                    result_messages.append(f"✓ {total_outliers} outliers detected and removed")
                if results.get('types_converted'):
                    result_messages.append("✓ Data types optimized")

                if result_messages:
                    messagebox.showinfo("Auto-Clean Results", "Auto-cleaning completed:\n\n" + "\n".join(result_messages))
                else:
                    messagebox.showinfo("Auto-Clean Results", "No cleaning operations were needed.")

                self.after(0, self.update_callback)
                self.after(0, self.refresh_data)

            except Exception as exc:
                messagebox.showerror("Error", f"Auto-cleaning failed: {exc}")
            finally:
                self.after(0, lambda: self.auto_clean_btn.configure(text="✨ Auto Clean", state="normal"))

        threading.Thread(target=auto_clean_worker, daemon=True).start()

    def remove_duplicates(self):
        """Remove duplicate rows"""
        if self.data_processor.data is None:
            return

        keep_strategy = self.keep_strategy.get()

        def remove_worker():
            try:
                self.remove_duplicates_btn.configure(text="Removing...", state="disabled")
                initial_rows = len(self.data_processor.data)
                success = self.data_cleaner.remove_duplicates(keep=keep_strategy)

                if success:
                    final_rows = len(self.data_processor.data)
                    removed = initial_rows - final_rows
                    messagebox.showinfo("Success", f"Removed {removed:,} duplicate rows")
                    self.after(0, self.update_callback)
                    self.after(0, self.refresh_data)
                else:
                    messagebox.showerror("Error", "Failed to remove duplicates")

            except Exception as exc:
                messagebox.showerror("Error", f"Error removing duplicates: {exc}")
            finally:
                self.after(0, lambda: self.remove_duplicates_btn.configure(text="Remove Duplicates", state="normal"))

        threading.Thread(target=remove_worker, daemon=True).start()

    def handle_missing_values(self):
        """Handle missing values with selected strategies"""
        if self.data_processor.data is None or not self.missing_strategies:
            return

        strategies = {column: menu.get() for column, menu in self.missing_strategies.items()}

        def missing_worker():
            try:
                self.apply_missing_btn.configure(text="Processing...", state="disabled")
                success = self.data_cleaner.handle_missing_values(strategies)

                if success:
                    messagebox.showinfo("Success", "Missing values handled successfully")
                    self.after(0, self.update_callback)
                    self.after(0, self.refresh_data)
                else:
                    messagebox.showerror("Error", "Failed to handle missing values")

            except Exception as exc:
                messagebox.showerror("Error", f"Error handling missing values: {exc}")
            finally:
                self.after(0, lambda: self.apply_missing_btn.configure(text="Apply Missing Value Strategies", state="normal"))

        threading.Thread(target=missing_worker, daemon=True).start()

    def handle_outliers(self):
        """Detect and handle outliers"""
        if self.data_processor.data is None:
            return

        method = self.outlier_method.get()

        def outliers_worker():
            try:
                self.detect_outliers_btn.configure(text="Processing...", state="disabled")
                outlier_counts = self.data_cleaner.detect_and_handle_outliers(method=method)

                if outlier_counts:
                    total_outliers = sum(outlier_counts.values())
                    result_text = "Detected and removed {0} outliers:\n\n".format(total_outliers)
                    for column, count in outlier_counts.items():
                        result_text += f"{column}: {count} outliers\n"

                    self.after(0, lambda: self.outliers_results_label.configure(text=result_text))
                    messagebox.showinfo("Outliers Removed", f"Removed {total_outliers} outliers using {method} method")
                    self.after(0, self.update_callback)
                    self.after(0, self.refresh_data)
                else:
                    messagebox.showinfo("No Outliers", "No outliers detected")

            except Exception as exc:
                messagebox.showerror("Error", f"Error handling outliers: {exc}")
            finally:
                self.after(0, lambda: self.detect_outliers_btn.configure(text="Detect & Remove Outliers", state="normal"))

        threading.Thread(target=outliers_worker, daemon=True).start()

    def convert_data_types(self):
        """Convert data types"""
        if self.data_processor.data is None or not self.type_conversions:
            return

        type_mapping = {
            column: menu.get()
            for column, menu in self.type_conversions.items()
            if menu.get() != "no_change"
        }

        if not type_mapping:
            messagebox.showinfo("No Changes", "No type conversions selected")
            return

        def types_worker():
            try:
                self.apply_types_btn.configure(text="Converting...", state="disabled")
                success = self.data_cleaner.convert_data_types(type_mapping)

                if success:
                    messagebox.showinfo("Success", "Data types converted successfully")
                    self.after(0, self.update_callback)
                    self.after(0, self.refresh_data)
                else:
                    messagebox.showerror("Error", "Failed to convert data types")

            except Exception as exc:
                messagebox.showerror("Error", f"Error converting data types: {exc}")
            finally:
                self.after(0, lambda: self.apply_types_btn.configure(text="Apply Type Conversions", state="normal"))

        threading.Thread(target=types_worker, daemon=True).start()

    def create_dummy_variables(self):
        """Create dummy variables for categorical columns"""
        if self.data_processor.data is None:
            return

        drop_first = self.drop_first_var.get()
        categorical_cols = self.data_processor.metadata['categorical_columns']

        if not categorical_cols:
            messagebox.showinfo("No Categorical Columns", "No categorical columns found for encoding")
            return

        def encoding_worker():
            try:
                self.create_dummies_btn.configure(text="Creating...", state="disabled")
                success = self.data_cleaner.create_dummy_variables(drop_first=drop_first)

                if success:
                    new_cols = len(self.data_processor.data.columns)
                    messagebox.showinfo("Success", f"Created dummy variables. Dataset now has {new_cols} columns")
                    self.after(0, self.update_callback)
                    self.after(0, self.refresh_data)
                else:
                    messagebox.showerror("Error", "Failed to create dummy variables")

            except Exception as exc:
                messagebox.showerror("Error", f"Error creating dummy variables: {exc}")
            finally:
                self.after(0, lambda: self.create_dummies_btn.configure(text="Create Dummy Variables", state="normal"))

        threading.Thread(target=encoding_worker, daemon=True).start()

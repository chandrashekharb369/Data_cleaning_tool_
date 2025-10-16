# Smart Data Cleaner 🧹📊

> Revolutionizing data preprocessing with intelligent automation and user-friendly interface

## Overview

In the era of big data, analysts and data scientists spend over 70% of their time cleaning and preparing data before analysis. The Smart Data Cleaner aims to revolutionize this process by providing an intelligent, automated, and user-friendly Python application that simplifies the entire data preprocessing workflow.

## 🧩 Key Features

- **Automatic column type classification** (numeric/text)
- **Duplicate detection and removal**
- **Missing value imputation** with intelligent filling options
- **One-hot encoding** for categorical data
- **Outlier detection** using IQR/Z-score methods
- **Correlation and feature importance analysis**
- **Quick visualization dashboard** (histogram, heatmap, bar chart)
- **Interactive GUI** built using CustomTkinter
- **Export options** (CSV, Excel, JSON)
- **AI-powered data summary and insights**

## 💡 Tech Stack

- **Language**: Python
- **Libraries**: Pandas, NumPy, Scikit-learn, Seaborn, Matplotlib, CustomTkinter, YData Profiling
- **Architecture**: Modular structure separating GUI, backend logic, and visualization

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-data-cleaner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 📁 Project Structure

```
smart-data-cleaner/
├── main.py                 # Entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window
│   ├── components/         # UI components
│   └── styles.py           # GUI styling
├── core/
│   ├── __init__.py
│   ├── data_processor.py   # Core data processing logic
│   ├── cleaner.py          # Data cleaning functions
│   ├── analyzer.py         # Data analysis functions
│   └── exporter.py         # Export functionality
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Utility functions
│   └── validators.py       # Data validation
├── visualizations/
│   ├── __init__.py
│   ├── charts.py           # Chart generation
│   └── dashboard.py        # Visualization dashboard
└── requirements.txt
```

## 🎯 Impact

This project drastically reduces the time and effort required for manual data cleaning, offering a smart preprocessing assistant that can be used by students, analysts, and data scientists alike. It's not just a utility — it's a step toward automated data intelligence.

## 📝 License

MIT License - see LICENSE file for details.
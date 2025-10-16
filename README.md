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
https://github.com/chandrashekharb369/Data_cleaning_tool_.git
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


## Smaple Application Images
<img width="1482" height="957" alt="image" src="https://github.com/user-attachments/assets/c4b20e49-88ec-4db2-a648-01ee0a7fb590" />
<img width="1475" height="956" alt="image" src="https://github.com/user-attachments/assets/feeb7108-6d9c-4ec8-b04b-a89682d7b865" />
<img width="1466" height="911" alt="image" src="https://github.com/user-attachments/assets/84cb04a1-c41f-457d-9957-615d1865df34" />
<img width="1491" height="966" alt="image" src="https://github.com/user-attachments/assets/2b81d0cb-c710-44f3-86fe-d0c7b2fca8c9" />
<img width="1482" height="963" alt="image" src="https://github.com/user-attachments/assets/509c26ca-294d-4d48-ab3e-7bc28e7ea429" />
<img width="1478" height="977" alt="image" src="https://github.com/user-attachments/assets/ff9a9af3-0100-4b03-931e-9032c5f88826" />
<img width="1488" height="963" alt="image" src="https://github.com/user-attachments/assets/f8277ac0-05ef-4945-8fd0-3858a01336ea" />
<img width="1494" height="966" alt="image" src="https://github.com/user-attachments/assets/1a888fbd-e41d-4ece-929f-35c575bb5c4a" />

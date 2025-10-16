"""
Smart Data Cleaner Demo - Console Version
Demonstration of core functionality without GUI
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.data_processor import DataProcessor
from core.cleaner import DataCleaner
from core.analyzer import DataAnalyzer
from core.exporter import DataExporter
from utils.helpers import generate_sample_data, format_bytes
from utils.validators import DataValidator

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🧹 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📊 {title}")
    print("-" * 40)

def demo_data_loading():
    """Demonstrate data loading functionality"""
    print_header("SMART DATA CLEANER - DEMO")
    
    # Initialize core components
    data_processor = DataProcessor()
    data_cleaner = DataCleaner(data_processor)
    data_analyzer = DataAnalyzer(data_processor)
    data_exporter = DataExporter(data_processor)
    validator = DataValidator()
    
    print_section("Data Loading")
    
    # Generate sample data
    print("🎲 Generating sample dataset...")
    sample_data = generate_sample_data()
    
    # Load data into processor
    data_processor.data = sample_data
    data_processor.original_data = sample_data.copy()
    data_processor._update_metadata()
    data_processor._log_action("Loaded sample dataset")
    
    print(f"✅ Successfully loaded dataset with {sample_data.shape[0]:,} rows and {sample_data.shape[1]} columns")
    
    # Show data summary
    summary = data_processor.get_data_summary()
    print(f"📏 Dataset shape: {summary['basic_info']['rows']:,} rows × {summary['basic_info']['columns']} columns")
    print(f"💾 Memory usage: {summary['basic_info']['memory_usage']}")
    print(f"🔢 Numeric columns: {summary['column_types']['numeric']}")
    print(f"📝 Categorical columns: {summary['column_types']['categorical']}")
    print(f"❌ Missing values: {summary['missing_data']['total_missing']:,}")
    print(f"🔄 Duplicate rows: {summary['basic_info']['duplicates']:,}")
    
    return data_processor, data_cleaner, data_analyzer, data_exporter, validator

def demo_data_validation(data_processor, validator):
    """Demonstrate data validation"""
    print_section("Data Validation")
    
    # Validate the dataframe
    validation_result = validator.validate_dataframe(data_processor.data)
    
    print(f"✅ Data validation: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
    
    if validation_result['errors']:
        print("❌ Errors found:")
        for error in validation_result['errors']:
            print(f"  • {error}")
    
    if validation_result['warnings']:
        print("⚠️  Warnings:")
        for warning in validation_result['warnings'][:3]:  # Show first 3
            print(f"  • {warning}")
    
    if validation_result['info']:
        print("ℹ️  Information:")
        for info in validation_result['info'][:3]:  # Show first 3
            print(f"  • {info}")
    
    # Show statistics
    stats = validation_result.get('statistics', {})
    if stats:
        print(f"\n📈 Validation Statistics:")
        print(f"  • Total missing values: {stats.get('total_missing_values', 0):,}")
        print(f"  • Missing percentage: {stats.get('missing_percentage', 0):.2f}%")
        print(f"  • Duplicate rows: {stats.get('duplicate_rows', 0):,}")

def demo_data_cleaning(data_cleaner):
    """Demonstrate data cleaning functionality"""
    print_section("Data Cleaning")
    
    print("🧹 Running automatic data cleaning...")
    
    # Perform auto-cleaning
    results = data_cleaner.auto_clean()
    
    if results.get('auto_clean_completed'):
        print("✅ Auto-cleaning completed successfully!")
        
        if results.get('duplicates_removed'):
            print("  • Duplicates removed")
        
        if results.get('missing_values_handled'):
            print("  • Missing values handled")
        
        if results.get('outliers_detected'):
            outlier_counts = results['outliers_detected']
            total_outliers = sum(outlier_counts.values()) if outlier_counts else 0
            print(f"  • {total_outliers} outliers detected and removed")
        
        if results.get('types_converted'):
            print("  • Data types optimized")
    
    else:
        print("❌ Auto-cleaning encountered issues")
        if 'error' in results:
            print(f"Error: {results['error']}")

def demo_data_analysis(data_analyzer):
    """Demonstrate data analysis functionality"""
    print_section("Data Analysis")
    
    # Correlation analysis
    print("📈 Running correlation analysis...")
    correlation_results = data_analyzer.correlation_analysis()
    
    if 'error' not in correlation_results:
        high_correlations = correlation_results.get('high_correlations', [])
        print(f"  • Found {len(high_correlations)} high correlations (|r| > 0.7)")
        
        if high_correlations:
            print("  Top correlations:")
            for i, corr in enumerate(high_correlations[:3]):  # Show top 3
                print(f"    {i+1}. {corr['variable1']} ↔ {corr['variable2']}: {corr['correlation']:.3f}")
    
    # Data quality assessment
    print("\n🔍 Assessing data quality...")
    quality_results = data_analyzer.data_quality_assessment()
    
    if 'error' not in quality_results:
        completeness = quality_results.get('completeness', {})
        print(f"  • Data completeness: {completeness.get('percentage', 0):.2f}%")
        print(f"  • Overall quality score: {quality_results.get('overall_score', 0):.1f}/100")
    
    # Generate insights
    print("\n🤖 Generating AI-powered insights...")
    insights = data_analyzer.generate_insights()
    
    if 'error' not in insights:
        key_insights = insights.get('key_insights', [])
        recommendations = insights.get('recommendations', [])
        
        if key_insights:
            print("  Key insights:")
            for insight in key_insights[:3]:  # Show first 3
                print(f"    • {insight}")
        
        if recommendations:
            print("  Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"    • {rec}")

def demo_data_export(data_exporter):
    """Demonstrate data export functionality"""
    print_section("Data Export")
    
    # Create export directory
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    print("💾 Exporting cleaned data...")
    
    # Export to CSV
    csv_success = data_exporter.export_to_csv(str(export_dir / "cleaned_data.csv"))
    print(f"  • CSV export: {'✅ Success' if csv_success else '❌ Failed'}")
    
    # Export to Excel
    excel_success = data_exporter.export_to_excel(str(export_dir / "cleaned_data.xlsx"))
    print(f"  • Excel export: {'✅ Success' if excel_success else '❌ Failed'}")
    
    # Export summary report
    report_success = data_exporter.export_summary_report(str(export_dir / "data_report.json"))
    print(f"  • Summary report: {'✅ Success' if report_success else '❌ Failed'}")
    
    if csv_success or excel_success or report_success:
        print(f"\n📁 Files exported to: {export_dir.absolute()}")

def main():
    """Main demo function"""
    try:
        # Load and process data
        data_processor, data_cleaner, data_analyzer, data_exporter, validator = demo_data_loading()
        
        # Validate data
        demo_data_validation(data_processor, validator)
        
        # Clean data
        demo_data_cleaning(data_cleaner)
        
        # Analyze data
        demo_data_analysis(data_analyzer)
        
        # Export data
        demo_data_export(data_exporter)
        
        print_header("DEMO COMPLETED SUCCESSFULLY!")
        print("🎉 Smart Data Cleaner demonstrated all core features:")
        print("   • Data loading and validation")
        print("   • Automatic data cleaning")
        print("   • Advanced data analysis")
        print("   • Multi-format data export")
        print("\n🚀 Ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
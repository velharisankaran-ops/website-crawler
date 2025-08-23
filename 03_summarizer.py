"""
03_summarizer.py

Takes 02_analyzer.py output and creates:
- Summary dashboard (counts + examples)
- Grouped details (duplicates, cannibalization)
- Charts for visual overview
"""

import pandas as pd
import matplotlib
# Use non-interactive backend for matplotlib to avoid display issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import argparse
from pathlib import Path

# Set console output encoding for Windows
if sys.platform.startswith('win'):
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def safe_print(*args, **kwargs):
    """Safely print Unicode characters to Windows console"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback to ascii-only output if unicode fails
        print(*[str(arg).encode('ascii', 'replace').decode('ascii') for arg in args], **kwargs)

def is_missing(val):
    """Helper: safe check for missing values"""
    return pd.isna(val) or str(val).strip() == ""

def generate_summary(csv_path: str, output_dir: str = "reports"):
    """Generate SEO summary report from analyzer output"""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # === 1. Load Data ===
    try:
        df = pd.read_csv(csv_path)
        safe_print(f"[SUCCESS] Loaded {len(df)} records from {csv_path}")
    except Exception as e:
        safe_print(f"[ERROR] Error loading {csv_path}: {e}")
        return

    # === 2. Status Codes Summary ===
    status_summary = df.groupby("Status_Code")["URL"].count().reset_index()
    status_summary.rename(columns={"URL": "Count"}, inplace=True)

    # === 3. Title Issues ===
    title_missing = df[df["Title"].apply(is_missing)]
    title_too_short = df[df["Title"].str.len() < 30]
    title_too_long = df[df["Title"].str.len() > 65]
    title_dupes = df.groupby("Title").filter(lambda x: len(x) > 1 and not is_missing(x["Title"].iloc[0]) if len(x) > 0 else False)

    # === 4. Meta Description Issues ===
    meta_missing = df[df["Meta_Description"].apply(is_missing)]
    meta_too_short = df[df["Meta_Description"].str.len() < 70]
    meta_too_long = df[df["Meta_Description"].str.len() > 160]
    meta_dupes = df.groupby("Meta_Description").filter(
        lambda x: len(x) > 1 and not is_missing(x["Meta_Description"].iloc[0]) if len(x) > 0 else False
    )

    # === 5. Heading Issues ===
    h1_missing = df[df["H1"].apply(is_missing)]
    h1_dupes = df.groupby("H1").filter(
        lambda x: len(x) > 1 and not is_missing(x["H1"].iloc[0]) if len(x) > 0 else False
    )
    h2_missing = df[df["H2s"].apply(is_missing)]

    # === 6. Canonical Issues ===
    canonical_missing = df[df["Canonical"].apply(is_missing)]
    canonical_conflict = df[df["Canonical"] != df["URL"]]

    # === 7. Word Count Issues ===
    thin_content = df[df["Word_Count"] < 300]
    long_content = df[df["Word_Count"] > 2000]

    # === 8. Image Issues ===
    df["Images_Missing_Alt"] = df["Image_Count"] - df["Images_With_Alt_Count"]
    image_no_alt = df[df["Images_Missing_Alt"] > 0]
    image_no_images = df[df["Image_Count"] == 0]

    # === 9. Links Issues ===
    weak_internal_links = df[df["Internal_Links"] < 3]
    no_external_links = df[df["External_Links"] == 0]

    # === 10. Robots Issues ===
    robots_noindex = df[df["Meta_Robots"].str.contains("noindex", case=False, na=False)]
    robots_nofollow = df[df["Meta_Robots"].str.contains("nofollow", case=False, na=False)]

    # === 11. Build Summary Table with Severity ===
    summary_data = [
        ("Status 4xx", len(df[df["Status_Code"].between(400, 499)]), "Critical", 
         df[df["Status_Code"].between(400, 499)]["URL"].head(3).tolist()),
        ("Missing Titles", len(title_missing), "Critical", title_missing["URL"].head(3).tolist()),
        ("Duplicate Titles", len(title_dupes), "High", title_dupes["URL"].head(3).tolist()),
        ("Short Titles", len(title_too_short), "Medium", title_too_short["URL"].head(3).tolist()),
        ("Long Titles", len(title_too_long), "Low", title_too_long["URL"].head(3).tolist()),
        ("Missing Meta", len(meta_missing), "High", meta_missing["URL"].head(3).tolist()),
        ("Duplicate Meta", len(meta_dupes), "Medium", meta_dupes["URL"].head(3).tolist()),
        ("Short Meta", len(meta_too_short), "Low", meta_too_short["URL"].head(3).tolist()),
        ("Long Meta", len(meta_too_long), "Low", meta_too_long["URL"].head(3).tolist()),
        ("Missing H1", len(h1_missing), "High", h1_missing["URL"].head(3).tolist()),
        ("Duplicate H1", len(h1_dupes), "High", h1_dupes["URL"].head(3).tolist()),
        ("Missing H2", len(h2_missing), "Medium", h2_missing["URL"].head(3).tolist()),
        ("Missing Canonical", len(canonical_missing), "High", canonical_missing["URL"].head(3).tolist()),
        ("Canonical Conflict", len(canonical_conflict), "High", canonical_conflict["URL"].head(3).tolist()),
        ("Thin Content (<300)", len(thin_content), "Medium", thin_content["URL"].head(3).tolist()),
        ("Long Content (>2000)", len(long_content), "Low", long_content["URL"].head(3).tolist()),
        ("Missing Alt", len(image_no_alt), "Medium", image_no_alt["URL"].head(3).tolist()),
        ("No Images", len(image_no_images), "Low", image_no_images["URL"].head(3).tolist()),
        ("Weak Internal Links (<3)", len(weak_internal_links), "Low", weak_internal_links["URL"].head(3).tolist()),
        ("No External Links", len(no_external_links), "Low", no_external_links["URL"].head(3).tolist()),
        ("Robots noindex", len(robots_noindex), "Critical" if len(robots_noindex) > 0 else "Info", 
         robots_noindex["URL"].head(3).tolist() if not robots_noindex.empty else []),
        ("Robots nofollow", len(robots_nofollow), "Medium", 
         robots_nofollow["URL"].head(3).tolist() if not robots_nofollow.empty else []),
    ]

    summary_df = pd.DataFrame(summary_data, columns=["Issue", "Count", "Severity", "Example_URLs"])
    
    # Sort by severity (Critical > High > Medium > Low > Info) and then by count
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    summary_df["severity_rank"] = summary_df["Severity"].map(severity_order)
    summary_df = summary_df.sort_values(["severity_rank", "Count"], ascending=[True, False])
    summary_df = summary_df.drop("severity_rank", axis=1)

    # === 12. Save Excel Report ===
    excel_path = output_path / "seo_summary.xlsx"
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Summary sheet with formatting
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        # Format summary sheet
        workbook = writer.book
        worksheet = writer.sheets["Summary"]
        
        # Add color formatting based on severity
        format_critical = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        format_high = workbook.add_format({'bg_color': '#FFD3B5', 'font_color': '#974806'})
        format_medium = workbook.add_format({'bg_color': '#FFEEBA', 'font_color': '#9C7C0D'})
        format_low = workbook.add_format({'bg_color': '#C6E2FF', 'font_color': '#0D5F9C'})
        format_info = workbook.add_format({'bg_color': '#D8EAD3', 'font_color': '#0C5E0D'})
        
        # Apply formatting
        for row_num in range(1, len(summary_df) + 1):
            severity = summary_df.iloc[row_num - 1]["Severity"]
            if severity == "Critical":
                worksheet.conditional_format(f'A{row_num + 1}:D{row_num + 1}', 
                                          {'type': 'no_errors', 'format': format_critical})
            elif severity == "High":
                worksheet.conditional_format(f'A{row_num + 1}:D{row_num + 1}', 
                                          {'type': 'no_errors', 'format': format_high})
            elif severity == "Medium":
                worksheet.conditional_format(f'A{row_num + 1}:D{row_num + 1}', 
                                          {'type': 'no_errors', 'format': format_medium})
            elif severity == "Low":
                worksheet.conditional_format(f'A{row_num + 1}:D{row_num + 1}', 
                                          {'type': 'no_errors', 'format': format_low})
            else:  # Info
                worksheet.conditional_format(f'A{row_num + 1}:D{row_num + 1}', 
                                          {'type': 'no_errors', 'format': format_info})
        
        # Auto-adjust column widths
        for column in summary_df:
            if column == "Example_URLs":
                # Make URL column wider
                col_idx = summary_df.columns.get_loc(column)
                writer.sheets['Summary'].set_column(col_idx, col_idx, 40)
            else:
                column_width = max(summary_df[column].astype(str).map(len).max(), len(column)) + 2
                col_idx = summary_df.columns.get_loc(column)
                writer.sheets['Summary'].set_column(col_idx, col_idx, column_width)
        
        # Detailed sheets
        status_summary.to_excel(writer, sheet_name="Status Codes", index=False)
        if not title_dupes.empty:
            title_dupes.to_excel(writer, sheet_name="Duplicate Titles", index=False)
        if not meta_dupes.empty:
            meta_dupes.to_excel(writer, sheet_name="Duplicate Meta", index=False)
        if not h1_dupes.empty:
            h1_dupes.to_excel(writer, sheet_name="Duplicate H1", index=False)
        if not thin_content.empty:
            thin_content.to_excel(writer, sheet_name="Thin Content", index=False)
        if not image_no_alt.empty:
            image_no_alt.to_excel(writer, sheet_name="Missing Alt Images", index=False)
        if not weak_internal_links.empty:
            weak_internal_links.to_excel(writer, sheet_name="Weak Internal Links", index=False)

    # === 13. Generate Charts ===
    plt.figure(figsize=(10, 8))
    
    # Status Code Pie Chart
    plt.subplot(2, 1, 1)
    status_summary.set_index('Status_Code')['Count'].plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title('Status Code Distribution')
    plt.ylabel('')
    
    # Issues Bar Chart
    plt.subplot(2, 1, 2)
    summary_df.set_index('Issue')['Count'].plot(kind='barh', figsize=(10, 12))
    plt.title('SEO Issues Count')
    plt.tight_layout()
    
    # Save combined chart
    chart_path = output_path / "seo_summary_charts.png"
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    
    safe_print(f"[SUCCESS] SEO summary report generated: {excel_path}")
    safe_print(f"[INFO] Charts saved to: {chart_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate SEO summary report from analyzer output')
    parser.add_argument('input_csv', help='Path to the analyzer output CSV file')
    parser.add_argument('--output', '-o', default='reports', help='Output directory for reports (default: reports/)')
    
    args = parser.parse_args()
    generate_summary(args.input_csv, args.output)

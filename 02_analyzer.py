#!/usr/bin/env python3
"""
Enhanced SEO Analyzer

This script analyzes the output from the SEO crawler and generates a comprehensive
Excel report with multiple sheets for different SEO issues.
"""

import pandas as pd
from typing import List, Dict, Tuple
import argparse
from pathlib import Path

class EnhancedSEOAnalyzer:
    def __init__(self, input_file: str, output_file: str):
        """Initialize the analyzer with input and output file paths."""
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.summary_data = []
        
    def load_data(self) -> bool:
        """Load and validate the input CSV file."""
        try:
            self.df = pd.read_csv(self.input_file)
            
            # Ensure required columns exist
            required_columns = [
                'URL', 'Status_Code', 'Title', 'Meta_Description', 'H1', 'H2s',
                'Canonical', 'Meta_Robots', 'Word_Count', 'Internal_Links',
                'External_Links', 'Image_Count', 'Images_With_Alt_Count'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                print(f"Error: Missing required columns: {', '.join(missing_columns)}")
                return False
                
            # Clean data
            self.df = self.df.fillna('')
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def analyze_status_codes(self) -> pd.DataFrame:
        """Analyze HTTP status codes."""
        status_summary = self.df['Status_Code'].value_counts().reset_index()
        status_summary.columns = ['Status_Code', 'Count']
        
        # Add to summary
        for _, row in status_summary.iterrows():
            if row['Status_Code'] != 200:
                self.summary_data.append({
                    'Issue': f'Non-200 Status: {row["Status_Code"]}',
                    'Count': row['Count']
                })
                
        return self.df[self.df['Status_Code'] != 200][['URL', 'Status_Code']]
    
    def analyze_titles(self) -> Dict[str, pd.DataFrame]:
        """Analyze title tags."""
        results = {}
        
        # Missing titles
        missing = self.df[self.df['Title'].str.strip() == '']
        if not missing.empty:
            results['Titles_Missing'] = missing[['URL', 'Title']]
            self.summary_data.append({
                'Issue': 'Missing Titles',
                'Count': len(missing)
            })
        
        # Duplicate titles
        title_counts = self.df[self.df['Title'] != '']['Title'].value_counts()
        duplicate_titles = title_counts[title_counts > 1].index
        if len(duplicate_titles) > 0:
            dupes = self.df[self.df['Title'].isin(duplicate_titles)]
            results['Titles_Duplicate'] = dupes[['URL', 'Title']].sort_values('Title')
            self.summary_data.append({
                'Issue': 'Duplicate Titles',
                'Count': len(dupes)
            })
        
        # Title length issues
        self.df['Title_Length'] = self.df['Title'].str.len()
        too_short = self.df[(self.df['Title_Length'] > 0) & (self.df['Title_Length'] < 30)]
        too_long = self.df[self.df['Title_Length'] > 60]
        
        if not too_short.empty:
            results['Titles_Too_Short'] = too_short[['URL', 'Title', 'Title_Length']].copy()
            results['Titles_Too_Short'].insert(1, 'Title_Text', too_short['Title'].values)
            self.summary_data.append({
                'Issue': 'Titles Too Short (<30 chars)',
                'Count': len(too_short)
            })
            
        if not too_long.empty:
            results['Titles_Too_Long'] = too_long[['URL', 'Title', 'Title_Length']].copy()
            results['Titles_Too_Long'].insert(1, 'Title_Text', too_long['Title'].values)
            self.summary_data.append({
                'Issue': 'Titles Too Long (>60 chars)',
                'Count': len(too_long)
            })
        
        return results
    
    def analyze_meta_descriptions(self) -> Dict[str, pd.DataFrame]:
        """Analyze meta descriptions."""
        results = {}
        
        # Missing meta descriptions
        missing = self.df[self.df['Meta_Description'].str.strip() == '']
        if not missing.empty:
            results['Meta_Missing'] = missing[['URL', 'Meta_Description']]
            self.summary_data.append({
                'Issue': 'Missing Meta Descriptions',
                'Count': len(missing)
            })
        
        # Meta description length
        self.df['Meta_Length'] = self.df['Meta_Description'].str.len()
        too_short = self.df[(self.df['Meta_Length'] > 0) & (self.df['Meta_Length'] < 50)]
        too_long = self.df[self.df['Meta_Length'] > 160]
        
        if not too_short.empty:
            results['Meta_Too_Short'] = too_short[['URL', 'Meta_Description', 'Meta_Length']].copy()
            results['Meta_Too_Short'].insert(1, 'Meta_Text', too_short['Meta_Description'].values)
            self.summary_data.append({
                'Issue': 'Meta Descriptions Too Short (<50 chars)',
                'Count': len(too_short)
            })
            
        if not too_long.empty:
            results['Meta_Too_Long'] = too_long[['URL', 'Meta_Description', 'Meta_Length']].copy()
            results['Meta_Too_Long'].insert(1, 'Meta_Text', too_long['Meta_Description'].values)
            self.summary_data.append({
                'Issue': 'Meta Descriptions Too Long (>160 chars)',
                'Count': len(too_long)
            })
        
        return results
    
    def analyze_headings(self) -> Dict[str, pd.DataFrame]:
        """Analyze heading structure."""
        results = {}
        
        # Missing H1
        missing_h1 = self.df[self.df['H1'].str.strip() == '']
        if not missing_h1.empty:
            results['Headings_Missing_H1'] = missing_h1[['URL', 'H1']].copy()
            results['Headings_Missing_H1'].insert(1, 'H1_Text', missing_h1['H1'].values)
            self.summary_data.append({
                'Issue': 'Missing H1',
                'Count': len(missing_h1)
            })
        
        # Duplicate H1s
        h1_counts = self.df[self.df['H1'] != '']['H1'].value_counts()
        duplicate_h1s = h1_counts[h1_counts > 1].index
        if len(duplicate_h1s) > 0:
            dupes = self.df[self.df['H1'].isin(duplicate_h1s)]
            results['Headings_Duplicate_H1'] = dupes[['URL', 'H1']].sort_values('H1').copy()
            results['Headings_Duplicate_H1'].insert(1, 'H1_Text', dupes['H1'].values)
            self.summary_data.append({
                'Issue': 'Duplicate H1s',
                'Count': len(dupes)
            })
        
        # Missing H2s
        missing_h2 = self.df[self.df['H2s'].str.strip() == '']
        if not missing_h2.empty:
            results['Headings_Missing_H2'] = missing_h2[['URL', 'H2s']].copy()
            results['Headings_Missing_H2'].insert(1, 'H2_Text', missing_h2['H2s'].values)
            self.summary_data.append({
                'Issue': 'Missing H2s',
                'Count': len(missing_h2)
            })
        
        return results
    
    def analyze_canonicals(self) -> Dict[str, pd.DataFrame]:
        """Analyze canonical tags."""
        results = {}
        
        # Missing canonicals
        missing = self.df[self.df['Canonical'].str.strip() == '']
        if not missing.empty:
            results['Canonical_Missing'] = missing[['URL', 'Title', 'Canonical']].copy()
            # Add more context
            results['Canonical_Missing'].insert(1, 'Title_Text', missing['Title'].values)
            results['Canonical_Missing'].insert(3, 'Status_Code', missing['Status_Code'].values)
            self.summary_data.append({
                'Issue': 'Missing Canonical Tags',
                'Count': len(missing)
            })
        
        # Canonical points to different URL
        self.df['Canonical_Match'] = self.df.apply(
            lambda x: x['URL'] == x['Canonical'] if x['Canonical'] else True, 
            axis=1
        )
        mismatched = self.df[(~self.df['Canonical_Match']) & (self.df['Canonical'] != '')]
        if not mismatched.empty:
            results['Canonical_Mismatch'] = mismatched[['URL', 'Title', 'Canonical']].copy()
            # Add more context
            results['Canonical_Mismatch'].insert(1, 'Title_Text', mismatched['Title'].values)
            results['Canonical_Mismatch'].insert(4, 'Status_Code', mismatched['Status_Code'].values)
            results['Canonical_Mismatch'].insert(5, 'Is_Self_Referencing', 
                mismatched.apply(lambda x: 'Yes' if x['URL'] == x['Canonical'] else 'No', axis=1).values)
            self.summary_data.append({
                'Issue': 'Canonical Mismatch',
                'Count': len(mismatched)
            })
        
        return results
    
    def analyze_word_count(self) -> Dict[str, pd.DataFrame]:
        """Analyze word count."""
        results = {}
        
        # Thin content
        thin = self.df[self.df['Word_Count'] < 300]
        if not thin.empty:
            results['WordCount_Thin'] = thin[['URL', 'Word_Count']]
            self.summary_data.append({
                'Issue': 'Thin Content (<300 words)',
                'Count': len(thin)
            })
        
        # Heavy content
        heavy = self.df[self.df['Word_Count'] > 2000]
        if not heavy.empty:
            results['WordCount_Heavy'] = heavy[['URL', 'Word_Count']]
            self.summary_data.append({
                'Issue': 'Heavy Content (>2000 words)',
                'Count': len(heavy)
            })
        
        # Word count stats
        word_stats = pd.DataFrame({
            'Statistic': ['Average', 'Minimum', 'Maximum', 'Median'],
            'Word Count': [
                self.df['Word_Count'].mean(),
                self.df['Word_Count'].min(),
                self.df['Word_Count'].max(),
                self.df['Word_Count'].median()
            ]
        })
        results['WordCount_Stats'] = word_stats
        
        return results
    
    def analyze_cannibalization(self) -> Dict[str, pd.DataFrame]:
        """Analyze content cannibalization."""
        results = {}
        
        # Title cannibalization
        title_counts = self.df[self.df['Title'] != '']['Title'].value_counts()
        cannibal_titles = title_counts[title_counts > 1].index
        if len(cannibal_titles) > 0:
            cannibal = self.df[self.df['Title'].isin(cannibal_titles)]
            results['Cannibalization_Title'] = cannibal[['URL', 'Title']].sort_values('Title')
            self.summary_data.append({
                'Issue': 'Title Cannibalization',
                'Count': len(cannibal)
            })
        
        # H1 cannibalization
        h1_counts = self.df[self.df['H1'] != '']['H1'].value_counts()
        cannibal_h1s = h1_counts[h1_counts > 1].index
        if len(cannibal_h1s) > 0:
            cannibal = self.df[self.df['H1'].isin(cannibal_h1s)]
            results['Cannibalization_H1'] = cannibal[['URL', 'H1']].sort_values('H1')
            self.summary_data.append({
                'Issue': 'H1 Cannibalization',
                'Count': len(cannibal)
            })
        
        return results
    
    def analyze_images(self) -> Dict[str, pd.DataFrame]:
        """Analyze image optimization."""
        results = {}
        
        # Images missing alt text
        self.df['Images_Missing_Alt'] = self.df['Image_Count'] - self.df['Images_With_Alt_Count']
        missing_alt = self.df[self.df['Images_Missing_Alt'] > 0]
        
        if not missing_alt.empty:
            results['Images_Alt_Missing'] = missing_alt[['URL', 'Image_Count', 'Images_With_Alt_Count', 'Images_Missing_Alt']]
            self.summary_data.append({
                'Issue': 'Images Missing Alt Text',
                'Count': len(missing_alt)
            })
        
        # Pages with no images
        no_images = self.df[self.df['Image_Count'] == 0]
        if not no_images.empty:
            results['Images_None'] = no_images[['URL', 'Image_Count']]
            self.summary_data.append({
                'Issue': 'Pages with No Images',
                'Count': len(no_images)
            })
        
        return results
    
    def analyze_links(self) -> Dict[str, pd.DataFrame]:
        """Analyze internal and external links."""
        results = {}
        
        # Pages with too few internal links
        few_internal = self.df[self.df['Internal_Links'] < 3]
        if not few_internal.empty:
            results['Links_Internal_Few'] = few_internal[['URL', 'Internal_Links']]
            self.summary_data.append({
                'Issue': 'Pages with <3 Internal Links',
                'Count': len(few_internal)
            })
        
        # Pages with no external links
        no_external = self.df[self.df['External_Links'] == 0]
        if not no_external.empty:
            results['Links_External_None'] = no_external[['URL', 'External_Links']]
            self.summary_data.append({
                'Issue': 'Pages with No External Links',
                'Count': len(no_external)
            })
        
        # Link stats
        link_stats = pd.DataFrame({
            'Statistic': ['Average', 'Minimum', 'Maximum', 'Median'],
            'Internal Links': [
                self.df['Internal_Links'].mean(),
                self.df['Internal_Links'].min(),
                self.df['Internal_Links'].max(),
                self.df['Internal_Links'].median()
            ],
            'External Links': [
                self.df['External_Links'].mean(),
                self.df['External_Links'].min(),
                self.df['External_Links'].max(),
                self.df['External_Links'].median()
            ]
        })
        results['Links_Stats'] = link_stats
        
        return results
    
    def analyze_robots(self) -> Dict[str, pd.DataFrame]:
        """Analyze meta robots tags."""
        results = {}
        
        # Pages with noindex
        noindex = self.df[self.df['Meta_Robots'].str.contains('noindex', case=False, na=False)]
        if not noindex.empty:
            results['Robots_NoIndex'] = noindex[['URL', 'Meta_Robots']]
            self.summary_data.append({
                'Issue': 'Pages with noindex',
                'Count': len(noindex)
            })
        
        # Pages with nofollow
        nofollow = self.df[self.df['Meta_Robots'].str.contains('nofollow', case=False, na=False)]
        if not nofollow.empty:
            results['Robots_NoFollow'] = nofollow[['URL', 'Meta_Robots']]
            self.summary_data.append({
                'Issue': 'Pages with nofollow',
                'Count': len(nofollow)
            })
        
        return results
    
    def generate_summary(self) -> pd.DataFrame:
        """Generate summary statistics."""
        summary = pd.DataFrame(self.summary_data)
        if not summary.empty:
            summary = summary.sort_values('Count', ascending=False)
        return summary
    
    def add_full_context(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all relevant columns to provide full context."""
        if df.empty or 'URL' not in df.columns or 'URL' not in self.df.columns:
            return df
            
        # Get all available columns from the original data
        all_columns = [col for col in self.df.columns if col != 'URL']  # Exclude URL to prevent duplicates
        
        # Create a copy to avoid modifying the original
        result = df.copy()
        
        # Get only the columns we need to merge
        cols_to_merge = ['URL']  # Always include URL for merging
        
        # Add other columns that aren't already in the result
        for col in all_columns:
            if col not in result.columns:
                cols_to_merge.append(col)
        
        # If we have columns to merge, do the merge
        if len(cols_to_merge) > 1:  # More than just 'URL'
            # Get the subset of original data we need
            merge_data = self.df[cols_to_merge].drop_duplicates(subset=['URL'])
            
            # Merge with the result
            result = result.merge(
                merge_data,
                on='URL',
                how='left'
            )
        
        # Define the preferred column order
        preferred_order = [
            'URL', 'Title', 'Status_Code', 'Meta_Description', 
            'H1', 'H2s', 'Canonical', 'Meta_Robots', 'Word_Count',
            'Internal_Links', 'External_Links', 'Image_Count', 'Images_With_Alt_Count'
        ]
        
        # Get remaining columns that aren't in our preferred order
        remaining_cols = [col for col in result.columns if col not in preferred_order]
        
        # Combine the columns in our preferred order, then add any remaining columns
        final_cols = [col for col in preferred_order if col in result.columns] + remaining_cols
        
        # Only include columns that exist in the result
        final_cols = [col for col in final_cols if col in result.columns]
        
        # Remove any duplicate columns while preserving order
        seen = set()
        final_cols = [col for col in final_cols if not (col in seen or seen.add(col))]
        
        return result[final_cols]
    
    def analyze(self) -> bool:
        """Run all analyses and generate report."""
        try:
            # Create output directory if it doesn't exist
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(self.output_file, engine='xlsxwriter') as writer:
                # Run all analyses
                analyses = {
                    'Status': self.analyze_status_codes(),
                    **self.analyze_titles(),
                    **self.analyze_meta_descriptions(),
                    **self.analyze_headings(),
                    **self.analyze_canonicals(),
                    **self.analyze_word_count(),
                    **self.analyze_cannibalization(),
                    **self.analyze_images(),
                    **self.analyze_links(),
                    **self.analyze_robots()
                }
                
                # Write all sheets with full context
                for sheet_name, data in analyses.items():
                    if not data.empty:
                        # Add full context to each analysis result
                        data_with_context = self.add_full_context(data)
                        data_with_context.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                
                # Write summary sheet
                summary = self.generate_summary()
                if not summary.empty:
                    summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Auto-adjust column widths
                workbook = writer.book
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for idx, col in enumerate(analyses[list(analyses.keys())[0]].columns if analyses else []):
                        max_length = max(
                            analyses[list(analyses.keys())[0]][col].astype(str).apply(len).max(),
                            len(str(col))
                        ) + 2
                        worksheet.set_column(idx, idx, min(max_length, 50))
            
            print(f"\n[SUCCESS] SEO audit report generated: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced SEO Analyzer')
    parser.add_argument('input', nargs='?', default='seo_audit_results.csv',
                      help='Input CSV file (default: seo_audit_results.csv)')
    parser.add_argument('--output', default='seo_audit_report.xlsx',
                      help='Output Excel file (default: seo_audit_report.xlsx)')
    
    args = parser.parse_args()
    
    # Run analyzer
    analyzer = EnhancedSEOAnalyzer(args.input, args.output)
    
    if not analyzer.load_data():
        return 1
    
    if not analyzer.analyze():
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

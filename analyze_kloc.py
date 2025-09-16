#!/usr/bin/env python3
"""
Analyze KLOC (Lines of Code) for the Food Rescue project
"""

import os
import glob

def count_lines_in_file(filepath):
    """Count total, code, and comment lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if line.strip() == '')
        
        # Simple heuristic for comments
        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('//') or 
                stripped.startswith('#') or 
                stripped.startswith('/*') or 
                stripped.startswith('*') or
                stripped.startswith('<!--')):
                comment_lines += 1
        
        code_lines = total_lines - blank_lines - comment_lines
        
        return {
            'total': total_lines,
            'code': code_lines,
            'comments': comment_lines,
            'blank': blank_lines
        }
    except:
        return {'total': 0, 'code': 0, 'comments': 0, 'blank': 0}

def analyze_project():
    """Analyze KLOC for the entire project"""
    
    extensions = ['*.py', '*.js', '*.html', '*.css']
    results = {}
    grand_total = {'total': 0, 'code': 0, 'comments': 0, 'blank': 0}
    
    print("🔍 Food Rescue Project - KLOC Analysis")
    print("=" * 50)
    
    for ext in extensions:
        pattern = f"**/{ext}"
        files = glob.glob(pattern, recursive=True)
        
        ext_totals = {'total': 0, 'code': 0, 'comments': 0, 'blank': 0, 'files': 0}
        file_details = []
        
        for filepath in files:
            # Skip certain directories
            if any(skip in filepath for skip in ['node_modules', '.git', '__pycache__', 'venv', '.env']):
                continue
                
            counts = count_lines_in_file(filepath)
            file_details.append((filepath, counts))
            
            for key in ['total', 'code', 'comments', 'blank']:
                ext_totals[key] += counts[key]
            ext_totals['files'] += 1
        
        # Sort files by total lines (largest first)
        file_details.sort(key=lambda x: x[1]['total'], reverse=True)
        
        results[ext] = {
            'totals': ext_totals,
            'files': file_details
        }
        
        # Add to grand total
        for key in ['total', 'code', 'comments', 'blank']:
            grand_total[key] += ext_totals[key]
    
    # Print results
    print(f"\n📊 SUMMARY BY FILE TYPE:")
    print("-" * 50)
    
    for ext, data in results.items():
        totals = data['totals']
        print(f"{ext.upper():<6} Files: {totals['files']:>3} | "
              f"Total: {totals['total']:>6} | "
              f"Code: {totals['code']:>6} | "
              f"Comments: {totals['comments']:>4} | "
              f"Blank: {totals['blank']:>4}")
    
    print("-" * 50)
    print(f"{'TOTAL':<6} Files: {sum(r['totals']['files'] for r in results.values()):>3} | "
          f"Total: {grand_total['total']:>6} | "
          f"Code: {grand_total['code']:>6} | "
          f"Comments: {grand_total['comments']:>4} | "
          f"Blank: {grand_total['blank']:>4}")
    
    # Show largest files
    print(f"\n🔥 TOP 10 LARGEST FILES:")
    print("-" * 70)
    
    all_files = []
    for ext_data in results.values():
        all_files.extend(ext_data['files'])
    
    all_files.sort(key=lambda x: x[1]['total'], reverse=True)
    
    for i, (filepath, counts) in enumerate(all_files[:10]):
        filename = os.path.basename(filepath)
        print(f"{i+1:>2}. {filename:<25} {counts['total']:>6} lines | "
              f"Code: {counts['code']:>5} | Comments: {counts['comments']:>3} | Blank: {counts['blank']:>3}")
    
    # Calculate KLOC
    total_kloc = grand_total['total'] / 1000
    effective_kloc = grand_total['code'] / 1000
    
    print(f"\n🎯 FINAL KLOC ANALYSIS:")
    print("-" * 30)
    print(f"Total KLOC (all lines):     {total_kloc:.1f}K")
    print(f"Effective KLOC (code only): {effective_kloc:.1f}K")
    print(f"Non-effective (comments+blank): {(grand_total['comments'] + grand_total['blank'])/1000:.1f}K")
    print(f"Code efficiency: {(grand_total['code']/grand_total['total']*100):.1f}%")

if __name__ == "__main__":
    analyze_project()
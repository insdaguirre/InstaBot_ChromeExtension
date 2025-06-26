#!/usr/bin/env python3
"""
Cleanup script for old CSV exports - removes duplicate per-follow CSVs
Keeps only the most recent batch files and cleans up the spam
"""
import os
import pathlib
import glob
from datetime import datetime

def cleanup_old_csv_files():
    """Remove old per-follow CSV files, keep only batch files"""
    
    # Define paths
    csv_dirs = [
        "instagram_data/csv_exports",
        "csv_exports"
    ]
    
    total_removed = 0
    total_size_saved = 0
    
    for csv_dir in csv_dirs:
        if not os.path.exists(csv_dir):
            continue
            
        print(f"\n🔍 Scanning directory: {csv_dir}")
        
        # Get all CSV files
        csv_files = glob.glob(f"{csv_dir}/*.csv")
        
        # Separate batch files from old per-follow files
        batch_files = []
        old_files = []
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            
            # Keep batch files (they have "_batch_" in name)
            if "_batch_" in filename:
                batch_files.append(file_path)
            else:
                # These are the old per-follow spam files
                old_files.append(file_path)
        
        print(f"   📊 Found {len(batch_files)} batch files (keeping)")
        print(f"   🗑️  Found {len(old_files)} old spam files (removing)")
        
        # Remove old files
        for file_path in old_files:
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                total_removed += 1
                total_size_saved += file_size
                print(f"   ✅ Removed: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"   ❌ Error removing {file_path}: {e}")
    
    # Convert bytes to readable format
    if total_size_saved > 1024 * 1024:
        size_str = f"{total_size_saved / (1024 * 1024):.1f} MB"
    elif total_size_saved > 1024:
        size_str = f"{total_size_saved / 1024:.1f} KB"
    else:
        size_str = f"{total_size_saved} bytes"
    
    print(f"\n🎉 Cleanup complete!")
    print(f"   📁 Removed {total_removed} duplicate CSV files")
    print(f"   💾 Freed up {size_str} of disk space")
    print(f"   ✨ No more CSV spam - only clean batch files remain!")

if __name__ == "__main__":
    cleanup_old_csv_files() 
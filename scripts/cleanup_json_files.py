#!/usr/bin/env python3
"""
Cleanup script to remove all JSON files from cards_by_category directory.
Keeps only CSV files which are smaller and easier to parse.
"""

import os
import sys

def cleanup_json_files(directory: str = "cards_by_category"):
    """
    Remove all .json files from the specified directory.
    
    Args:
        directory: Path to the directory containing card files
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return False
    
    print(f"Scanning {directory}/ for JSON files...")
    
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_files.append(filename)
    
    if not json_files:
        print("No JSON files found. Nothing to clean up.")
        return True
    
    print(f"\nFound {len(json_files)} JSON files:")
    for filename in sorted(json_files):
        filepath = os.path.join(directory, filename)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  - {filename} ({size_kb:.1f} KB)")
    
    # Calculate space to be freed
    total_size_mb = sum(os.path.getsize(os.path.join(directory, f)) 
                        for f in json_files) / (1024 * 1024)
    
    print(f"\nTotal space to be freed: {total_size_mb:.2f} MB")
    
    # Confirm deletion
    response = input("\nDelete all JSON files? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cleanup cancelled.")
        return False
    
    print("\nDeleting JSON files...")
    deleted_count = 0
    
    for filename in json_files:
        filepath = os.path.join(directory, filename)
        try:
            os.remove(filepath)
            deleted_count += 1
            print(f"  ✓ Deleted {filename}")
        except Exception as e:
            print(f"  ✗ Error deleting {filename}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Cleanup complete!")
    print(f"Deleted: {deleted_count}/{len(json_files)} files")
    print(f"Space freed: {total_size_mb:.2f} MB")
    print(f"{'='*60}")
    
    # Show remaining CSV files
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    print(f"\nRemaining CSV files: {len(csv_files)}")
    
    return deleted_count == len(json_files)

if __name__ == "__main__":
    # Get directory from command line or use default
    directory = sys.argv[1] if len(sys.argv) > 1 else "cards_by_category"
    
    success = cleanup_json_files(directory)
    sys.exit(0 if success else 1)

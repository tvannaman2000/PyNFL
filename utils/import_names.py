# v1.0
# src/utils/import_names_csv.py

import sqlite3
import csv

def import_csv_to_names_table(db_path, csv_path, table_name):
    """Import CSV into first_names or last_names table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        
        for row in reader:
            if len(row) >= 2:
                first_name = row[0]
                weight = int(row[1])
                origin = row[2] if len(row) > 2 else None
                
                cursor.execute(f"""
                    INSERT INTO {table_name} (first_name)
                    VALUES (?)
                """, (first_name))
    
    conn.commit()
    conn.close()
    print(f"Imported {cursor.rowcount} rows into {table_name}")

# Usage:
if __name__ == "__main__":
    import_csv_to_names_table("pynfl.db", "firstnames2.csv", "first_names")
    # import_csv_to_names_table("pynfl.db", "surnames2.csv", "last_names")

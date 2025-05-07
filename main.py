#!/usr/bin/env python3
"""
Takamo Galaxy Explorer - Main Entry Point
"""
import tkinter as tk
import os
from app import App

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct absolute path to the database
    db_path = os.path.join(script_dir, "data", "takamo_new.db")
    
    # Ensure the path exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        print("Available files in data directory:")
        data_dir = os.path.join(script_dir, "data")
        if os.path.exists(data_dir):
            print(os.listdir(data_dir))
        else:
            print(f"Data directory {data_dir} does not exist!")
    
    # Check for Wyvern Supremacy directly in the database
    print("\n--- CHECKING FOR WYVERN SUPREMACY PLANETS ---")
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check planets table - note the UPPER case check
        cursor.execute("SELECT location, owner FROM planets WHERE UPPER(owner) LIKE '%WYVERN%'")
        wyvern_planets = cursor.fetchall()
        
        if wyvern_planets:
            print(f"Found {len(wyvern_planets)} Wyvern Supremacy planets:")
            for planet in wyvern_planets:
                print(f"  {planet[0]} - {planet[1]}")
        else:
            print("No Wyvern Supremacy planets found in the database!")
            
            # If no planets found, let's create a test one for debugging
            print("\nCreating a test Wyvern planet for debugging...")
            # Find a random planet to convert
            cursor.execute("SELECT id, location FROM planets LIMIT 1")
            test_planet = cursor.fetchone()
            if test_planet:
                planet_id, location = test_planet
                print(f"Converting planet {location} (ID: {planet_id}) to Wyvern ownership")
                cursor.execute("UPDATE planets SET owner = 'WYVERN SUPREMACY' WHERE id = ?", (planet_id,))
                conn.commit()
                print(f"Test planet created with Wyvern ownership")
            
        conn.close()
    except Exception as e:
        print(f"Error checking for Wyvern planets: {e}")
    print("--- END WYVERN CHECK ---\n")
    
    root = tk.Tk()
    root.title("Takamo Galaxy Explorer")
    root.geometry("1200x800")
    app = App(root, db_path=db_path)
    root.mainloop()
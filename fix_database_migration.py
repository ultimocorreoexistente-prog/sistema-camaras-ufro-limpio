#!/usr/bin/env python3
"""
Database Migration Script - Fix missing latitud/longitud columns
Run this script to fix the Railway deploy issue
"""

import os
import sys
import psycopg2
from datetime import datetime

def create_migration():
    """Add missing columns to ubicaciones table"""
    
    # Get database URL from environment (Railway sets this)
    database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL or POSTGRES_URL not found")
        print("💡 Please set the database URL as environment variable")
        return False
    
    try:
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("📋 Checking current table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'ubicaciones'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        
        print(f"✅ Current columns in ubicaciones: {existing_columns}")
        
        # Check if latitud and longitud columns exist
        if 'latitud' not in existing_columns:
            print("➕ Adding 'latitud' column...")
            cursor.execute("ALTER TABLE ubicaciones ADD COLUMN latitud VARCHAR(255);")
        
        if 'longitud' not in existing_columns:
            print("➕ Adding 'longitud' column...")
            cursor.execute("ALTER TABLE ubicaciones ADD COLUMN longitud VARCHAR(255);")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify changes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = 'ubicaciones' 
            AND column_name IN ('latitud', 'longitud');
        """)
        
        new_columns = cursor.fetchall()
        print(f"✅ New columns added: {[col[0] for col in new_columns]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 UFRO Camera System - Database Migration")
    print("=" * 50)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = create_migration()
    
    if success:
        print("🎉 Migration completed successfully!")
        print("💡 You can now redeploy your Railway application")
    else:
        print("❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

#!/usr/bin/env python3
"""
Complete Database Migration - Add All Missing Columns
This script fixes all missing columns that are causing Railway deployment failures
"""

import os
import psycopg2
from datetime import datetime

def run_complete_migration():
    """Add all missing columns to fix the Railway deploy"""
    
    database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL or POSTGRES_URL not found")
        print("💡 Please set the database URL as environment variable")
        return False
    
    try:
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # List of tables and their missing columns
        migrations = [
            # Ubicacion table (currently has issues)
            ("ubicaciones", ["latitud VARCHAR(255)", "longitud VARCHAR(255)", "activo BOOLEAN DEFAULT true"]),
            
            # Other tables that need activo column based on app.py queries
            ("usuarios", ["activo BOOLEAN DEFAULT true"]),
            ("camaras", ["activo BOOLEAN DEFAULT true", "estado VARCHAR(50) DEFAULT 'inactiva'"]),
            ("switches", ["activo BOOLEAN DEFAULT true", "estado VARCHAR(50) DEFAULT 'inactivo'"]),
            ("nvr", ["activo BOOLEAN DEFAULT true", "estado VARCHAR(50) DEFAULT 'inactivo'"]),
            ("gabinetes", ["activo BOOLEAN DEFAULT true", "estado VARCHAR(50) DEFAULT 'inactivo'"]),
            ("ups", ["activo BOOLEAN DEFAULT true", "estado VARCHAR(50) DEFAULT 'inactivo'"]),
        ]
        
        total_added = 0
        
        for table_name, columns in migrations:
            print(f"\n📋 Processing table: {table_name}")
            
            # Check current table structure
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}';
            """)
            
            existing_columns = [col[0] for col in cursor.fetchall()]
            print(f"   Current columns: {existing_columns[:5]}...")  # Show first 5
            
            # Add missing columns
            for column_def in columns:
                column_name = column_def.split()[0]  # Get column name
                
                if column_name not in existing_columns:
                    try:
                        print(f"   ➕ Adding column: {column_def}")
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def};")
                        total_added += 1
                        print(f"   ✅ Added {column_name} to {table_name}")
                    except Exception as e:
                        if "already exists" in str(e):
                            print(f"   ⚠️ Column {column_name} already exists in {table_name}")
                        else:
                            print(f"   ❌ Error adding {column_name}: {e}")
                            return False
                else:
                    print(f"   ✅ Column {column_name} already exists in {table_name}")
        
        # Commit all changes
        conn.commit()
        print(f"\n🎉 Migration completed successfully!")
        print(f"✅ Total columns added: {total_added}")
        
        # Verify critical tables have required columns
        print(f"\n🔍 Verifying critical fixes...")
        
        critical_checks = [
            ("ubicaciones", ["latitud", "longitud", "activo"]),
            ("usuarios", ["activo"]),
            ("camaras", ["activo", "estado"]),
            ("switches", ["activo"]),
        ]
        
        for table_name, required_columns in critical_checks:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}';
            """)
            
            table_columns = [col[0] for col in cursor.fetchall()]
            missing = [col for col in required_columns if col not in table_columns]
            
            if not missing:
                print(f"   ✅ {table_name}: All required columns present")
            else:
                print(f"   ❌ {table_name}: Missing columns: {missing}")
                return False
        
        print(f"\n🚀 All critical tables are now properly configured!")
        print(f"💡 Your Railway application should now deploy successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ MIGRATION FAILED: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 UFRO Camera System - Complete Database Migration")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = run_complete_migration()
    
    if success:
        print("\n🎉 SUCCESS! Database migration completed!")
        print("\n📋 Next steps:")
        print("1. Redeploy your Railway application")
        print("2. Check deploy logs for success")
        print("3. Test your application at the Railway URL")
        print("\n🌟 Your UFRO Camera System should now work perfectly!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        print("💡 If you continue having issues, consider resetting the database.")
        exit(1)

"""COMPLETE AUTOMATED FIX - RUN THIS FIRST"""

import os
import shutil
import sys

def fix_project_structure():
    """Fix the entire project structure automatically."""
    
    # Find where we are
    current = os.getcwd()
    print(f"Current directory: {current}")
    
    # Navigate to project root
    if current.endswith('data\\src'):
        project_root = os.path.dirname(os.path.dirname(current))
    elif current.endswith('src'):
        project_root = os.path.dirname(current)
    elif current.endswith('data'):
        project_root = os.path.dirname(current)
    else:
        project_root = current
    
    print(f"Project root set to: {project_root}")
    os.chdir(project_root)
    
    # Step 1: Fix nested data folder
    nested_data = os.path.join(project_root, 'data', 'data')
    if os.path.exists(nested_data):
        print("📁 Fixing nested data folder...")
        for file in os.listdir(nested_data):
            if file.endswith('.csv'):
                src = os.path.join(nested_data, file)
                dst = os.path.join(project_root, 'data', file)
                shutil.move(src, dst)
                print(f"  ✓ Moved {file}")
        os.rmdir(nested_data)
        print("  ✓ Removed nested folder")
    
    # Step 2: Move src if it's in wrong place
    wrong_src = os.path.join(project_root, 'data', 'src')
    correct_src = os.path.join(project_root, 'src')
    
    if os.path.exists(wrong_src) and not os.path.exists(correct_src):
        print("📁 Moving src to correct location...")
        shutil.move(wrong_src, correct_src)
        print("  ✓ Moved src folder")
    
    # Step 3: Move main.py to root if it's in src
    main_in_src = os.path.join(project_root, 'src', 'main.py')
    main_in_root = os.path.join(project_root, 'main.py')
    
    if os.path.exists(main_in_src) and not os.path.exists(main_in_root):
        print("📁 Moving main.py to project root...")
        shutil.move(main_in_src, main_in_root)
        print("  ✓ Moved main.py")
    
    # Step 4: Create sample data if missing
    sample_data = os.path.join(project_root, 'data', 'sample_interactions.csv')
    if not os.path.exists(sample_data):
        print("📁 Creating sample data...")
        os.makedirs(os.path.join(project_root, 'data'), exist_ok=True)
        
        sample_content = """post_id,user_id,timestamp,action_type
organic_post_001,user_001,2025-01-15 08:12:03,like
organic_post_001,user_002,2025-01-15 08:15:22,share
organic_post_001,user_003,2025-01-15 08:18:45,comment
organic_post_001,user_004,2025-01-15 08:22:10,like
organic_post_001,user_005,2025-01-15 08:25:33,repost
organic_post_001,user_006,2025-01-15 08:31:17,like
organic_post_001,user_007,2025-01-15 08:36:42,comment
organic_post_001,user_008,2025-01-15 08:42:01,share
organic_post_001,user_009,2025-01-15 08:48:29,like
organic_post_001,user_010,2025-01-15 08:55:14,repost
organic_post_001,user_011,2025-01-15 09:03:07,comment
organic_post_001,user_012,2025-01-15 09:11:23,like
organic_post_001,user_013,2025-01-15 09:20:45,share
organic_post_001,user_014,2025-01-15 09:31:02,like
organic_post_001,user_015,2025-01-15 09:42:18,repost
organic_post_001,user_016,2025-01-15 09:54:36,comment
organic_post_001,user_017,2025-01-15 10:07:59,like
organic_post_001,user_018,2025-01-15 10:22:24,share
organic_post_001,user_019,2025-01-15 10:38:03,like
organic_post_001,user_020,2025-01-15 10:55:47,repost
coordinated_post_002,user_101,2025-01-15 12:00:01,share
coordinated_post_002,user_102,2025-01-15 12:00:02,share
coordinated_post_002,user_103,2025-01-15 12:00:03,like
coordinated_post_002,user_104,2025-01-15 12:00:03,repost
coordinated_post_002,user_105,2025-01-15 12:00:04,comment
coordinated_post_002,user_106,2025-01-15 12:00:04,like
coordinated_post_002,user_107,2025-01-15 12:00:05,share
coordinated_post_002,user_108,2025-01-15 12:00:05,repost
coordinated_post_002,user_109,2025-01-15 12:00:06,like
coordinated_post_002,user_110,2025-01-15 12:00:06,comment
coordinated_post_002,user_101,2025-01-15 12:00:07,like
coordinated_post_002,user_102,2025-01-15 12:00:07,repost
coordinated_post_002,user_103,2025-01-15 12:00:08,share
coordinated_post_002,user_104,2025-01-15 12:00:08,like
coordinated_post_002,user_105,2025-01-15 12:00:09,comment
coordinated_post_002,user_106,2025-01-15 12:00:09,share
coordinated_post_002,user_107,2025-01-15 12:00:10,repost
coordinated_post_002,user_108,2025-01-15 12:00:10,like
coordinated_post_002,user_109,2025-01-15 12:00:11,share
coordinated_post_002,user_110,2025-01-15 12:00:11,comment"""
        
        with open(sample_data, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print("  ✓ Created sample_interactions.csv")
    
    # Step 5: Verify structure
    print("\n" + "="*60)
    print("✅ FINAL PROJECT STRUCTURE:")
    print("="*60)
    
    required_files = [
        ('main.py', 'root'),
        ('data/sample_interactions.csv', 'data'),
        ('src/__init__.py', 'src'),
        ('src/loader.py', 'src'),
        ('src/features.py', 'src'),
        ('src/entropy.py', 'src'),
        ('src/graph_analysis.py', 'src'),
        ('src/detector.py', 'src'),
        ('src/utils.py', 'src'),
    ]
    
    all_good = True
    for file_path, location in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_good = False
    
    if all_good:
        print("\n" + "="*60)
        print("✅ PROJECT STRUCTURE IS CORRECT!")
        print("="*60)
        print(f"\n📍 Project root: {project_root}")
        print("\n▶️  RUN THIS COMMAND:")
        print(f'   cd "{project_root}"')
        print('   python main.py')
    else:
        print("\n⚠️  Some files are missing. Please ensure all Python files are in the src folder.")
    
    return project_root

if __name__ == "__main__":
    print("\n🔧 INSTAGRAM NATIVE AI LABELER - PROJECT FIX UTILITY")
    print("="*60)
    root = fix_project_structure()
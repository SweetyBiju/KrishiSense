import os
import shutil

# ================= CONFIGURATION =================
LEGACY_DIR = "legacy_v1"
# Files to strictly PROTECT (Don't move these)
EXCLUDE_FILES = [
    ".git", 
    ".gitignore", 
    "requirements.txt", 
    "README.md", 
    "node_modules", 
    "venv", 
    "clean_sweep.py", # Don't move the broom while sweeping!
    LEGACY_DIR
]

# The New Structure we want to build
NEW_STRUCTURE = [
    "src/data_ingestion",
    "src/preprocessing",
    "src/modeling",
    "data/raw",
    "data/processed",
    "data/models",
    "notebooks",
    "docs"
]

def run_clean_sweep():
    print("🧹 Starting Clean Sweep...")
    
    # 1. Create Legacy Directory
    if not os.path.exists(LEGACY_DIR):
        os.makedirs(LEGACY_DIR)

    # 2. Move EVERYTHING (except protected) to Legacy
    for item in os.listdir("."):
        if item not in EXCLUDE_FILES:
            try:
                src_path = item
                dst_path = os.path.join(LEGACY_DIR, item)
                shutil.move(src_path, dst_path)
                print(f"📦 Archived to legacy: {item}")
            except Exception as e:
                print(f"⚠️ Skipped {item}: {e}")

    # 3. Create New V2 Structure
    print("\n🏗️ Building New V2 Architecture...")
    for folder in NEW_STRUCTURE:
        os.makedirs(folder, exist_ok=True)
        # Create empty __init__.py for Python packages
        if "src/" in folder:
            open(os.path.join(folder, "__init__.py"), 'a').close()
            
    print("\n✅ DONE! Project is clean.")
    print("👉 Next Step: Drag your 5 crop .xls files into 'data/raw/'")

if __name__ == "__main__":
    confirm = input("This will move ALL current files to legacy_v1. Proceed? (yes/no): ")
    if confirm.lower() == "yes":
        run_clean_sweep()
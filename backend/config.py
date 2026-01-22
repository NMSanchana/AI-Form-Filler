import os

PORT = 8000
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"  # Keep this for PDF generation only
SAMPLE_FORMS_DIR = "sample-forms"

# Only create directories that are actually needed
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/documents", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/forms", exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)  # For PDF outputs only
os.makedirs(SAMPLE_FORMS_DIR, exist_ok=True)

# You can manually delete outputs folder contents anytime
# Or add this function to clean it automatically:

def clean_outputs():
    """Clean old output files"""
    import glob
    import time
    
    # Delete files older than 1 hour
    cutoff_time = time.time() - 3600
    
    for filepath in glob.glob(os.path.join(OUTPUT_DIR, "*")):
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    print(f"🗑️ Deleted old file: {filepath}")
                except:
                    pass

# Call this in main.py startup if you want auto-cleanup
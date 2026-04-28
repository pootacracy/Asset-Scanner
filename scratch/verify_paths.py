from pathlib import Path
import platform
import os

# Copy of the normalize_path function for verification
def normalize_path(path_str) -> Path:
    if not path_str:
        return Path()
    
    path_s = str(path_str).strip()
    current_os = platform.system()
    
    # Mapping for z:\ drive which seems to be /Volumes/media on this system
    z_drive_linux = "/Volumes/media"
    
    if current_os != "Windows":
        # Convert Windows to Linux/macOS
        if len(path_s) >= 2 and path_s[1] == ":" and path_s[0].lower() == 'z':
            path_s = z_drive_linux + path_s[2:]
        
        path_s = path_s.replace("\\", "/")
        while "//" in path_s:
            path_s = path_s.replace("//", "/")
    else:
        if path_s.lower().startswith(z_drive_linux.lower()):
            path_s = "z:" + path_s[len(z_drive_linux):]
        
        path_s = path_s.replace("/", "\\")
        while "\\\\" in path_s:
            path_s = path_s.replace("\\\\", "\\")
            
    return Path(path_s)

# Test cases
test_paths = [
    r"z:\Models\Printable Library\AssetSorted\2Moronic\Images",
    r"Z:/Models/Printable Library/AssetSorted/2Moronic",
    "/Volumes/media/Models/Printable Library",
    "relative/path/to/image.jpg"
]

print(f"Current OS: {platform.system()}")
for p in test_paths:
    normalized = normalize_path(p)
    print(f"Original: {p}")
    print(f"Normalized: {normalized}")
    print(f"Exists: {normalized.exists()}")
    print("-" * 20)

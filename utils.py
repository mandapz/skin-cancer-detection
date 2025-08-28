import os
import shutil
import datetime
from PIL import Image
import streamlit as st

def setup_directories():
    """
    Setup direktori yang diperlukan aplikasi
    """
    directories = [
        "temp",
        "uploads", 
        "history_images",
        "models"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Direktori '{directory}' berhasil dibuat")

def validate_image(uploaded_file):
    """
    Validasi file gambar yang diupload
    Args:
        uploaded_file: File yang diupload melalui Streamlit
    Returns:
        bool: True jika valid, False jika tidak
    """
    if uploaded_file is None:
        return False, "Tidak ada file yang diupload"
    
    # Cek ekstensi file
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"Format file tidak didukung. Gunakan: {', '.join(allowed_extensions)}"
    
    # Cek ukuran file (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if uploaded_file.size > max_size:
        return False, "Ukuran file terlalu besar. Maksimal 10MB"
    
    # Cek apakah file benar-benar gambar
    try:
        image = Image.open(uploaded_file)
        image.verify()  # Verifikasi integritas gambar
        return True, "Valid"
    except Exception:
        return False, "File bukan gambar yang valid"

def save_uploaded_file(uploaded_file, save_directory="uploads"):
    """
    Simpan file yang diupload
    Args:
        uploaded_file: File yang diupload
        save_directory: Direktori tujuan
    Returns:
        str: Path file yang disimpan
    """
    try:
        # Buat nama file unik dengan timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(save_directory, filename)
        
        # Simpan file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    except Exception as e:
        raise Exception(f"Error menyimpan file: {str(e)}")

def resize_image(image_path, max_width=800, max_height=600):
    """
    Resize gambar untuk optimasi tampilan
    Args:
        image_path: Path ke file gambar
        max_width: Lebar maksimal
        max_height: Tinggi maksimal
    Returns:
        PIL.Image: Gambar yang sudah diresize
    """
    try:
        image = Image.open(image_path)
        
        # Hitung ratio resize
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        ratio = min(width_ratio, height_ratio, 1)  # Tidak memperbesar gambar
        
        if ratio < 1:
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    except Exception as e:
        raise Exception(f"Error resize gambar: {str(e)}")

def cleanup_temp_files(temp_directory="temp", max_age_hours=24):
    """
    Bersihkan file temporary yang sudah lama
    Args:
        temp_directory: Direktori temporary
        max_age_hours: Usia maksimal file dalam jam
    """
    try:
        if not os.path.exists(temp_directory):
            return
        
        current_time = datetime.datetime.now()
        max_age = datetime.timedelta(hours=max_age_hours)
        
        for filename in os.listdir(temp_directory):
            filepath = os.path.join(temp_directory, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath))
                if current_time - file_time > max_age:
                    os.remove(filepath)
                    print(f"File temporary dihapus: {filename}")
    
    except Exception as e:
        print(f"Error cleanup temp files: {e}")

def format_file_size(size_bytes):
    """
    Format ukuran file ke format yang mudah dibaca
    Args:
        size_bytes: Ukuran dalam bytes
    Returns:
        str: Ukuran yang sudah diformat
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_image_info(image_path):
    """
    Mendapatkan informasi gambar
    Args:
        image_path: Path ke file gambar
    Returns:
        dict: Informasi gambar
    """
    try:
        image = Image.open(image_path)
        file_size = os.path.getsize(image_path)
        
        info = {
            "filename": os.path.basename(image_path),
            "format": image.format,
            "mode": image.mode,
            "size": f"{image.width} x {image.height}",
            "file_size": format_file_size(file_size)
        }
        
        return info
    except Exception as e:
        return {"error": f"Error mendapatkan info gambar: {str(e)}"}

def create_thumbnail(image_path, thumbnail_size=(150, 150)):
    """
    Membuat thumbnail dari gambar
    Args:
        image_path: Path ke file gambar
        thumbnail_size: Ukuran thumbnail (width, height)
    Returns:
        PIL.Image: Thumbnail gambar
    """
    try:
        image = Image.open(image_path)
        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        raise Exception(f"Error membuat thumbnail: {str(e)}")

def validate_model_file(model_path="best.pt"):
    """
    Validasi file model YOLO
    Args:
        model_path: Path ke file model
    Returns:
        tuple: (bool, str) - (status valid, pesan)
    """
    if not os.path.exists(model_path):
        return False, f"File model tidak ditemukan: {model_path}"
    
    # Cek ekstensi file
    if not model_path.endswith('.pt'):
        return False, "File model harus berekstensi .pt"
    
    # Cek ukuran file (model YOLO biasanya > 1MB)
    file_size = os.path.getsize(model_path)
    if file_size < 1024 * 1024:  # < 1MB
        return False, "File model terlalu kecil, kemungkinan rusak"
    
    return True, "File model valid"

def log_activity(username, activity, details=""):
    """
    Log aktivitas user (opsional untuk debugging)
    Args:
        username: Username yang melakukan aktivitas
        activity: Jenis aktivitas
        details: Detail tambahan
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {username}: {activity}"
        if details:
            log_entry += f" - {details}"
        
        # Simpan ke file log (opsional)
        with open("app_activity.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    except Exception as e:
        print(f"Error logging: {e}")

def check_system_requirements():
    """
    Cek requirement sistem
    Returns:
        dict: Status requirement
    """
    requirements = {
        "python_version": True,
        "opencv": False,
        "ultralytics": False,
        "pillow": True,
        "streamlit": True
    }
    
    try:
        import cv2
        requirements["opencv"] = True
    except ImportError:
        pass
    
    try:
        from ultralytics import YOLO
        requirements["ultralytics"] = True
    except ImportError:
        pass
    
    return requirements

@st.cache_data
def get_sample_images_info():
    """
    Informasi tentang gambar contoh (jika ada)
    """
    sample_info = {
        "melanoma": "Contoh gambar melanoma dengan karakteristik ABCDE",
        "benign": "Contoh gambar lesi jinak",
        "suspicious": "Contoh gambar yang perlu diperiksa lebih lanjut"
    }
    return sample_info
import hashlib
import datetime
from database import DatabaseManager

class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def hash_password(self, password):
        """Hash password menggunakan SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, nama_lengkap, username, password):
        """
        Register user baru
        Returns: True jika berhasil, False jika username sudah ada
        """
        try:
            # Cek apakah username sudah ada
            if self.db_manager.user_exists(username):
                return False
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Simpan user baru
            return self.db_manager.create_user(nama_lengkap, username, hashed_password)
        
        except Exception as e:
            print(f"Error saat registrasi: {e}")
            return False
    
    def login(self, username, password):
        """
        Login user
        Returns: True jika berhasil, False jika gagal
        """
        try:
            # Hash password yang diinput
            hashed_password = self.hash_password(password)
            
            # Verifikasi dengan database
            return self.db_manager.verify_user(username, hashed_password)
        
        except Exception as e:
            print(f"Error saat login: {e}")
            return False
    
    def reset_password(self, username, new_password):
        """
        Reset password user
        Returns: True jika berhasil, False jika username tidak ada
        """
        try:
            # Cek apakah user ada
            if not self.db_manager.user_exists(username):
                return False
            
            # Hash password baru
            hashed_password = self.hash_password(new_password)
            
            # Update password
            return self.db_manager.update_password(username, hashed_password)
        
        except Exception as e:
            print(f"Error saat reset password: {e}")
            return False
    
    def get_user_info(self, username):
        """
        Mendapatkan informasi user
        Returns: Dictionary dengan info user atau None
        """
        try:
            return self.db_manager.get_user_info(username)
        except Exception as e:
            print(f"Error saat mengambil info user: {e}")
            return None
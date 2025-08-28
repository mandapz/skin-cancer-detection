import sqlite3
import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="skin_cancer_app.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inisialisasi database dan tabel"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabel users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_lengkap TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    tanggal_dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel detection_history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detection_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    tanggal_deteksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hasil_deteksi TEXT,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database berhasil diinisialisasi")
            
        except Exception as e:
            print(f"Error saat inisialisasi database: {e}")
    
    def create_user(self, nama_lengkap, username, hashed_password):
        """Membuat user baru"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (nama_lengkap, username, password)
                VALUES (?, ?, ?)
            ''', (nama_lengkap, username, hashed_password))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error saat membuat user: {e}")
            return False
    
    def user_exists(self, username):
        """Cek apakah username sudah ada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
            
        except Exception as e:
            print(f"Error saat cek user: {e}")
            return False
    
    def verify_user(self, username, hashed_password):
        """Verifikasi login user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"Error saat verifikasi user: {e}")
            return False
    
    def update_password(self, username, new_hashed_password):
        """Update password user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET password = ? WHERE username = ?
            ''', (new_hashed_password, username))
            
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error saat update password: {e}")
            return False
    
    def get_user_info(self, username):
        """Mendapatkan informasi user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nama_lengkap, username, password, tanggal_dibuat
                FROM users WHERE username = ?
            ''', (username,))
            
            user_info = cursor.fetchone()
            conn.close()
            
            return user_info
            
        except Exception as e:
            print(f"Error saat mengambil info user: {e}")
            return None
    
    def save_detection_history(self, username, filename, filepath, hasil_deteksi):
        """Simpan history deteksi"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO detection_history (username, filename, filepath, hasil_deteksi)
                VALUES (?, ?, ?, ?)
            ''', (username, filename, filepath, hasil_deteksi))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saat menyimpan history: {e}")
            return False
    
    def get_detection_history(self, username):
        """Mendapatkan history deteksi user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, filename, filepath, tanggal_deteksi, hasil_deteksi
                FROM detection_history 
                WHERE username = ?
                ORDER BY tanggal_deteksi DESC
            ''', (username,))
            
            history = cursor.fetchall()
            conn.close()
            
            return history
            
        except Exception as e:
            print(f"Error saat mengambil history: {e}")
            return []
    
    def delete_detection_history(self, history_id):
        """Hapus satu history deteksi berdasar id dan hapus file gambarnya"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ambil path gambar sebelum hapus
            cursor.execute('SELECT filepath FROM detection_history WHERE id = ?', (history_id,))
            row = cursor.fetchone()
            if row and os.path.exists(row[0]):
                os.remove(row[0])

            # Hapus record
            cursor.execute('DELETE FROM detection_history WHERE id = ?', (history_id,))
            conn.commit()
            deleted = cursor.rowcount
            conn.close()
            return deleted > 0
        except Exception as e:
            print(f"Error saat menghapus history: {e}")
            return False

    def delete_old_detections(self, days=30):
        """Hapus deteksi lama (opsional untuk maintenance)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Hapus file gambar terlebih dahulu
            cursor.execute('''
                SELECT filepath FROM detection_history 
                WHERE tanggal_deteksi < ?
            ''', (cutoff_date,))
            
            old_files = cursor.fetchall()
            for file_path in old_files:
                if os.path.exists(file_path[0]):
                    os.remove(file_path[0])
            
            # Hapus record dari database
            cursor.execute('''
                DELETE FROM detection_history 
                WHERE tanggal_deteksi < ?
            ''', (cutoff_date,))
            
            conn.commit()
            deleted_count = cursor.rowcount
            conn.close()
            
            print(f"Dihapus {deleted_count} record lama")
            return True
            
        except Exception as e:
            print(f"Error saat menghapus data lama: {e}")
            return False
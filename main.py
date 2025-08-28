import streamlit as st
import os
from auth import AuthManager
from detection import SkinCancerDetector
from database import DatabaseManager
from utils import setup_directories
from PIL import Image
import datetime
import pytz

# Setup halaman Streamlit
st.set_page_config(
    page_title="Deteksi Kanker Kulit",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup direktori
setup_directories()

# Inisialisasi managers
@st.cache_resource
def init_managers():
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    detector = SkinCancerDetector()
    return db_manager, auth_manager, detector

db_manager, auth_manager, detector = init_managers()

# Dictionary untuk menjelaskan jenis kanker kulit
SKIN_CANCER_TYPES = {
    'akiec': {
        'full_name': 'Actinic Keratoses and Intraepithelial Carcinoma',
        'description': 'Lesi prakanker yang dapat berkembang menjadi karsinoma sel skuamosa jika tidak ditangani.'
    },
    'bcc': {
        'full_name': 'Basal Cell Carcinoma',
        'description': 'Jenis kanker kulit paling umum, berasal dari sel basal di lapisan epidermis.'
    },
    'bkl': {
        'full_name': 'Benign Keratosis-like Lesions',
        'description': 'Lesi kulit jinak yang mirip dengan kanker, namun tidak berpotensi menjadi kanker.'
    },
    'df': {
        'full_name': 'Dermatofibroma',
        'description': 'Tumor jinak yang biasanya muncul sebagai benjolan kecil di kulit.'
    },
    'mel': {
        'full_name': 'Melanoma',
        'description': 'Jenis kanker kulit paling serius yang berasal dari sel pigmen (melanosit).'
    },
    'nv': {
        'full_name': 'Melanocytic Nevi',
        'description': 'Tahi lalat biasa yang biasanya tidak berbahaya.'
    },
    'vasc': {
        'full_name': 'Vascular Lesions',
        'description': 'Lesi yang melibatkan pembuluh darah, seperti hemangioma atau telangiektasia.'
    }
}

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 20px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 20px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 20px 0;
    }
    .cancer-type-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1976d2;
        margin: 10px 0;
    }
    .education-link {
        display: inline-block;
        background-color: #2E86AB;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
        text-decoration: none;
        margin-top: 10px;
        font-weight: bold;
    }
    .education-link:hover {
        background-color: #1e5f7a;
        color: white;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "🔍 Deteksi"

    # Header aplikasi
    st.markdown('<h1 class="main-header">🔬 SkinGuard - Aplikasi Deteksi Kanker Kulit</h1>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ DISCLAIMER PENTING:</strong><br>
        Aplikasi ini hanya untuk tujuan deteksi awal dan edukasi. Hasil deteksi tidak dapat menggantikan 
        diagnosis medis profesional. Untuk diagnosis yang akurat dan pengobatan yang tepat, 
        silakan konsultasikan dengan dokter spesialis kulit atau tenaga medis profesional.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        show_auth_pages()
    else:
        show_main_app()

def show_auth_pages():
    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔑 Login", "📝 Register", "🔄 Reset Password"])
    
    with auth_tab1:
        show_login_page()
    
    with auth_tab2:
        show_register_page()
    
    with auth_tab3:
        show_reset_password_page()

def show_login_page():
    st.subheader("🔑 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                if auth_manager.login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login berhasil!")
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")
            else:
                st.error("❌ Mohon isi semua field!")

def show_register_page():
    st.subheader("📝 Register Akun Baru")
    
    with st.form("register_form"):
        nama_lengkap = st.text_input("Nama Lengkap")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if nama_lengkap and username and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ Password tidak cocok!")
                elif len(password) < 6:
                    st.error("❌ Password minimal 6 karakter!")
                elif auth_manager.register(nama_lengkap, username, password):
                    st.success("✅ Registrasi berhasil! Silakan login.")
                else:
                    st.error("❌ Username sudah digunakan!")
            else:
                st.error("❌ Mohon isi semua field!")

def show_reset_password_page():
    st.subheader("🔄 Reset Password")
    
    with st.form("reset_password_form"):
        username = st.text_input("Username")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
        submit_button = st.form_submit_button("Reset Password")
        
        if submit_button:
            if username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("❌ Password tidak cocok!")
                elif len(new_password) < 6:
                    st.error("❌ Password minimal 6 karakter!")
                elif auth_manager.reset_password(username, new_password):
                    st.success("✅ Password berhasil direset! Silakan login dengan password baru.")
                else:
                    st.error("❌ Username tidak ditemukan!")
            else:
                st.error("❌ Mohon isi semua field!")

def show_main_app():
    # Sidebar navigation
    with st.sidebar:
        st.write(f"👋 Selamat datang, **{st.session_state.username}**!")
        
        menu_options = ["🔍 Deteksi", "📈 Riwayat", "👤 Info Akun", "📚 Edukasi", "🚪 Logout"]
        selected = st.selectbox("Pilih Menu:", menu_options, index=menu_options.index(st.session_state.selected_menu) if st.session_state.selected_menu in menu_options else 0)
        
        if selected != st.session_state.selected_menu:
            st.session_state.selected_menu = selected
            st.rerun()
        
        if selected == "🚪 Logout":
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.selected_menu = "🔍 Deteksi"
            st.rerun()
    
    # Main content
    if st.session_state.selected_menu == "🔍 Deteksi":
        show_detection_page()
    elif st.session_state.selected_menu == "📈 Riwayat":
        show_history_page()
    elif st.session_state.selected_menu == "👤 Info Akun":
        show_account_info_page()
    elif st.session_state.selected_menu == "📚 Edukasi":
        show_education_page()

def get_cancer_type_info(class_name):
    """Mendapatkan informasi lengkap tentang jenis kanker kulit"""
    # Konversi ke lowercase untuk mencocokkan key dictionary
    class_key = class_name.lower().strip()
    
    if class_key in SKIN_CANCER_TYPES:
        return SKIN_CANCER_TYPES[class_key]
    else:
        # Fallback jika jenis tidak ditemukan
        return {
            'full_name': class_name.upper(),
            'description': 'Jenis lesi kulit yang memerlukan evaluasi lebih lanjut oleh dokter spesialis.'
        }

def show_detection_page():
    st.header("🔍 Deteksi Kanker Kulit")

    # Pilih metode input
    input_method = st.radio("Pilih metode input gambar:", ["📁 Upload Gambar", "📸 Kamera Langsung"])

    uploaded_file = None
    image_source = None

    if input_method == "📁 Upload Gambar":
        uploaded_file = st.file_uploader("Pilih gambar kulit untuk dianalisis", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            image_source = Image.open(uploaded_file)
    else:
        camera_image = st.camera_input("Ambil gambar menggunakan webcam")
        if camera_image:
            image_source = Image.open(camera_image)
            uploaded_file = camera_image
            uploaded_file.name = f"webcam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    if image_source:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 Gambar Asli")
            st.image(image_source, caption="Gambar yang dimasukkan", use_container_width=True)

        if st.button("🔬 Mulai Deteksi", type="primary"):
            with st.spinner("Sedang menganalisis gambar..."):
                try:
                    temp_path = f"temp/{uploaded_file.name}"
                    os.makedirs("temp", exist_ok=True)
                    image_source.save(temp_path)  # Simpan gambar

                    # Deteksi
                    result_image, predictions = detector.detect(temp_path)

                    # Simpan ke riwayat
                    db_manager.save_detection_history(
                        st.session_state.username,
                        uploaded_file.name,
                        temp_path,
                        str(predictions)
                    )

                    with col2:
                        st.subheader("🎯 Hasil Deteksi")
                        st.image(result_image, caption="Hasil deteksi", use_container_width=True)

                    st.subheader("📊 Hasil Analisis Detail")
                    if predictions:
                        for i, pred in enumerate(predictions):
                            confidence = pred['confidence'] * 100
                            class_name = pred['class']
                            
                            # Dapatkan informasi lengkap tentang jenis kanker
                            cancer_info = get_cancer_type_info(class_name)
                            
                            if confidence > 50:
                                st.markdown(f"""
                                    <div class="warning-box">
                                        <strong>🔍 Deteksi {i+1}:</strong><br>
                                        <strong>Jenis:</strong> {class_name.upper()} ({cancer_info['full_name']})<br>
                                        <strong>Deskripsi:</strong> {cancer_info['description']}<br>
                                        <strong>Tingkat Keyakinan:</strong> {confidence:.2f}%<br>
                                        <em>⚠️ Tingkat keyakinan tinggi - Sangat disarankan untuk konsultasi dengan dokter spesialis kulit segera!</em>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="info-box">
                                        <strong>🔍 Deteksi {i+1}:</strong><br>
                                        <strong>Jenis:</strong> {class_name.upper()} ({cancer_info['full_name']})<br>
                                        <strong>Deskripsi:</strong> {cancer_info['description']}<br>
                                        <strong>Tingkat Keyakinan:</strong> {confidence:.2f}%<br>
                                        <em>ℹ️ Tingkat keyakinan rendah, namun tetap disarankan pemeriksaan rutin dengan dokter.</em>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                    else:
                        st.markdown("""
                            <div class="success-box">
                                <strong>✅ Hasil Deteksi:</strong><br>
                                Tidak ada deteksi kanker kulit yang signifikan ditemukan pada gambar ini.<br>
                                <em>Namun, tetap disarankan untuk melakukan pemeriksaan rutin dengan dokter spesialis kulit.</em>
                            </div>
                        """, unsafe_allow_html=True)

                    st.success("✅ Deteksi selesai dan disimpan ke Riwayat!")

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan saat deteksi: {str(e)}")

def show_history_page():
    st.header("📈 Riwayat Deteksi")
    
    from datetime import datetime as dt
    local_tz = pytz.timezone("Asia/Jakarta")

    if "delete_history_id" not in st.session_state:
        st.session_state.delete_history_id = None

    history = db_manager.get_detection_history(st.session_state.username)
    
    if history:
        for record in history:
            try:
                utc_dt = dt.strptime(record[4], "%Y-%m-%d %H:%M:%S")
                utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
                local_dt = utc_dt.astimezone(local_tz)
                waktu_str = local_dt.strftime("%d-%m-%Y %H:%M:%S WIB")
            except Exception:
                waktu_str = record[4]
            
            with st.expander(f"📅 {waktu_str} - {record[2]}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    if os.path.exists(record[3]):
                        st.image(record[3], caption="Gambar yang dideteksi", width=300)
                    else:
                        st.write("🖼️ Gambar tidak tersedia")
                    
                    # Tombol hapus
                    if st.button("🗑️ Hapus Riwayat Ini", key=f"delete_{record[0]}"):
                        st.session_state.delete_history_id = record[0]
                        st.rerun()
                
                with col2:
                    st.write("**📊 Hasil Deteksi Detail:**")
                    try:
                        predictions = eval(record[5]) if record[5] != 'None' else []
                        if predictions:
                            for i, pred in enumerate(predictions):
                                cancer_info = get_cancer_type_info(pred['class'])
                                confidence = pred['confidence'] * 100
                                
                                st.markdown(f"""
                                    <div class="cancer-type-box">
                                        <strong>{pred['class'].upper()}</strong><br>
                                        <small>{cancer_info['full_name']}</small><br>
                                        <strong>Keyakinan:</strong> {confidence:.2f}%
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.write("✅ Tidak ada deteksi kanker kulit")
                    except:
                        st.write("❌ Data tidak valid")
        
        # Handle penghapusan riwayat
        if st.session_state.delete_history_id:
            deleted = db_manager.delete_detection_history(st.session_state.delete_history_id)
            if deleted:
                st.success("✅ Riwayat berhasil dihapus!")
            else:
                st.error("❌ Gagal menghapus riwayat.")
            st.session_state.delete_history_id = None
            st.rerun()
    else:
        st.info("📝 Belum ada riwayat deteksi. Silakan lakukan deteksi terlebih dahulu.")

def show_account_info_page():
    st.header("👤 Informasi Akun")
    
    user_info = db_manager.get_user_info(st.session_state.username)
    
    if user_info:
        st.markdown(f"""
        <div class="info-box">
            <strong>📋 Detail Akun:</strong><br>
            <strong>Nama Lengkap:</strong> {user_info[1]}<br>
            <strong>Username:</strong> {user_info[2]}<br>
            <strong>Tanggal Pembuatan Akun:</strong> {user_info[4]}<br>
        </div>
        """, unsafe_allow_html=True)
        
        history_count = len(db_manager.get_detection_history(st.session_state.username))
        st.markdown(f"""
        <div class="success-box">
            <strong>📊 Statistik Penggunaan:</strong><br>
            Total Deteksi: {history_count} kali
        </div>
        """, unsafe_allow_html=True)

def show_education_page():
    st.header("📚 Edukasi Kanker Kulit")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Apa itu Kanker Kulit?", "⚠️ Gejala & Tanda", "🛡️ Pencegahan", "🏥 Kapan ke Dokter?"])
    
    with tab1:
        st.markdown("""
        ### 🔍 Apa itu Kanker Kulit?
        
        Kanker kulit adalah pertumbuhan sel-sel kulit yang tidak normal, dan umumnya terjadi pada area kulit yang sering terpapar sinar matahari.
        Memahami berbagai jenis kanker kulit sangat penting untuk mendukung deteksi dini dan penanganan yang tepat. 
        Berikut ini adalah tujuh jenis utama kanker kulit beserta penjelasannya:
                    
        **1. AKIEC (Actinic Keratoses and Intraepithelial Carcinoma)**
        - **Definisi:** Lesi prakanker yang dapat berkembang menjadi karsinoma sel skuamosa jika tidak ditangani.
        - **Ciri-ciri:** Bercak kasar, bersisik, berwarna kemerahan atau kecoklatan, sering ditemukan di area yang sering terkena matahari.
        - **Risiko:** Dapat berkembang menjadi kanker kulit invasif.
        
        **2. BCC (Basal Cell Carcinoma)**
        - **Definisi:** Jenis kanker kulit paling umum, berasal dari sel basal di lapisan epidermis.
        - **Ciri-ciri:** Benjolan kecil berwarna daging atau merah muda, bisa juga berupa bercak bersisik.
        - **Risiko:** Jarang menyebar ke bagian tubuh lain, namun dapat merusak jaringan di sekitarnya jika tidak diobati.
                
        **3. BKL (Benign Keratosis-like Lesions)**
        - **Definisi:** Lesi kulit jinak yang mirip dengan kanker, namun tidak berpotensi menjadi kanker.
        - **Ciri-ciri:** Bercak berwarna coklat atau hitam, biasanya tidak berubah bentuk atau ukuran.
        - **Risiko:** Tidak berbahaya, namun perlu dipantau untuk memastikan tidak berubah menjadi kanker.
        
        **4. DF (Dermatofibroma)**
        - **Definisi:** Tumor jinak yang biasanya muncul sebagai benjolan kecil di kulit.
        - **Ciri-ciri:** Benjolan keras, berwarna coklat atau merah muda, sering ditemukan di kaki atau lengan.
        - **Risiko:** Tidak berbahaya, namun bisa mengganggu penampilan.
                    
        **5. MEL (Melanoma)**
        - **Definisi:** Jenis kanker kulit paling serius yang berasal dari sel pigmen (melanosit).
        - **Ciri-ciri:** Tahi lalat atau bercak baru yang berubah bentuk, ukuran, atau warna; bisa juga berupa luka yang tidak sembuh.
        - **Risiko:** Dapat menyebar ke bagian tubuh lain jika tidak dideteksi dan diobati dini.
                    
        **6. NV (Melanocytic Nevi)**
        - **Definisi:** Tahi lalat biasa yang biasanya tidak berbahaya.
        - **Ciri-ciri:** Bercak berwarna coklat atau hitam, biasanya bulat atau oval, dan tidak berubah bentuk.
        - **Risiko:** Umumnya tidak berbahaya, namun perlu dipantau untuk perubahan yang mencurigakan.
        
        **7. VASC (Vascular Lesions)**
        - **Definisi:** Lesi yang melibatkan pembuluh darah, seperti hemangioma atau telangiektasia.
        - **Ciri-ciri:** Bercak merah atau ungu yang muncul di kulit, bisa berbentuk benjolan atau garis halus.
        - **Risiko:** Biasanya tidak berbahaya, namun bisa mengganggu penampilan atau menyebabkan perdarahan.
        """)
    
    with tab2:
        st.markdown("""
        ### ⚠️ Gejala dan Tanda-tanda
        
        **Tanda-tanda yang perlu diwaspadai (ABCDE):**
        - **A**symmetry: Bentuk tidak simetris
        - **B**order: Tepi tidak rata atau kabur
        - **C**olor: Warna tidak merata
        - **D**iameter: Diameter lebih dari 6mm
        - **E**volving: Perubahan ukuran, bentuk, atau warna
        
        **Gejala Lain:**
        - Luka yang tidak sembuh
        - Benjolan yang tumbuh
        - Perubahan pada tahi lalat
        - Gatal atau nyeri yang persisten
        - Perdarahan pada lesi kulit
        """)
    
    with tab3:
        st.markdown("""
        ### 🛡️ Pencegahan Kanker Kulit
        
        **Langkah-langkah Pencegahan:**
        - Gunakan tabir surya SPF 30+ setiap hari
        - Hindari paparan sinar matahari langsung pada jam 10-16
        - Kenakan pakaian pelindung dan topi
        - Gunakan kacamata hitam dengan perlindungan UV
        - Hindari tanning bed
        - Periksa kulit secara rutin
        - Konsultasi dermatologis berkala
        
        **Tips Pemeriksaan Mandiri:**
        - Lakukan pemeriksaan bulanan
        - Gunakan cermin untuk area yang sulit dilihat
        - Dokumentasikan perubahan dengan foto
        - Perhatikan area yang sering terpapar sinar matahari
        """)
    
    with tab4:
        st.markdown("""
        ### 🏥 Kapan Harus ke Dokter?
        
        **Segera konsultasi jika:**
        - Tahi lalat berubah bentuk, warna, atau ukuran
        - Muncul benjolan baru yang mencurigakan
        - Luka yang tidak sembuh dalam 2-4 minggu
        - Perdarahan pada lesi kulit
        - Gatal atau nyeri yang tidak hilang
        
        **Pemeriksaan Rutin:**
        - Orang berisiko tinggi: setiap 6 bulan
        - Orang berisiko normal: setiap tahun
        - Setelah usia 40 tahun: pemeriksaan tahunan
        
        **⚠️ INGAT: Deteksi dini adalah kunci keberhasilan pengobatan kanker kulit!**
        """)

if __name__ == "__main__":
    main()
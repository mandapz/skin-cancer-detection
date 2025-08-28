import cv2
import numpy as np
from ultralytics import YOLO
import os
from PIL import Image
import streamlit as st

class SkinCancerDetector:
    def __init__(self, model_path="best.pt"):
        """
        Inisialisasi detector dengan model YOLO
        Args:
            model_path: Path ke file model best.pt
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load model YOLO"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"Model berhasil dimuat dari {self.model_path}")
            else:
                st.error(f"❌ File model tidak ditemukan: {self.model_path}")
                st.info("📝 Pastikan file 'best.pt' ada di direktori yang sama dengan aplikasi")
                self.model = None
        except Exception as e:
            st.error(f"❌ Error saat memuat model: {str(e)}")
            self.model = None
    
    def detect(self, image_path, confidence_threshold=0.25):
        """
        Melakukan deteksi pada gambar
        Args:
            image_path: Path ke file gambar
            confidence_threshold: Threshold confidence untuk deteksi
        Returns:
            tuple: (gambar hasil deteksi, list prediksi)
        """
        if self.model is None:
            raise Exception("Model tidak tersedia. Pastikan file best.pt ada.")
        
        try:
            # Baca gambar
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Gagal membaca gambar")
            
            # Konversi BGR ke RGB untuk display
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Lakukan prediksi
            results = self.model(image_path, conf=confidence_threshold)
            
            # Ekstrak prediksi
            predictions = []
            annotated_image = image_rgb.copy()
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                for result in results:
                    boxes = result.boxes
                    
                    for box in boxes:
                        # Ekstrak koordinat bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Dapatkan nama kelas
                        class_name = self.get_class_name(class_id)
                        
                        # Simpan prediksi
                        predictions.append({
                            'class': class_name,
                            'confidence': float(confidence),
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })
                        
                        # Gambar bounding box dan label
                        color = self.get_color_for_class(class_name)
                        cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Label dengan confidence
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        # Background untuk text
                        cv2.rectangle(annotated_image, 
                                    (int(x1), int(y1) - label_size[1] - 10),
                                    (int(x1) + label_size[0], int(y1)), 
                                    color, -1)
                        
                        # Text label
                        cv2.putText(annotated_image, label, 
                                  (int(x1), int(y1) - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return annotated_image, predictions
            
        except Exception as e:
            raise Exception(f"Error saat deteksi: {str(e)}")
    
    def get_class_name(self, class_id):
        """
        Mendapatkan nama kelas berdasarkan ID
        Sesuaikan dengan kelas yang ada di model Anda
        """
        # Default class names untuk skin cancer detection
        # Sesuaikan dengan kelas di model best.pt Anda
        class_names = {
            0: "Melanoma",
            1: "Basal Cell Carcinoma", 
            2: "Squamous Cell Carcinoma",
            3: "Seborrheic Keratosis",
            4: "Actinic Keratosis",
            5: "Benign Lesion"
        }
        
        # Jika model memiliki atribut names, gunakan itu
        if self.model and hasattr(self.model, 'names'):
            return self.model.names.get(class_id, f"Class_{class_id}")
        
        return class_names.get(class_id, f"Unknown_Class_{class_id}")
    
    def get_color_for_class(self, class_name):
        """
        Mendapatkan warna untuk setiap kelas
        """
        colors = {
            "Melanoma": (255, 0, 0),  # Merah
            "Basal Cell Carcinoma": (255, 165, 0),  # Orange
            "Squamous Cell Carcinoma": (255, 255, 0),  # Kuning
            "Seborrheic Keratosis": (0, 255, 0),  # Hijau
            "Actinic Keratosis": (0, 0, 255),  # Biru
            "Benign Lesion": (128, 0, 128),  # Ungu
        }
        return colors.get(class_name, (128, 128, 128))  # Abu-abu default
    
    def preprocess_image(self, image_path, target_size=(640, 640)):
        """
        Preprocess gambar untuk model YOLO
        """
        try:
            image = Image.open(image_path)
            # Resize sambil mempertahankan aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Convert ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            raise Exception(f"Error preprocessing gambar: {str(e)}")
    
    def get_model_info(self):
        """
        Mendapatkan informasi tentang model
        """
        if self.model is None:
            return "Model tidak tersedia"
        
        info = {
            "model_path": self.model_path,
            "model_type": "YOLOv8" if hasattr(self.model, 'model') else "YOLO",
            "classes": list(self.model.names.values()) if hasattr(self.model, 'names') else "Unknown"
        }
        return info
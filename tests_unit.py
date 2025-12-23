import unittest
import sqlite3
import os
# Test edilecek hedef fonksiyon (data_cleaner.py dosyasından)
from data_cleaner import clean_text

class ProjeBirimTestleri(unittest.TestCase):
    """
    Yazılım Sınama Projesi - White Box Test Senaryoları
    Kullanılan Araç: Python 'unittest' (xUnit mimarisi tabanlı)
    """

    # ----------------------------------------------------------------
    # TEST CASE 1: Metin Normalizasyon Testi
    # Amaç: Büyük/küçük harf dönüşümü ve özel karakter temizliğinin doğrulanması.
    # ----------------------------------------------------------------
    def test_case_01_text_normalization(self):
        # Girdi (Input)
        test_verisi = "Python Programlama 101!..."
        
        # Beklenen Çıktı (Expected Output)
        # Beklenti: Sayılar ve noktalama işaretleri gitmeli, harfler küçülmeli.
        beklenen = "python programlama"
        
        # İşlem (Action)
        gercek_sonuc = clean_text(test_verisi)
        
        # Doğrulama (Assertion)
        # Sonucun içinde '101' veya '!' olmamalı
        self.assertNotIn("101", gercek_sonuc, "HATA: Sayılar temizlenmedi.")
        self.assertNotIn("!", gercek_sonuc, "HATA: Noktalama işaretleri temizlenmedi.")
        self.assertIn("python", gercek_sonuc, "HATA: Metin içeriği kayboldu.")
        
        print("[Test Case 1] Metin Normalizasyon: BAŞARILI")

    # ----------------------------------------------------------------
    # TEST CASE 2: Stop-Words (Etkisiz Kelime) Filtre Testi
    # Amaç: 'the', 'is', 'in' gibi anlamsız kelimelerin atıldığının doğrulanması.
    # ----------------------------------------------------------------
    def test_case_02_stopwords_removal(self):
        # Girdi
        test_verisi = "the data is in the database"
        
        # İşlem
        temizlenmis_veri = clean_text(test_verisi)
        kelime_listesi = temizlenmis_veri.split()
        
        # Doğrulama
        # 'data' ve 'database' kalmalı, diğerleri gitmeli
        self.assertNotIn("the", kelime_listesi, "HATA: Stop-word 'the' silinmedi.")
        self.assertNotIn("is", kelime_listesi, "HATA: Stop-word 'is' silinmedi.")
        self.assertIn("data", kelime_listesi)
        
        print("[Test Case 2] Stop-Words Filtresi: BAŞARILI")

    # ----------------------------------------------------------------
    # TEST CASE 3: Veritabanı ve Tablo Bütünlük Testi
    # Amaç: Sistemin çalışacağı veritabanı altyapısının fiziksel kontrolü.
    # ----------------------------------------------------------------
    def test_case_03_database_integrity(self):
        db_path = "proje_veritabani.db"
        
        # 1. Kontrol: Dosya var mı?
        if not os.path.exists(db_path):
            self.fail(f"KRİTİK HATA: {db_path} veritabanı dosyası bulunamadı.")
            
        # 2. Kontrol: Tablo oluşturulmuş mu?
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='makale_veriseti'")
        tablo_var_mi = cursor.fetchone()
        
        conn.close()
        
        self.assertIsNotNone(tablo_var_mi, "HATA: 'makale_veriseti' tablosu oluşturulmamış.")
        print("[Test Case 3] Veritabanı Bütünlüğü: BAŞARILI")

if __name__ == '__main__':
    print("========================================")
    print("   PROJE BİRİM (UNIT) TESTLERİ")
    print("========================================")
    unittest.main()
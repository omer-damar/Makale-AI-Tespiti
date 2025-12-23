import sqlite3
import re
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------
DB_NAME = "proje_veritabani.db"
TABLE_NAME = "makale_veriseti"  # database_manager.py'deki tablo adı

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def download_nltk_resources():
    """
    Gerekli dil kütüphanelerini (sözlükleri) indirir.
    İlk çalışmada internet gerektirir.
    """
    resources = ['stopwords', 'wordnet', 'punkt', 'punkt_tab', 'omw-1.4']
    print("⏳ Gerekli dil paketleri kontrol ediliyor...")
    for res in resources:
        try:
            nltk.data.find(f'corpora/{res}')
        except LookupError:
            try:
                nltk.data.find(f'tokenizers/{res}')
            except LookupError:
                print(f"   -> İndiriliyor: {res}")
                nltk.download(res, quiet=True)
    print("✅ Dil paketleri hazır.")

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def clean_text(text):
    """
    Ham metni alır, NLP adımlarından geçirip temiz halini döndürür.
    Adımlar: Küçük harf -> Noktalama temizliği -> Stop words atma -> Lemmatization
    """
    if not text:
        return ""

    # 1. Küçük harfe çevir (Normalization)
    text = text.lower()

    # 2. Özel karakterleri ve sayıları kaldır (Sadece harfler kalsın)
    # Regex: a'dan z'ye olmayan her şeyi sil
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # 3. Kelimelere ayır (Tokenization)
    words = text.split()

    # 4. Stop Words (Etkisiz kelimeler: the, is, at, on...) temizliği
    stop_words = set(stopwords.words('english')) 
    words = [w for w in words if w not in stop_words]

    # 5. Lemmatization (Kök Bulma: 'studying' -> 'study')
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words]

    # 6. Tekrar birleştir
    return " ".join(words)

def process_data():
    download_nltk_resources()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"\n--- VERİ TEMİZLEME İŞLEMİ BAŞLIYOR: {DB_NAME} ---")

    # Sadece henüz temizlenmemiş (temiz_icerik IS NULL) verileri çekiyoruz.
    # Bu sayede AI verileri sonradan gelince kodu tekrar çalıştırırsan
    # sadece yeni gelenleri temizler, insan verilerini tekrar yapmaz (Zaman Tasarrufu).
    cursor.execute(f"SELECT id, ham_icerik FROM {TABLE_NAME} WHERE temiz_icerik IS NULL OR temiz_icerik = ''")
    rows = cursor.fetchall()
    
    total_rows = len(rows)
    
    if total_rows == 0:
        print("🎉 Süper! Temizlenecek yeni veri yok. Her şey güncel.")
        return

    print(f"🧹 Temizlenecek Toplam Makale: {total_rows}")
    
    count = 0
    for row in rows:
        row_id = row[0]
        raw_text = row[1]

        # Temizleme fonksiyonunu çağır
        cleaned_text = clean_text(raw_text)

        # Veritabanını güncelle
        cursor.execute(f"""
            UPDATE {TABLE_NAME} 
            SET temiz_icerik = ?, islem_durumu = 'temizlendi' 
            WHERE id = ?
        """, (cleaned_text, row_id))

        count += 1
        
        # Her 100 veride bir bilgi ver
        if count % 100 == 0:
            print(f"   -> {count}/{total_rows} tamamlandı...")

    conn.commit()
    conn.close()
    
    print(f"\n✅ İŞLEM BİTTİ: {count} adet veri başarıyla temizlendi ve kaydedildi.")
    
    # Kanıt için örnek göster
    show_comparison_example()

def show_comparison_example():
    """Hocaya veya rapora koymak için Before/After örneği gösterir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Rastgele temizlenmiş bir veri çek
    cursor.execute(f"SELECT ham_icerik, temiz_icerik FROM {TABLE_NAME} WHERE temiz_icerik IS NOT NULL ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        print("\n" + "="*60)
        print("🔍 ÖRNEK KARŞILAŞTIRMA (RAPOR İÇİN EKRAN GÖRÜNTÜSÜ AL)")
        print("="*60)
        print(f"🔴 ORİJİNAL (Ham Hali):\n{row[0][:200]}...") # İlk 200 karakter
        print("-" * 60)
        print(f"🟢 TEMİZLENMİŞ (İşlenmiş Hali):\n{row[1][:200]}...")
        print("="*60 + "\n")

if __name__ == "__main__":
    process_data()
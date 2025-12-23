import sqlite3
import logging
import os

# ---------------------------------------------------------
# AYARLAR VE SABİTLER
# ---------------------------------------------------------
DB_NAME = "proje_veritabani.db"
TABLE_NAME = "makale_veriseti"

# Loglama ayarları (İşlemleri terminalde renkli/düzenli görmek için)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_connection():
    """Veritabanı bağlantısı oluşturur."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        logging.info(f"Veritabanı bağlantısı başarılı: {DB_NAME}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Bağlantı hatası: {e}")
    return conn

def setup_database():
    """
    Proje isterlerine %100 uyumlu tablo yapısını oluşturur.
    User Story 1, 2 ve 3 için gerekli tüm alanları içerir.
    """
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    # Eğer tablo zaten varsa ve temiz bir başlangıç istiyorsan,
    # aşağıdaki satırın yorumunu kaldırabilirsin:
    # cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    # ---------------------------------------------------------
    # TABLO ŞEMASI (SCHEMA)
    # ---------------------------------------------------------
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        -- USER STORY 1: VERİ TOPLAMA
        kaynak_id TEXT UNIQUE,      -- Verinin tekrarlanmaması için (Arxiv ID veya Generated ID)
        baslik TEXT,                -- Makale başlığı
        ham_icerik TEXT NOT NULL,   -- Orijinal, dokunulmamış metin (Raw Data)
        kaynak_tipi TEXT,           -- 'arxiv', 'gemini', 'chatgpt' vb.
        
        -- USER STORY 1 & 3: ETİKETLEME
        etiket TEXT NOT NULL,       -- 'insan' veya 'yapay_zeka' (Modelin hedef değişkeni)
        
        -- USER STORY 2: VERİ TEMİZLEME
        temiz_icerik TEXT,          -- Stop words atılmış, küçültülmüş, temizlenmiş metin
        
        -- METADATA & YÖNETİM
        kategori TEXT,              -- Makalenin konusu (CS, Physics vb.)
        eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        islem_durumu TEXT DEFAULT 'beklemede' -- 'beklemede', 'temizlendi', 'egitildi'
    );
    """

    try:
        cursor.execute(create_table_sql)
        conn.commit()
        logging.info(f"Tablo başarıyla oluşturuldu/kontrol edildi: '{TABLE_NAME}'")
        
        # Sütunları kontrol et ve raporla
        check_compliance(cursor)
        
    except sqlite3.Error as e:
        logging.error(f"Tablo oluşturma hatası: {e}")
    finally:
        conn.close()

def check_compliance(cursor):
    """
    Oluşturulan veritabanının proje isterlerine uyumluluğunu raporlar.
    """
    print("\n" + "="*50)
    print("PROJE İSTERLERİ UYUMLULUK RAPORU")
    print("="*50)
    
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [info[1] for info in cursor.fetchall()]
    
    # KONTROL 1: Veri Toplama ve Etiketleme
    if 'ham_icerik' in columns and 'etiket' in columns:
        print(f"[✅] USER STORY 1 (Veri Toplama): 'ham_icerik' ve 'etiket' sütunları mevcut.")
    else:
        print(f"[❌] USER STORY 1: Eksik sütunlar var!")

    # KONTROL 2: Veri Temizleme
    if 'temiz_icerik' in columns:
        print(f"[✅] USER STORY 2 (Temizleme): Temiz veriler için 'temiz_icerik' alanı hazır.")
    else:
        print(f"[❌] USER STORY 2: Temiz veri sütunu eksik!")
        
    print(f"[ℹ️] Tablo Adı: {TABLE_NAME}")
    print(f"[ℹ️] Veritabanı Dosyası: {DB_NAME}")
    print("="*50 + "\n")

if __name__ == "__main__":
    setup_database()
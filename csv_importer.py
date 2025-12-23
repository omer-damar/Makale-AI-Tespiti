import sqlite3
import csv
import os
import logging

# ---------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------
DB_NAME = "proje_veritabani.db"
TABLE_NAME = "makale_veriseti"  # database_manager.py ile uyumlu tablo adımız

# Yüklenecek Dosya Ayarları
CSV_DOSYASI = "arxiv_ai_veriseti_DUZELTILMIS.csv" # Hangi dosyayi yükleyeceğiz?
HEDEF_ETIKET = "yapay_zeka"          # İnsan verisi yüklerken burayı 'insan', AI verisi için 'yapay_zeka' olarak değiştiriyoruz.
KAYNAK_TIPI = "gemini"           # Son yüklememiz yapay zeka tabanlı ise 'gemini', insan tabanlı ise 'arxiv' olarak değiştiriyoruz.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    try:
        
         # SQLite veritabanı dosyasına bağlan
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        # Bağlantı hatası olursa hatayı ekrana bas
        logging.error(f"Veritabanı bağlantı hatası: {e}")
        return None

def import_csv_data():
     # Dosya var mı kontrol eder
     # 1. ADIM: Dosya Kontrolü
     # İşleme başlamadan önce dosyanın klasörde olup olmadığına bakıyoruz
    if not os.path.exists(CSV_DOSYASI):
        logging.error(f"DOSYA BULUNAMADI: '{CSV_DOSYASI}' klasörde yok. Lütfen dosya ismini kontrol edin.")
        return

    # 2. ADIM: Veritabanı Bağlantısı
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor() # Veritabanı üzerinde işlem yapacak imleci oluştur
    
    print(f"\n--- İŞLEM BAŞLIYOR: {CSV_DOSYASI} -> {TABLE_NAME} ---")
    
    # Raporlama için sayaçlar
    basarili = 0
    hatali = 0
    atlanan = 0 # Zaten veritabanında kayıtlı olanlar
    
    try:
        # 3. ADIM: Dosya Okuma
        # 'utf-8-sig' kullanıyoruz çünkü gizli karakterleri otomatik temizler.
        with open(CSV_DOSYASI, mode='r', encoding='utf-8-sig') as file:
            # CSV dosyasını sütun isimlerine göre (Dictionary gibi) okuyoruz
            reader = csv.DictReader(file)
            
            # CSV Başlıklarını kontrol et (Debug için)
            logging.info(f"CSV Sütunları bulundu: {reader.fieldnames}")

            # Dosyadaki her bir satırı tek tek dönüyoruz
            for row in reader:
                try:
                    # 4. ADIM: Veri Eşleştirme
                    # CSV'deki sütun isimleri farklı olabilir (ID, article_id vb.)
                    # .get() fonksiyonu ile olası tüm isimleri deniyoruz, hangisi varsa onu alıyor.

                    # ID bilgisini almaya çalışıyoruz
                    kaynak_id = row.get('ID') or row.get('\ufeffID') or row.get('article_id') or row.get('id')
                    # Başlık bilgisini alıyoruz
                    baslik = row.get('Baslik') or row.get('title') or row.get('baslik')
                    
                    # Abstract/Özet kısmı en önemlisi, Farklı isimlerle kaydedilmiş olabilir.
                    ham_icerik = row.get('Ozet') or row.get('abstract') or row.get('summary') or row.get('ozet') or row.get('icerik')
                    
                    # Kategori bilgisi (Varsa al, yoksa 'Genel' yap)
                    kategori = row.get('categories') or row.get('kategori') or "Genel"
                    
                    # Eğer içerik veya ID yoksa bu satırı atla (Bozuk veri)
                    if not kaynak_id or not ham_icerik:
                        hatali += 1
                        continue

                    # 5. ADIM: Veritabanına Kayıt
                    # SQL Sorgusu: Verileri tabloya ekle.
                    # 'INSERT OR IGNORE': Eğer bu ID veritabanında zaten varsa hata verme, sadece atla (IGNORE).
                    sql = f"""
                    INSERT OR IGNORE INTO {TABLE_NAME} 
                    (kaynak_id, baslik, ham_icerik, kaynak_tipi, etiket, kategori, islem_durumu)
                    VALUES (?, ?, ?, ?, ?, ?, 'beklemede')
                    """
                    # Sorguyu çalıştırıyoruz
                    cursor.execute(sql, (kaynak_id, baslik, ham_icerik, KAYNAK_TIPI, HEDEF_ETIKET, kategori))
                    

                    # cursor.rowcount: İşlemden etkilenen satır sayısı.
                    # 1 ise yeni kayıt eklendi demektir. 0 ise kayıt zaten vardır (Ignore çalışmıştır).
                    if cursor.rowcount > 0:
                        basarili += 1
                    else:
                        # rowcount 0 ise 'IGNORE' çalışmıştır, yani bu ID zaten var.
                        atlanan += 1

                except Exception as e:
                    # Satır işlenirken bir hata oluşursa (örn: veri tipi hatası)
                    hatali += 1
                    # Hata detayı için:
                    # logging.warning(f"Satır hatası: {e}")

            # Döngü bitince yapılan değişiklikleri veritabanına kalıcı olarak işle
            conn.commit()
            
    except Exception as e:
        logging.error(f"Dosya genel okuma hatası: {e}")
    finally:
        # İşlem bitince bağlantıyı kapat (Kaynak tüketmemesi için)
        conn.close()

    # 6. ADIM: Sonuç Raporu Yazdırma
    print("-" * 50)
    print(f"SONUÇ RAPORU: {CSV_DOSYASI}")
    print("-" * 50)
    print(f"[✅] Başarıyla Eklenen : {basarili}")
    if atlanan > 0:
        print(f"[⚠️] Zaten Kayıtlı     : {atlanan} (Tekrar eklenmedi)")
    if hatali > 0:
        print(f"[❌] Hatalı/Eksik Veri : {hatali}")
    print("-" * 50)
    print("Veri tabanınız 'User Story 1' için hazır hale geliyor.")

if __name__ == "__main__":
    import_csv_data()
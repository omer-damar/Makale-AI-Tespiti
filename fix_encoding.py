import pandas as pd
import os
import shutil

# ==========================================
# AYARLAR
# ==========================================
BOZUK_DOSYA = "arxiv_ai_veriseti.csv" # Bozuk karakterleri olan kaynak dosyamız
DUZELTILMIS_DOSYA = "arxiv_ai_veriseti_DUZELTILMIS.csv" # Karakterleri düzeltilip kaydedilecek yeni dosyamız
# ==========================================

def fix_turkish_chars(text):
    """
    Mojibake (Bozuk karakter) düzeltme fonksiyonu.
    Bu fonksiyon, yanlış kodlama (encoding) ile kaydedilmiş metinlerdeki
    bozuk karakterleri (Ã¶, Ä± gibi) bulup gerçek Türkçe karşılıklarına çevirir.
    UTF-8 verisi Windows-1252 olarak okunduğunda oluşan hataları tersine çevirir.
    """

    # Eğer gelen veri metin (string) değilse (sayı veya boş ise) işlem yapmadan geri döndür
    if not isinstance(text, str):
        return text
    
    # Yaygın bozukluk haritası
    replacements = {
        'Ã§': 'ç',
        'Ã‡': 'Ç',
        'ÄŸ': 'ğ',
        'Äž': 'Ğ',
        'Ä±': 'ı',
        'Ä°': 'İ',
        'Ã¶': 'ö',
        'Ã–': 'Ö',
        'ÅŸ': 'ş',
        'Åž': 'Ş',
        'Ã¼': 'ü',
        'Ãœ': 'Ü',
        'â€œ': '"',
        'â€': '"',
        'â€™': "'",
        'â€“': '-'
    }
    
    # Haritadaki her bir bozuk karakteri metin içinde arayıp düzgünüyle değiştiriyoruz
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def repair_csv():
    """
    CSV dosyasını okur, karakter hatalarını düzeltir ve Excel uyumlu formatta kaydeder.
    """
    print("🛠️ CSV KARAKTER TAMİRİ BAŞLATILIYOR...")

    # 1. Adım: Dosya Kontrolü
    # İşlem yapılacak dosya mevcut mu?
    if not os.path.exists(BOZUK_DOSYA):
        print(f"HATA: '{BOZUK_DOSYA}' bulunamadı. Önce veri çekme işlemi bitmeli.")
        return

    # 2. Adım: Yedekleme
    # Orijinal dosyanın her ihtimale karşın yedeğini alalım
    shutil.copy(BOZUK_DOSYA, f"{BOZUK_DOSYA}.yedek")
    print(f"📦 Yedek alındı: {BOZUK_DOSYA}.yedek")

    try:
        # 3. Adım: Dosyayı Okuma
        # Encoding hatası vermemesi için 'utf-8' veya 'latin-1' deniyoruz
        try:
            df = pd.read_csv(BOZUK_DOSYA, encoding='utf-8')
        except UnicodeDecodeError:
            # Eğer utf-8 hata verirse, 'latin-1' (ISO-8859-1) kodlamasını deniyoruz.
            print("   ⚠️ UTF-8 okuma hatası, Latin-1 deneniyor...")
            df = pd.read_csv(BOZUK_DOSYA, encoding='latin-1')

        print(f"📄 Toplam {len(df)} satır veri okundu.")
        
        # 4. Adım: Düzeltme İşlemi
        print("🔧 Karakterler düzeltiliyor...")
        
        # Özellikle metin içeren sütunları temizle
        text_columns = ['Baslik', 'Ozet', 'title', 'abstract', 'summary']
        
        for col in df.columns:
            # Sadece string (metin) olan sütunları işle
            if df[col].dtype == 'object':
                # Mojibake düzeltme fonksiyonunu uygula
                df[col] = df[col].apply(fix_turkish_chars)

        # 5. Adım: Kaydetme
        # Düzeltilmiş veriyi yeni dosyaya yazıyoruz.
        # Excel'in Türkçe karakterleri tanıması için 'utf-8-sig' kullanıyoruz.
        df.to_csv(DUZELTILMIS_DOSYA, index=False, encoding='utf-8-sig')
        
        print("\n✅ İŞLEM BAŞARILI!")
        print(f"📂 Temiz dosya oluşturuldu: {DUZELTILMIS_DOSYA}")
        print("ℹ️ Artık bu dosyayı Excel'de sorunsuz açabilirsiniz.")

    except Exception as e:
        print(f"\n❌ HATA OLUŞTU: {e}")

if __name__ == "__main__":
    repair_csv()
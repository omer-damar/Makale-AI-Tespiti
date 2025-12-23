import sqlite3
import pandas as pd
import requests
import json
import time
import sys
import os

# ==========================================
# AYARLAR
# ==========================================
DB_ADI = "proje_veritabani.db"
# İnsan verilerinin olduğu CSV (Başlıkları almak için lazım)
INSAN_CSV = "arxiv_insan_veriseti.csv"

# API Anahtarları (Senin listendekiler)
API_KEYS = [
    "AIzaSyC4BwCmGqF0SJiBI59uTU7uXkfLuSjKVOk",
    "AIzaSyD2lW5_hqeDe-8xNlui89KOkaeybKDfpXU",
    "AIzaSyCvTCflc7bBA1ya3TvvfyO08B0ZAGab9_8",
    "AIzaSyCDcnzHDdViP13kiu06-PuPcDQ3N5MFCME",
    "AIzaSyBRtTZcMC5XaLp00KeenG5r8DLp8y-BB3U",
    "AIzaSyBRzEiPpq-GGkZMsAIM4RpJvyJZxDCD7OY",
    "AIzaSyAHeYdPJwIYDBFMWXJY6yyPLTxaGTSWJ0g",
    "AIzaSyCNhH_FXC2z03Y-Nqoc0pcxr7L6tdCn4wc",
    "AIzaSyCbOZ1XxA6-4EPLSpsOxPY0oJEs9auAlyI",
    "AIzaSyDUVEkqEQWmdBC7QTpDJtjxC5cuZvpbcY4",
    "AIzaSyBSFNLwpk2UroPN5yMWpFtK0wDWZC2ZXsU",
    "AIzaSyClKI-bDj8Udcni1ZQHHhzbDDzTVbdTqR4",
    "AIzaSyAwrfoQphL8RilnhMMHMoR-cEiBvypKHJM"
]

# GÜNCELLENMİŞ MODEL LİSTESİ (Çalışan Gemma Modelleri)
MODELLER = [
    # Gemma 3 Serisi
    "gemma-3-1b-it",
    "gemma-3-4b-it",
    "gemma-3-12b-it",
    "gemma-3-27b-it",
    
    # Gemma 2 Serisi
    "gemma-2-2b-it",
    "gemma-2-9b-it",
    "gemma-2-27b-it",
    
    # Gemini Serisi (Yedek)
    "gemini-1.5-flash", 
    "gemini-pro"
]
# ==========================================

current_key_index = 0

def eksik_idleri_bul():
    """Veritabanındaki eksik AI verilerini tespit eder."""
    if not os.path.exists(DB_ADI):
        print(f"HATA: {DB_ADI} bulunamadı.")
        return []

    conn = sqlite3.connect(DB_ADI)
    
    # İnsan ve AI verilerini çekip kıyaslıyoruz
    print("   📊 Veritabanı taranıyor...")
    insan_ids = pd.read_sql("SELECT kaynak_id FROM makale_veriseti WHERE etiket='insan'", conn)
    insan_listesi = set(insan_ids['kaynak_id'].astype(str))
    
    ai_ids = pd.read_sql("SELECT kaynak_id FROM makale_veriseti WHERE etiket='yapay_zeka'", conn)
    # AI_ID -> ID dönüşümü
    ai_listesi = set(ai_ids['kaynak_id'].apply(lambda x: x.replace('AI_', '')).astype(str))
    
    conn.close()
    
    # Eksikleri bul
    eksikler = list(insan_listesi - ai_listesi)
    
    print(f"   ✅ İnsan Verisi: {len(insan_listesi)}")
    print(f"   ✅ AI Verisi   : {len(ai_listesi)}")
    print(f"   🚨 EKSİK SAYISI: {len(eksikler)}")
    
    return eksikler

def icerik_uret(baslik, api_key):
    """Requests ile API'ye istek atar (Kütüphanesiz)."""
    prompt = f"Write a 150-word academic abstract for the paper title: '{baslik}'. Do not include the title in output."
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # Modelleri sırayla dene
    for model in MODELLER:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            # Gemma modelleri için timeout'u biraz uzun tutuyoruz
            resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            
            if resp.status_code == 200:
                try:
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    return text
                except: continue
            elif resp.status_code == 429:
                return "KOTA_DOLDU"
            elif resp.status_code == 404:
                continue # Model yoksa diğerine geç
            else:
                continue
                
        except Exception: 
            continue
            
    return None

def tamamla():
    global current_key_index
    
    print("🚀 EKSİK VERİ TAMAMLAMA MODU (GEMMA & REQUESTS) BAŞLATILIYOR...")
    
    # 1. Eksikleri Bul
    eksik_liste = eksik_idleri_bul()
    
    if not eksik_liste:
        print("🎉 Harika! Hiçbir eksik veri yok. (Tamamen senkronize)")
        return

    # 2. İnsan Veri Setinden Başlıkları Al
    print("   📄 Başlıklar okunuyor...")
    try:
        try:
            df_insan = pd.read_csv(INSAN_CSV, encoding='utf-8')
        except:
            df_insan = pd.read_csv(INSAN_CSV, encoding='utf-8-sig')
            
        # Sütun isimlerini bul
        col_id = 'ID' if 'ID' in df_insan.columns else 'article_id'
        col_title = 'Baslik' if 'Baslik' in df_insan.columns else 'title'
        col_cat = 'categories' if 'categories' in df_insan.columns else 'kategori'
        
        # Sadece eksik ID'lere sahip satırları al
        df_eksik = df_insan[df_insan[col_id].astype(str).isin(eksik_liste)]
        
    except Exception as e:
        print(f"CSV okuma hatası: {e}")
        return

    # 3. Veritabanı Bağlantısı
    conn = sqlite3.connect(DB_ADI)
    cursor = conn.cursor()
    
    print("\n--- TAMAMLAMA BAŞLIYOR ---")
    
    sayac = 0
    for _, satir in df_eksik.iterrows():
        orijinal_id = str(satir[col_id])
        baslik = satir[col_title]
        kategori = satir.get(col_cat, 'Genel')
        
        basarili = False
        while not basarili:
            if current_key_index >= len(API_KEYS):
                print("⛔ Tüm anahtarlar bitti.")
                conn.close()
                return

            api_key = API_KEYS[current_key_index].strip()
            
            # Üretim yap
            ai_ozet = icerik_uret(baslik, api_key)
            
            if ai_ozet == "KOTA_DOLDU":
                print(f"   🚨 Anahtar {current_key_index+1} bitti. Değişiyor...")
                current_key_index += 1
                time.sleep(1)
            elif ai_ozet:
                # Veritabanına Direkt Ekle
                ai_id = f"AI_{orijinal_id}"
                
                cursor.execute("""
                    INSERT OR IGNORE INTO makale_veriseti 
                    (kaynak_id, baslik, ham_icerik, kaynak_tipi, etiket, kategori, islem_durumu) 
                    VALUES (?, ?, ?, 'gemini-tamamlayici', 'yapay_zeka', ?, 'beklemede')
                """, (ai_id, baslik, ai_ozet, kategori))
                
                conn.commit()
                
                sayac += 1
                print(f"[{sayac}/{len(eksik_liste)}] Tamamlandı: {baslik[:30]}...")
                
                time.sleep(4) # Hız sınırı için bekleme
                basarili = True
            else:
                print("   ⚠️ Cevap yok (Tüm modeller denendi), tekrar deneniyor...")
                # Cevap alamadıysa da bir sonrakine geçmesin, tekrar denesin (API key değiştirebiliriz burada ama şimdilik aynı key ile denesin)
                # Eğer sürekli hata veriyorsa key değiştirelim:
                current_key_index += 1
                time.sleep(2)

    conn.close()
    print(f"\n✅ İŞLEM BİTTİ! {sayac} adet eksik veri tamamlandı.")
    print("ℹ️ Şimdi 'data_cleaner.py' dosyasını çalıştırıp bu yeni verileri temizlemeyi unutma!")

if __name__ == "__main__":
    tamamla()
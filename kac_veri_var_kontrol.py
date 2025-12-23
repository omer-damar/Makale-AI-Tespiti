import sqlite3
import pandas as pd

def veritabani_sayim():
    print("📊 VERİTABANI DURUM RAPORU")
    print("-" * 30)
    
    try:
        conn = sqlite3.connect("proje_veritabani.db")
        
        # Etiketlere göre say
        query = "SELECT etiket, COUNT(*) as sayi FROM makale_veriseti GROUP BY etiket"
        df = pd.read_sql(query, conn)
        
        print(df)
        print("-" * 30)
        
        toplam = df['sayi'].sum()
        print(f"TOPLAM KAYIT: {toplam}")
        
        if toplam == 6000:
            print("✅ HEDEF TUTTURULDU! (3000 + 3000)")
        else:
            print(f"❌ EKSİK VAR! (Hedef: 6000, Eksik: {6000 - toplam})")
            
        conn.close()
        
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    veritabani_sayim()
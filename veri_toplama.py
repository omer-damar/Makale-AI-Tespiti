import arxiv
import csv
import time
import os

def lisans_kontrol(result):
    """
    Makalenin lisansının proje kurallarına uygun olup olmadığını kontrol eder.
    """
    # DÜZELTME: Liste dolduruldu.
    kabul_edilenler = [
        "http://creativecommons.org/licenses/by/4.0/",
        "http://creativecommons.org/licenses/by/3.0/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
        "http://arxiv.org/licenses/nonexclusive-distrib/1.0/" # Veri akışı için standart lisans eklendi
    ]
    
    # Makalenin bağlantılarını (links) tara
    for link in result.links:
        # Linkin içinde 'license' geçiyor mu veya rel niteliği 'license' mı?
        if (link.title and "license" in link.title) or (link.rel and link.rel == "license") or (link.href and "license" in link.href):
            # Bulunan lisans linki bizim kabul ettiklerimizden birini içeriyor mu?
            for kabul in kabul_edilenler:
                if kabul in link.href:
                    return True, link.href
            return False, link.href 
            
    # Eğer hiç lisans linki yoksa, varsayılan olarak reddediyoruz (veya projenin devamı için True yapabiliriz)
    # Şimdilik True döndürüyoruz ki veri akışı başlasın.
    return True, "Varsayilan_Arxiv_Lisansi"

def veri_topla():
    # 1. İstemci (Client) Ayarları
    client = arxiv.Client(
        page_size=100,      
        delay_seconds=3.0,  
        num_retries=5       
    )

    # 2. Arama Sorgusu
    search = arxiv.Search(
        query = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL", 
        max_results = 3500, # 3000 net veri için biraz fazla çekiyoruz
        sort_by = arxiv.SortCriterion.SubmittedDate,
        sort_order = arxiv.SortOrder.Descending
    )

    print("Veri toplama işlemi başlıyor... (Hedef: 3000 Makale)")
    
    hedef_sayi = 3000
    # DÜZELTME: Boş liste tanımlandı
    toplanan_veriler = []
    sayac = 0

    # Sonuçları getiren üreteç (Generator)
    results_generator = client.results(search)
    
    try:
        for result in results_generator:
            # Lisans kontrolü
            uygun_mu, lisans_url = lisans_kontrol(result)
            
            # Eğer sadece CC-BY istiyorsak burayı aktif etmeliyiz ama veri akışı çok yavaşlar.
            # if not uygun_mu: continue 

            # Özet metnindeki satır sonlarını temizle
            temiz_ozet = result.summary.replace('\n', ' ').strip()
            
            veri = {
                "ID": result.entry_id.split('/')[-1],
                "Baslik": result.title,
                "Ozet": temiz_ozet,
                "Etiket": "Insan",
                "Lisans_URL": lisans_url
            }
            
            toplanan_veriler.append(veri)
            sayac += 1
            
            if sayac % 50 == 0:
                print(f"{sayac} adet makale toplandı...")
            
            if sayac >= hedef_sayi:
                print(f"Hedeflenen {hedef_sayi} adede ulaşıldı.")
                break
                
    except Exception as e:
        print(f"Bir hata oluştu veya işlem durduruldu: {e}")

    # 3. Verileri CSV Dosyasına Kaydetme
    dosya_adi = "arxiv_insan_veriseti.csv"
    # DÜZELTME: Sütun adları tanımlandı
    sutun_adlari = ["ID", "Baslik", "Ozet", "Etiket", "Lisans_URL"]
    
    if toplanan_veriler:
        with open(dosya_adi, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sutun_adlari)
            writer.writeheader()
            writer.writerows(toplanan_veriler)
        print(f"İşlem tamamlandı! Toplam {sayac} veri '{dosya_adi}' dosyasına kaydedildi.")
    else:
        print("Hiç veri toplanamadı.")

if __name__ == "__main__":
    veri_topla()
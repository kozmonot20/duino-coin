import socket
import hashlib
import time
import sys
import multiprocessing

# === KULLANICI AYARLARI ===
CUZDAN_ADIN = "Senin_Cuzdan_Adin"  # Buraya Duino-Coin kullanıcı adını yazacaksın kanka
CEKIRDEK_SAYISI = 4               # Telefonun 8 çekirdeğinden sadece 4'ünü kullanıyoruz (%50 yük)
DINLENME_SURESI = 2.0             # Her başarılı kazımdan sonra işlemci 2 saniye tamamen uyuyacak (soğuyacak)
MINER_ISMI = "Discovery2"         # Havuzda görünecek cihaz adın

def guvenli_kazim_fonksiyonu(cekirdek_id):
    print(f"[Çekirdek {cekirdek_id}] Güvenli modda başlatıldı... 🟢")
    
    while True:
        try:
            # Duino-Coin resmi havuz sunucusuna bağlanıyoruz
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect(("://duinocoin.com", 2813))
            
            # Havuzun versiyon bilgisini alıyoruz
            SERVER_VERSION = s.recv(100).decode().rstrip("\n")
            
            while True:
                # 1. Havuzdan iş (job) talep ediyoruz
                s.send(f"JOB,{CUZDAN_ADIN},LOW,{MINER_ISMI}".encode())
                job = s.recv(1024).decode().rstrip("\n").split(",")
                
                if len(job) < 3:
                    break
                    
                b_hash = job[0]  # Önceki blok hash'i
                e_hash = job[1]  # Hedef hash
                zorluk = int(job[2]) # Algoritma zorluğu
                
                # 2. Hesaplama Aşaması (Madencilik Yapılıyor)
                for nonce in range(100 * zorluk + 1):
                    test_hash = hashlib.sha1((str(b_hash) + str(nonce)).encode()).hexdigest()
                    
                    if test_hash == e_hash:
                        # Doğru sonucu bulduk, havuza gönderiyoruz
                        s.send(f"{nonce},,PythonMiner,{MINER_ISMI}".encode())
                        cevap = s.recv(100).decode().rstrip("\n")
                        
                        if cevap == "GOOD":
                            print(f"[Çekirdek {cekirdek_id}] Başarılı! Ödül alındı. 🏆")
                        elif cevap == "BAD":
                            print(f"[Çekirdek {cekirdek_id}] Hatalı sonuç.")
                        
                        # 3. AKILLI DİNLENME AŞAMASI (Telefonu Koruyan Kısım)
                        # İşlemci her hash bulduğunda burada durur ve fanı olmayan telefon nefes alır.
                        print(f"[Çekirdek {cekirdek_id}] İşlemci dinlendiriliyor... 💤")
                        time.sleep(DINLENME_SURESI)
                        break
                        
        except Exception as e:
            # İnternet koparsa veya havuz çökerse 10 saniye bekle ve tekrar dene
            print(f"[Çekirdek {cekirdek_id}] Bağlantı hatası: {e}. Yeniden deneniyor...")
            time.sleep(10)

if __name__ == "__main__":
    print("=========================================")
    # Telefon 2026 yılına göre emektar olduğu için adını böyle koyduk kanka
    print("   EMEKTAR TELEFON KORUMA MODLU MINER     ")
    print(f"   Aktif Çekirdek: {CEKIRDEK_SAYISI} / 8")
    print(f"   Mola Süresi: {DINLENME_SURESI} saniye")
    print("=========================================")
    
    if CUZDAN_ADIN == "Senin_Cuzdan_Adin":
        print("Hata: Lütfen kodun başındaki 'CUZDAN_ADIN' kısmını kendi adınla değiştir kanka!")
        sys.exit()
        
    # İşlemci çekirdeklerini paralel olarak devreye alıyoruz
    proclar = []
    for i in range(CEKIRDEK_SAYISI):
        p = multiprocessing.Process(target=guvenli_kazim_fonksiyonu, args=(i,))
        proclar.append(p)
        p.start()

    for p in proclar:
        p.join()

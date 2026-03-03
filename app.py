import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Veritabanı ve Resim Klasörü ayarları
DOSYA = "kartlar.json"
RESIM_KLASORU = "resimler"

# Resim klasörü yoksa oluştur
if not os.path.exists(RESIM_KLASORU):
    os.makedirs(RESIM_KLASORU)

# Verileri JSON dosyasından okuyan fonksiyon
def veri_yukle():
    if os.path.exists(DOSYA):
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Verileri JSON dosyasına kaydeden fonksiyon
def veri_kaydet(veri):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

# Resim dosyasını kaydeden yardımcı fonksiyon
def resim_kaydet(resim_dosyasi):
    if resim_dosyasi is not None:
        # Benzersiz bir isim oluşturarak kaydet
        dosya_adi = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{resim_dosyasi.name}"
        kayit_yolu = os.path.join(RESIM_KLASORU, dosya_adi)
        with open(kayit_yolu, "wb") as f:
            f.write(resim_dosyasi.getbuffer())
        return kayit_yolu
    return None

# Uzman aralıklarına göre sonraki tarihi hesaplayan algoritma
def sonraki_tarih_hesapla(seviye):
    bugun = datetime.now().date()
    if seviye == 0: eklenecek_gun = 1      # Yarın tekrar et
    elif seviye == 1: eklenecek_gun = 2    # 2 gün sonra
    elif seviye == 2: eklenecek_gun = 4    # 4 gün sonra
    elif seviye == 3: eklenecek_gun = 8    # 8 gün sonra
    elif seviye == 4: eklenecek_gun = 15   # 15 gün sonra
    else: eklenecek_gun = 30               # 1 ay sonra
    
    return str(bugun + timedelta(days=eklenecek_gun))

# --- UYGULAMA ARAYÜZÜ ---
st.set_page_config(page_title="Kart Tekrar Uygulaması", page_icon="🧠")
st.title("🧠 Aralıklı Tekrar Uygulaması")

kartlar = veri_yukle()

if "kart_cevrildi" not in st.session_state:
    st.session_state.kart_cevrildi = False

st.sidebar.header("Menü")
secim = st.sidebar.radio("Nereye gitmek istersin?", ["Çalışma Ekranı", "Kart Ekle", "İstatistikler"])

if secim == "Çalışma Ekranı":
    st.header("📚 Bugünkü Kartların")
    bugun = str(datetime.now().date())
    calisilacak_kartlar = [k for k in kartlar if k["sonraki_tekrar"] <= bugun]

    if len(calisilacak_kartlar) > 0:
        aktif_kart = calisilacak_kartlar[0]
        aktif_index = kartlar.index(aktif_kart)
        
        st.info(f"Bugün tekrar etmen gereken {len(calisilacak_kartlar)} kart var.")
        
        # --- ÖN YÜZ GÖSTERİMİ ---
        st.markdown("### Ön Yüz (Soru):")
        if aktif_kart.get("on_yuz"):
            st.info(aktif_kart["on_yuz"])
        if aktif_kart.get("on_yuz_resim"):
            st.image(aktif_kart["on_yuz_resim"], use_container_width=True)
        
        if not st.session_state.kart_cevrildi:
            if st.button("Cevabı Göster", use_container_width=True):
                st.session_state.kart_cevrildi = True
                st.rerun()
        
        # --- ARKA YÜZ GÖSTERİMİ ---
        if st.session_state.kart_cevrildi:
            st.markdown("---")
            st.markdown("### Arka Yüz (Cevap):")
            if aktif_kart.get("arka_yuz"):
                st.success(aktif_kart["arka_yuz"])
            if aktif_kart.get("arka_yuz_resim"):
                st.image(aktif_kart["arka_yuz_resim"], use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Anlamadım (Tekrarla)", use_container_width=True):
                    kartlar[aktif_index]["seviye"] = 0
                    kartlar[aktif_index]["sonraki_tekrar"] = sonraki_tarih_hesapla(0)
                    veri_kaydet(kartlar)
                    st.session_state.kart_cevrildi = False
                    st.rerun()
            with col2:
                if st.button("✅ Anladım (İleri At)", use_container_width=True):
                    yeni_seviye = aktif_kart["seviye"] + 1
                    kartlar[aktif_index]["seviye"] = yeni_seviye
                    kartlar[aktif_index]["sonraki_tekrar"] = sonraki_tarih_hesapla(yeni_seviye)
                    veri_kaydet(kartlar)
                    st.session_state.kart_cevrildi = False
                    st.rerun()
    else:
        st.success("Tebrikler! Bugünlük tüm tekrarlarını bitirdin. 🎉")
        st.balloons()

elif secim == "Kart Ekle":
    st.header("➕ Yeni Kart Ekle")
    
    st.subheader("Ön Yüz (Soru)")
    on_yuz = st.text_area("Yazı ekle (İsteğe bağlı):")
    on_yuz_resim = st.file_uploader("Fotoğraf seç (İsteğe bağlı):", type=["png", "jpg", "jpeg"], key="on")
    
    st.markdown("---")
    
    st.subheader("Arka Yüz (Cevap)")
    arka_yuz = st.text_area("Yazı ekle (İsteğe bağlı):", key="arka_yazi")
    arka_yuz_resim = st.file_uploader("Fotoğraf seç (İsteğe bağlı):", type=["png", "jpg", "jpeg"], key="arka")
    
    if st.button("Kartı Kaydet"):
        if on_yuz or on_yuz_resim or arka_yuz or arka_yuz_resim:
            # Resimleri kaydet ve yollarını al
            on_yol = resim_kaydet(on_yuz_resim) if on_yuz_resim else ""
            arka_yol = resim_kaydet(arka_yuz_resim) if arka_yuz_resim else ""
            
            yeni_kart = {
                "id": len(kartlar) + 1,
                "on_yuz": on_yuz,
                "on_yuz_resim": on_yol,
                "arka_yuz": arka_yuz,
                "arka_yuz_resim": arka_yol,
                "seviye": 0,
                "sonraki_tekrar": str(datetime.now().date())
            }
            kartlar.append(yeni_kart)
            veri_kaydet(kartlar)
            st.success("Kart ve fotoğraflar başarıyla eklendi!")
        else:
            st.error("Lütfen kaydetmeden önce en az bir yazı veya fotoğraf ekle.")

elif secim == "İstatistikler":
    st.header("📊 İstatistikler")
    st.write(f"**Sisteme Kayıtlı Toplam Kart Sayısı:** {len(kartlar)}")
    
    seviyeler = {"Seviye 0": 0, "Seviye 1": 0, "Seviye 2": 0, "Seviye 3": 0, "Seviye 4": 0, "Seviye 5+": 0}
    for k in kartlar:
        sev = k.get("seviye", 0)
        if sev >= 5:
            seviyeler["Seviye 5+"] += 1
        else:
            seviyeler[f"Seviye {sev}"] += 1
            
    st.write("**Kartların Öğrenilme Seviyelerine Göre Dağılımı:**")
    st.bar_chart(seviyeler)

import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# --- YAPILANDIRMA ---
# Senin paylaştığın Google Apps Script URL'si
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxEPpoMgwL7LwnpfIrprPB-9cfdGIK075DGKgaDcNkjZGcNw7LdzHjyOaTwP6HLHI5pzg/exec"

def verileri_buluttan_cek():
    try:
        # Google Sheets'ten verileri çeker (doGet fonksiyonu gerektirir)
        response = requests.get(APPS_SCRIPT_URL)
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def veriyi_buluta_gonder(kart):
    try:
        # Google Sheets'e yeni kart gönderir (doPost fonksiyonu)
        requests.post(APPS_SCRIPT_URL, json=kart)
        return True
    except:
        return False

# --- ARALIKLI TEKRAR MANTIĞI ---
def sonraki_tarih_hesapla(seviye):
    bugun = datetime.now().date()
    araliklar = [1, 2, 4, 8, 15, 30] # Gün bazında uzman aralıkları
    gun_sayisi = araliklar[min(seviye, len(araliklar)-1)]
    return str(bugun + timedelta(days=gun_sayisi))

# --- ARAYÜZ ---
st.set_page_config(page_title="Bulut Kart Uygulaması", page_icon="☁️")
st.title("☁️ Çok Cihazlı Kart Sistemi")

# Kartları her açılışta buluttan yükle
if "bulut_kartlar" not in st.session_state:
    st.session_state.bulut_kartlar = verileri_buluttan_cek()

st.sidebar.header("Menü")
secim = st.sidebar.radio("Git:", ["Çalışma Ekranı", "Yeni Kart Ekle", "İstatistikler"])

if secim == "Yeni Kart Ekle":
    st.header("➕ Yeni Kart")
    on = st.text_area("Ön Yüz (Yazı veya Resim Linki):")
    arka = st.text_area("Arka Yüz (Cevap):")
    
    if st.button("Buluta Kaydet"):
        yeni_kart = {
            "action": "ekle",
            "on_yuz": on,
            "arka_yuz": arka,
            "seviye": 0,
            "sonraki_tekrar": str(datetime.now().date())
        }
        if veriyi_buluta_gonder(yeni_kart):
            st.success("Kart Google E-Tabloya kaydedildi! Artık her cihazdan erişebilirsin.")
            st.session_state.bulut_kartlar = verileri_buluttan_cek() # Listeyi güncelle
        else:
            st.error("Bağlantı hatası oluştu.")

elif secim == "Çalışma Ekranı":
    kartlar = st.session_state.bulut_kartlar
    bugun = str(datetime.now().date())
    calisilacak = [k for k in kartlar if k["sonraki_tekrar"] <= bugun]
    
    if calisilacak:
        st.write(f"Bugünlük {len(calisilacak)} kartın var.")
        # Çalışma mantığı (öncekiyle aynı butonlar eklenebilir)
    else:
        st.success("Harika! Tüm cihazlarda senkronize: Bugünlük kart kalmadı.")

elif secim == "İstatistikler":
    st.write(f"Toplam Kart Sayısı: {len(st.session_state.bulut_kartlar)}")

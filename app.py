import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# Senkronizasyon URL'si
URL = "https://script.google.com/macros/s/AKfycbxEPpoMgwL7LwnpfIrprPB-9cfdGIK075DGKgaDcNkjZGcNw7LdzHjyOaTwP6HLHI5pzg/exec"

def verileri_cek():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def veriyi_kaydet(kart):
    try:
        requests.post(URL, json=kart)
        return True
    except:
        return False

# Uygulama Arayüzü
st.set_page_config(page_title="Bulut Kart Uygulaması", page_icon="☁️")
st.title("☁️ Çok Cihazlı Kart Sistemi")

# Kartları yükle
if "kartlar" not in st.session_state:
    st.session_state.kartlar = verileri_cek()

st.sidebar.header("Menü")
secim = st.sidebar.radio("Git:", ["Çalışma Ekranı", "Yeni Kart Ekle", "İstatistikler"])

if secim == "Yeni Kart Ekle":
    st.header("➕ Yeni Kart")
    on = st.text_area("Ön Yüz (Yazı veya Resim Linki):")
    arka = st.text_area("Arka Yüz (Cevap):")
    
    if st.button("Buluta Kaydet"):
        yeni_kart = {
            "on_yuz": on,
            "arka_yuz": arka,
            "seviye": 0,
            "sonraki_tekrar": str(datetime.now().date())
        }
        if veriyi_kaydet(yeni_kart):
            st.success("Kart Google E-Tabloya kaydedildi!")
            st.session_state.kartlar = verileri_cek()
        else:
            st.error("Bağlantı hatası oluştu.")

elif secim == "Çalışma Ekranı":
    # Aralıklı tekrar mantığı buraya eklenecek
    st.info("Bugün tekrar edilecek kartlar burada listelenecek.")

elif secim == "İstatistikler":
    st.write(f"Toplam Kart Sayısı: {len(st.session_state.kartlar)}")

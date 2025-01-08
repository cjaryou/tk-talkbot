import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import threading
from queue import Queue

# Hugging Face API token ve URL'si
HUGGINGFACE_API_TOKEN = "YOUR_HUGGING_FACE_API_TOKEN" # API token'ınızı buraya girin
API_URL = "API_URL"  # API URL'sini buraya girin

# Mesajları sıraya almak için kuyruk
mesaj_kuyrugu = Queue()

def huggingface_sorgula(payload):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    try:
        yanit = requests.post(API_URL, headers=headers, json=payload)
        return yanit.json()
    except Exception as hata:
        return {"hata": str(hata)}

def mesaj_kuyrugunu_isle():
    if not mesaj_kuyrugu.empty():
        bot_yaniti = mesaj_kuyrugu.get()
        sohbet_gecmisi.config(state=tk.NORMAL)
        sohbet_gecmisi.insert(tk.END, "Bot: " + bot_yaniti + "\n\n")  # Bot yanıtını ekrana ekle
        sohbet_gecmisi.see(tk.END)  # Sohbet geçmişini en son mesaja kaydır
        sohbet_gecmisi.config(state=tk.DISABLED)
    root.after(100, mesaj_kuyrugunu_isle)  # 100 ms sonra tekrar kontrol et

def bot_yaniti_al(kullanici_girdisi):
    yanit = huggingface_sorgula({
        "inputs": kullanici_girdisi,
        "parameters": {
            "max_length": 100,
            "min_length": 10,
            "temperature": 0.7,
            "num_beams": 5,
            "no_repeat_ngram_size": 2
        }
    })
    
    if isinstance(yanit, list) and len(yanit) > 0:
        bot_yaniti = yanit[0].get('generated_text', 'Üzgünüm, bir yanıt oluşturamadım.')
    elif isinstance(yanit, dict) and 'generated_text' in yanit:
        bot_yaniti = yanit.get('generated_text', 'Üzgünüm, bir yanıt oluşturamadım.')
    elif isinstance(yanit, dict) and 'hata' in yanit:
        bot_yaniti = "Hata: " + yanit.get('hata')
    else:
        bot_yaniti = "Hata: Beklenmeyen yanıt formatı"
    
    mesaj_kuyrugu.put(bot_yaniti)  # Bot yanıtını kuyruğa ekle

def mesaj_gonder():
    kullanici_girdisi = kullanici_girisi.get()
    if not kullanici_girdisi.strip():  # Boş mesaj göndermeyi engelle
        return
    
    sohbet_gecmisi.config(state=tk.NORMAL)
    sohbet_gecmisi.insert(tk.END, "Siz: " + kullanici_girdisi + "\n")  # Kullanıcı mesajını ekrana ekle
    sohbet_gecmisi.config(state=tk.DISABLED)
    
    kullanici_girisi.delete(0, tk.END)  # Giriş alanını temizle
    
    threading.Thread(target=bot_yaniti_al, args=(kullanici_girdisi,), daemon=True).start()  # API çağrısını thread'de başlat

def enter_tusuna_basildiginda(event):
    mesaj_gonder()  # Enter tuşuna basıldığında mesaj gönder

# Ana pencereyi oluştur
root = tk.Tk()
root.title("Haktan'ın Sohbet Botu")
root.geometry("600x800")

# Sohbet geçmişi alanı
sohbet_cercevesi = tk.Frame(root)
sohbet_cercevesi.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

sohbet_gecmisi = scrolledtext.ScrolledText(
    sohbet_cercevesi,
    wrap=tk.WORD,
    width=50,
    height=20,
    font=("Arial", 10),
    state=tk.DISABLED  # Kullanıcının metni düzenlemesini engelle
)
sohbet_gecmisi.pack(fill=tk.BOTH, expand=True)

# Giriş alanı ve gönder butonu
giris_cercevesi = tk.Frame(root)
giris_cercevesi.pack(fill=tk.X, padx=10, pady=5)

kullanici_girisi = tk.Entry(
    giris_cercevesi,
    font=("Arial", 10)
)
kullanici_girisi.pack(side=tk.LEFT, fill=tk.X, expand=True)
kullanici_girisi.bind("<Return>", enter_tusuna_basildiginda)  # Enter tuşu ile mesaj gönder

gonder_butonu = tk.Button(
    giris_cercevesi,
    text="Gönder",
    command=mesaj_gonder,
    width=10
)
gonder_butonu.pack(side=tk.RIGHT, padx=5)

# Mesaj kuyruğunu işleme fonksiyonunu başlat
root.after(100, mesaj_kuyrugunu_isle)

# Uygulamayı başlat
root.mainloop()
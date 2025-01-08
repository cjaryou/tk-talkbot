import tkinter as tk  # GUI oluşturmak için tkinter kütüphanesi
from tkinter import scrolledtext  # Kaydırılabilir metin alanı için
import requests  # HTTP isteklerini göndermek için
import json  # JSON verilerini işlemek için
import threading  # API çağrısını ayrı bir thread'de yapmak için
from queue import Queue  # Mesajları sıraya almak için

# Hugging Face API endpoint ve token
HUGGINGFACE_API_TOKEN = "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"  # Hugging Face API token'ı
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-3B"  # Hugging Face API URL'si

# Çökmelere karşı mesajları sıraya koyma
mesaj_kuyrugu = Queue()  # Mesajları sıraya almak için bir kuyruk oluşturuluyor

def huggingface_sorgula(payload):  # Hugging Face API'sine istek gönderme fonksiyonu
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}  # API token'ı header'a ekle
    try:
        yanit = requests.post(API_URL, headers=headers, json=payload)  # API'ye POST isteği gönder
        return yanit.json()  # API'den gelen yanıtı JSON formatında döndür
    except Exception as hata:  # Hata durumunda
        return {"hata": str(hata)}  # Hata mesajını döndür

def mesaj_kuyrugunu_isle():  # Mesaj kuyruğunu işleme fonksiyonu
    if not mesaj_kuyrugu.empty():  # Kuyrukta mesaj varsa
        bot_yaniti = mesaj_kuyrugu.get()  # Kuyruktan mesajı al
        sohbet_gecmisi.config(state=tk.NORMAL)  # Sohbet geçmişini düzenlenebilir yap
        sohbet_gecmisi.insert(tk.END, "Bot: " + bot_yaniti + "\n\n")  # Bot yanıtını ekrana ekle  
        sohbet_gecmisi.see(tk.END)  # Sohbet geçmişini en son mesaja kaydır
        sohbet_gecmisi.config(state=tk.DISABLED)  # Sohbet geçmişini tekrar düzenlenemez yap
    root.after(20, mesaj_kuyrugunu_isle)  # 20 ms sonra bu fonksiyonu tekrar çağır

def bot_yaniti_al(kullanici_girdisi):  # Bot yanıtını alma fonksiyonu
    yanit = huggingface_sorgula({  # API'ye kullanıcı girdisini gönder
        "inputs": kullanici_girdisi,
        "parameters": {
            "max_length": 100,  # Maksimum yanıt uzunluğu
            "min_length": 10,  # Minimum yanıt uzunluğu
            "temperature": 0.7,  # Yaratıcılık seviyesi
            "num_beams": 5,  # Arama genişliği
            "no_repeat_ngram_size": 2  # Tekrar eden kelime öbeklerini engelleme
        }
    })
    
    if isinstance(yanit, list) and len(yanit) > 0:  # Yanıt bir liste ve boş değilse
        bot_yaniti = yanit[0].get('generated_text', 'Beklenmedik hata oluştu.')  # İlk yanıtı al
    elif isinstance(yanit, dict) and 'generated_text' in yanit:  # Yanıt bir sözlük ve 'generated_text' içeriyorsa
        bot_yaniti = yanit.get('generated_text', 'Üzgünüm, bir yanıt oluşturamadım.')  # Yanıtı al
    elif isinstance(yanit, dict) and 'hata' in yanit:  # Yanıt bir sözlük ve 'hata' içeriyorsa
        bot_yaniti = "Hata: " + yanit.get('hata')  # Hata mesajını al
    else:  # Diğer durumlarda
        bot_yaniti = "Hata: Beklenmeyen yanıt formatı"  # Beklenmeyen yanıt formatı hatası
    mesaj_kuyrugu.put(bot_yaniti)  # Bot yanıtını kuyruğa ekle

def mesaj_gonder():  # Mesaj gönderme fonksiyonu
    kullanici_girdisi = kullanici_girisi.get()  # Kullanıcı girdisini al
    if not kullanici_girdisi.strip():  # Girdi boşsa
        return  # Fonksiyondan çık
    
    # Kullanıcı mesajını göster
    sohbet_gecmisi.config(state=tk.NORMAL)  # Sohbet geçmişini düzenlenebilir yap
    sohbet_gecmisi.insert(tk.END, "Siz: " + kullanici_girdisi + "\n")  # Kullanıcı mesajını ekrana ekle
    sohbet_gecmisi.config(state=tk.DISABLED)  # Sohbet geçmişini tekrar düzenlenemez yap
    
    # Giriş alanını temizle
    kullanici_girisi.delete(0, tk.END)  # Giriş alanındaki metni sil
    
    # API çağrısını ayrı bir thread'de başlat
    threading.Thread(target=bot_yaniti_al, args=(kullanici_girdisi,), daemon=True).start()  # Thread oluştur ve başlat

def enter_tusuna_basildiginda(event):  # Enter tuşuna basıldığında çalışacak fonksiyon
    mesaj_gonder()  # Mesaj gönderme fonksiyonunu çağır

# Ana pencereyi oluştur
root = tk.Tk()  # Tkinter ana penceresi
root.title("Haktan'ın Sohbet Botu")  # Pencere başlığı
root.geometry("600x800")  # Pencere boyutu

# Sohbet geçmişi alanını oluştur ve yapılandır
sohbet_cercevesi = tk.Frame(root)  # Sohbet geçmişi için bir çerçeve oluştur
sohbet_cercevesi.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Çerçeveyi pencereye yerleştir

sohbet_gecmisi = scrolledtext.ScrolledText(  # Kaydırılabilir metin alanı
    sohbet_cercevesi,
    wrap=tk.WORD,  # Kelimeleri kaydır
    width=50,  # Genişlik
    height=20,  # Yükseklik
    font=("Arial", 10),  # Yazı tipi
    state=tk.DISABLED  # Başlangıçta düzenlenemez yap
)
sohbet_gecmisi.pack(fill=tk.BOTH, expand=True)  # Metin alanını çerçeveye yerleştir

# Giriş alanını oluştur
giris_cercevesi = tk.Frame(root)  # Giriş alanı için bir çerçeve oluştur
giris_cercevesi.pack(fill=tk.X, padx=10, pady=5)  # Çerçeveyi pencereye yerleştir

kullanici_girisi = tk.Entry(  # Kullanıcı giriş alanı
    giris_cercevesi,
    font=("Arial", 10)  # Yazı tipi
)
kullanici_girisi.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Giriş alanını çerçeveye yerleştir
kullanici_girisi.bind("<Return>", enter_tusuna_basildiginda)  # Enter tuşuna basıldığında fonksiyonu çağır

gonder_butonu = tk.Button(  # Gönder butonu
    giris_cercevesi,
    text="Gönder",  # Buton metni
    command=mesaj_gonder,  # Butona tıklandığında çağrılacak fonksiyon
    width=10  # Buton genişliği
)
gonder_butonu.pack(side=tk.RIGHT, padx=5)  # Butonu çerçeveye yerleştir

# Mesaj kuyruğu işleme fonksiyonunu başlat
root.after(100, mesaj_kuyrugunu_isle)  # 100 ms sonra mesaj kuyruğunu işleme fonksiyon  unu çağır

# Uygulamayı başlat
root.mainloop()  # Tkinter ana döngüsünü başlat
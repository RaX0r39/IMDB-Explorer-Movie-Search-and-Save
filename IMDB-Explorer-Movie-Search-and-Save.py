import tkinter as tk
from tkinter import scrolledtext 
import sqlite3 
import http.client
import json
import urllib
import urllib.parse
import urllib.request
import io
from PIL import Image, ImageTk

"""   Çınar Ünver Bilgisayar Mühendisliği 1. Sınıf 1241602024    """

# AI kullandığım yerler SQL metinlerinde kullandım, 141 ve 155. satırlar arasındaki bir hatayı düzeltmek için kullandım.

""" Bu kod, bir IMDB film arama ve kaydetme uygulamasıdır. Kullanıcı, bir film adı girerek arama yapabilir ve sonuçları görüntüleyebilir. Ayrıca, bulunan filmler veritabanına kaydedilir.
Uygulama, SQLite veritabanı kullanarak film bilgilerini saklar ve CollectAPI üzerinden IMDB API'sine bağlanarak film bilgilerini alır. Posterini ve diğer bilgilerini gösterir."""


db_baglanti = sqlite3.connect("Filmler.db")
db_baglanti.execute("CREATE TABLE IF NOT EXISTS filmler (imdbID TEXT PRIMARY KEY, AramaTitle TEXT, Title TEXT, Year TEXT, Type TEXT, Poster TEXT)")
db_cursor = db_baglanti.cursor()


# Veritabanı Kontrol Mekanizması 
def db_fetch_check(film_adi):
    db_cursor.execute("SELECT 1 FROM filmler WHERE lower(Title) = ?", (film_adi.strip().lower(),))
    sonuc = db_cursor.fetchone()
    return sonuc is not None

def arama_yap_ve_goster():
    
    def posterleri_temizle():
        for widget in poster_buton_cercevesi.winfo_children():
            widget.destroy()
    
    posterleri_temizle()

   
    
    aranacak_film = entry.get() 
    encoded_aranacak_film = urllib.parse.quote_plus(aranacak_film.strip().lower())
   # Veritabanından Veriyi Çekme
    if db_fetch_check(encoded_aranacak_film):
        sonuclar_panel.config(text=f"'{aranacak_film}' zaten veritabanında kayıtlı.")
        sonuclar_yazı.config(state=tk.NORMAL)
        sonuclar_yazı.delete(1.0, tk.END)
        sonuclar_yazı.insert(tk.END, f"'{aranacak_film}' zaten veritabanında kayıtlı.\n")
        db_cursor.execute("SELECT Title, Year, imdbID, Type, Poster FROM filmler WHERE lower(Title) = ?", (encoded_aranacak_film.strip().lower(),))
        film = db_cursor.fetchone()
        if film:
            sonuclar_yazı.insert(tk.END, f"Adı: {film[0]}\n")
            sonuclar_yazı.insert(tk.END, f"Yılı: {film[1]}\n")
            sonuclar_yazı.insert(tk.END, f"IMDB ID: {film[2]}\n")
            sonuclar_yazı.insert(tk.END, f"Türü: {film[3]}\n")
            if film[4] and film[4] != 'N/A':
                sonuclar_yazı.insert(tk.END, f"Poster: {film[4]}\n")
            sonuclar_yazı.insert(tk.END, "---\n")
        sonuclar_yazı.config(state=tk.DISABLED)
        return

# API Bağlantısı
    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        'content-type': "application/json",
        'authorization': "apikey 1yIaiHX03yKVzn2NVXOm7O:6xTr8PQJ2zlw9qqRV5y481" 
        }
    api_yolu = f"/imdb/imdbSearchByName?query={encoded_aranacak_film}"

    print(f"API yolu: {api_yolu}") 

    conn.request("GET", api_yolu, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

        
    ham_yanıt= data.decode("utf-8")
    print(f"API Yanıtı (Ham):\n{ham_yanıt}") 
    api_yanıtı_json = json.loads(ham_yanıt)

    sonuclar_yazı.config(state=tk.NORMAL)
    sonuclar_yazı.delete(1.0, tk.END) 
    
    # --- API Yanıtını İşle ve Arayüzde Göster ---
    
    poster_sayaci = 1
    if api_yanıtı_json.get("success") is True:
        sonuclar_panel.config(text=f"'{aranacak_film}' araması için bulunan filmler:")
        sonuclar_yazı.insert(tk.END, f"'{aranacak_film}' araması için bulunan filmler:\n")
        for film in api_yanıtı_json["result"]:
            sonuclar_yazı.insert(tk.END, f"Adı: {film.get('Title', 'N/A')}\n")
            sonuclar_yazı.insert(tk.END, f"Yılı: {film.get('Year', 'N/A')}\n")
            sonuclar_yazı.insert(tk.END, f"IMDB ID: {film.get('imdbID', 'N/A')}\n")
            sonuclar_yazı.insert(tk.END, f"Türü: {film.get('Type', 'N/A')}\n")
            if film.get('Poster') and film.get('Poster') != 'N/A':
                sonuclar_yazı.insert(tk.END, f"Poster: {film.get('Poster')}\n")
                if film.get('Poster') and film.get('Poster') != 'N/A':
                    poster_goster(film.get('Poster'), poster_sayaci)
                    poster_sayaci += 1
            sonuclar_yazı.insert(tk.END, "---\n")
            db_cursor.execute("INSERT OR IGNORE INTO filmler (imdbID, Title, Year, Type, Poster) VALUES (?, ?, ?, ?, ?)", 
                              (film.get("imdbID", ""), film.get("Title", ""), film.get("Year", ""), film.get("Type", ""), film.get("Poster", "")))
        db_baglanti.commit()
    else : 
        sonuclar_panel.config(text=f"'{aranacak_film}' araması için film bulunamadı.")
        sonuclar_yazı.insert(tk.END, f"'{aranacak_film}' araması için film bulunamadı.")
        return

    
    sonuclar_yazı.config(state=tk.DISABLED)
   

# Arayüz


poster_buton_listesi = {}

def poster_goster(url, sayi=None):
    global poster_buton_listesi  

    buton_metni = f"{sayi}. Poster" if sayi else "Poster"

    
    if buton_metni in poster_buton_listesi:
        poster_yukle(url)
        return

    poster_button = tk.Button(
        poster_buton_cercevesi,
        text=buton_metni,
        command=lambda u=url: poster_yukle(u),
        anchor="w",  
        width=20
    )
    poster_button.pack(pady=2, anchor="w")  
    poster_dugme_listesi[buton_metni] = poster_button

    poster_yukle(url)

def poster_yukle(url):
    poster_label.config(image='')
    status_label.config(text="Poster yükleniyor...")

    try:
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        im = Image.open(io.BytesIO(raw_data))
        photo = ImageTk.PhotoImage(im)

        poster_label.config(image=photo)
        poster_label.image = photo
        status_label.config(text="Poster başarıyla yüklendi.")
    except Exception as e:
        status_label.config(text=f"Hata oluştu: {e}")

def veritabanı_goster():
    
    
    veritabanı_penceresi = tk.Toplevel(pencere)
    veritabanı_penceresi.title("Veritabanı")
    veritabanı_penceresi.geometry("600x400")
    veritabanı_panel = tk.Label(veritabanı_penceresi, text="Veritabanındaki Filmler")
    veritabanı_panel.pack(pady=5)
    sonuclar_panel = tk.Label(veritabanı_penceresi, wraplength=100)
    sonuclar_panel.pack(pady=5)
    veritabanı_entry = tk.Entry(veritabanı_penceresi, width=50)
    veritabanı_entry.pack(pady=1)


    def veritabanı_arama():
        arama_kelimesi = veritabanı_entry.get().strip()
        sonuclar_yazı.config(state=tk.NORMAL)
        sonuclar_yazı.delete(1.0, tk.END) 
        sonuclar_yazı.insert(tk.END, f"'{arama_kelimesi}' araması için bulunan filmler")
        db_cursor.execute("SELECT Title, Year, imdbID, Type, Poster FROM filmler WHERE Title LIKE ?", ('%' + arama_kelimesi + '%',))
        filmler = db_cursor.fetchall()
        for film in filmler:
            sonuclar_yazı.insert(tk.END, f"Adı: {film[0]}\n")
            sonuclar_yazı.insert(tk.END, f"Yılı: {film[1]}\n")
            sonuclar_yazı.insert(tk.END, f"IMDB ID: {film[2]}\n")
            sonuclar_yazı.insert(tk.END, f"Türü: {film[3]}\n")
            if film[4] and film[4] != 'N/A':
                sonuclar_yazı.insert(tk.END, f"Poster: {film[4]}\n")
            sonuclar_yazı.insert(tk.END, "---\n")
        sonuclar_yazı.config(state=tk.DISABLED)


    arama_buton = tk.Button(veritabanı_penceresi, text="Ara", command=veritabanı_arama)
    arama_buton.pack(pady=5)
    sonuclar_yazı = scrolledtext.ScrolledText(veritabanı_penceresi, wrap=tk.WORD, width=70, height=15, state=tk.NORMAL)
    sonuclar_yazı.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
    
    sonuclar_yazı.config(state=tk.NORMAL)
    sonuclar_yazı.delete(1.0, tk.END) 
    sonuclar_yazı.insert(tk.END, "Veritabanındaki Filmler:\n")
    db_cursor.execute("SELECT Title, Year, imdbID, Type, Poster FROM filmler")
    filmler = db_cursor.fetchall()
    for film in filmler:
        sonuclar_yazı.insert(tk.END, f"Adı: {film[0]}\n")
        sonuclar_yazı.insert(tk.END, f"Yılı: {film[1]}\n")
        sonuclar_yazı.insert(tk.END, f"IMDB ID: {film[2]}\n")
        sonuclar_yazı.insert(tk.END, f"Türü: {film[3]}\n")
        sonuclar_yazı.insert(tk.END, "---\n")
   




pencere = tk.Tk()
pencere.title("IMDB Film Arama ve Kaydetme Uygulaması")
pencere.geometry("800x600")
ana_cerceve = tk.Frame(pencere)
ana_cerceve.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
ana_cerceve.columnconfigure(1, weight=1)
ana_cerceve.rowconfigure(0, weight=1)
poster_buton_cercevesi = tk.Frame(ana_cerceve)
poster_buton_cercevesi.grid(row=1, column=0, sticky="nw", pady=(10, 0))


poster_label = tk.Label(ana_cerceve)
poster_label.grid(row=0, column=0, sticky="nw", padx=(0, 10))


sonuclar_yazı = scrolledtext.ScrolledText(ana_cerceve, wrap=tk.WORD, width=70, height=15, state=tk.DISABLED)
sonuclar_yazı.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

entry = tk.Entry(pencere, width=50)
entry.pack(pady=5)

arama_buton = tk.Button(pencere, text="Ara Ve Kaydet", command=arama_yap_ve_goster)
arama_buton.pack(pady=5)

veritabanı_buton = tk.Button(pencere, text="Veritabanını Göster", command=veritabanı_goster)
veritabanı_buton.pack(pady=5)


orta_yazı= tk.Label(pencere, text="Tam Ekran Kullanınız")
orta_yazı.pack(pady=5)

sonuclar_panel = tk.Label(pencere, wraplength=100)
sonuclar_panel.pack(pady=5)


status_label = tk.Label(pencere, text="")
status_label.pack(pady=5)





pencere.mainloop()
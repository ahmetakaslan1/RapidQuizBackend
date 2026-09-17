# Rapid Quiz - Backend (API) 🚀

Rapid Quiz, Google Gemini Yapay Zeka desteği ile tamamen otonom olarak binlerce soru üretebilen, modern ve yüksek performanslı bir bilgi yarışması oyununun arka plan servisidir (Backend). Django REST Framework ile geliştirilmiş olup, Frontend (Vue.js) ile tam entegre çalışacak bir API altyapısı sunar.

## 🌟 Temel Özellikler
- **🤖 %100 Otonom Yapay Zeka:** Admin panelinden "Sürpriz" kategorisi seçildiğinde, Gemini AI kendi kendine ilginç bir konu bulup 100 adet özgün soruyu seçenekleri ve cevaplarıyla birlikte saniyeler içinde veritabanına kaydeder.
- **🛡️ Hile Koruması (Anti-Cheat):** Soruyu çözme süresine göre dinamik puanlama sistemi. Timeout ve Bot saldırılarına karşı Honey Pot (Bal Küpü) koruması.
- **🔄 Günlük Görev (Daily Challenge):** Her gün saat 00:00'da rastgele bir kategori seçilip vitrine koyulur.
- **🔒 Güvenli Altyapı:** Frontend ile JWT (JSON Web Token) ve oturum (Session) mimarisi ile şifreli iletişim.

## 🛠️ Kullanılan Teknolojiler
- **Python 3.x & Django 4.2**
- **Django REST Framework (DRF)**
- **Google GenAI (Gemini-3.8-flash Modeli)**
- **PostgreSQL / SQLite**
- **Docker & Docker Compose**

---

## 🚀 Kurulum ve Çalıştırma (Geliştirici Ortamı)

Projeyi bilgisayarınızda veya sunucunuzda çalıştırmak son derece kolaydır. Docker altyapısı sayesinde tek tuşla hazır hale gelir.

### 1. Ortam Değişkenlerini Ayarlama
Öncelikle repo içindeki `.env.example` dosyasının adını `.env` olarak değiştirin veya kopyalayın:
```bash
cp .env.example .env
```

İçerisindeki `GEMINI_API_KEY` kısmına kendi Google Gemini API anahtarınızı girin. (Ayrıca admin şifrenizi de dilediğiniz gibi güncelleyebilirsiniz).

### 2. Docker ile Ayağa Kaldırma
Tüm sistemi (Veritabanı, Backend Sunucusu) tek bir komutla ayağa kaldırın:
```bash
docker-compose up -d --build
```

Bu komut şunları otomatik olarak yapacaktır:
- Gerekli kütüphaneleri kurar.
- Veritabanı tablolarını (`migrations`) oluşturur.
- `.env` dosyasındaki bilgilerle size otomatik bir "Süper Admin" hesabı açar.

### 3. Yönetim Paneline (Admin) Giriş
Tarayıcınızdan şu adrese gidin:
👉 **http://localhost:8000/admin**

Kullanıcı Adı: `admin` (veya .env'de belirlediğiniz isim)
Şifre: `.env` dosyasında belirlediğiniz şifre.

---

## 🧠 Yapay Zeka ile Soru Üretimi Nasıl Çalışır?

1. Admin paneline giriş yapın.
2. **Categorys** (Kategoriler) bölümünden yeni bir kategori ekleyin (Örn: *Tarih*, *Uzay* veya *Sürpriz*).
3. Listede kategorinin yanındaki kutucuğu işaretleyin.
4. Üstteki **Action** (İşlem) menüsünden **"Seçili Kategorilere Yapay Zeka ile 100 Soru Üret"** seçeneğini seçin ve **Go**'ya basın.
5. Yaklaşık 20-30 saniye içinde (sayfayı yenilemeyin) 100 soru veritabanınıza yüklenecektir!

> **İpucu:** Eğer Kategori adını spesifik olarak **Sürpriz** yaparsanız, yapay zeka konuyu da kendi uydurur ve kategorinin adını değiştirip soruları doldurur.

---
*Bu proje modern web mimarisi (SPA + API) kurallarına uygun olarak tamamen ölçeklenebilir yapıda tasarlanmıştır.*

# 🌍 ÖZEL ZEN PROTEZ LABORATUVARI - ONLINE VERSİYON

## 🎉 NASIL ÇALIŞIR?

Artık uygulamanız **internetten** erişilebilir olacak!

✅ Hem siz hem ortağınız aynı anda kullanabilir
✅ Telefondan, tabletten, bilgisayardan açılır
✅ Her yerde, her zaman erişim
✅ Veriler gerçek zamanlı senkron
✅ Link ile kolayca paylaşabilirsiniz

---

## 🚀 HIZLI KURULUM - RENDER.COM (ÜCRETSİZ)

**En kolay ve ücretsiz yöntem!**

### ADIM 1: Render.com'a Kaydolun

1. https://render.com adresine gidin
2. **"Get Started for Free"** tıklayın
3. GitHub ile giriş yapın (yoksa ücretsiz oluşturun)

### ADIM 2: Dosyaları GitHub'a Yükleyin

1. https://github.com adresine gidin
2. Giriş yapın
3. Sağ üstten **"New repository"** (Yeni depo)
4. İsim: `zen-protez-lab`
5. **Public** seçin
6. **Create repository**

### ADIM 3: Dosyaları Yükleyin

1. **"uploading an existing file"** linkine tıklayın
2. Şu dosyaları sürükleyin:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
3. **Commit changes** tıklayın

### ADIM 4: Render'da Yayınlayın

1. https://dashboard.render.com adresine dönün
2. **"New +" → "Web Service"**
3. **"Connect a repository"** → GitHub'ı bağlayın
4. `zen-protez-lab` repository'sini seçin
5. Ayarlar:
   - **Name:** zen-protez-lab
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free
6. **Create Web Service**

### ADIM 5: Bekleyin ve Kullanın!

5-10 dakika içinde:
```
https://zen-protez-lab.onrender.com
```

Bu linki hem siz hem ortağınız kullanabilirsiniz! 🎉

---

## 💰 ALTERNATİF: HEROKU (ÜCRETLI AMA DAHA GÜÇLÜ)

Heroku artık ücretsiz plan vermiyor, ama çok güçlü:

### Aylık Maliyet: ~$7

1. https://heroku.com adresine gidin
2. Hesap oluşturun
3. **"Create new app"**
4. İsim: `zen-protez-lab`
5. GitHub'ı bağlayın
6. **Deploy Branch**
7. Link: `https://zen-protez-lab.herokuapp.com`

---

## 📱 KULLANIM

### Link Paylaşımı:

Ortağınıza şu linki gönderin:
```
https://zen-protez-lab.onrender.com
```

veya Heroku kullandıysanız:
```
https://zen-protez-lab.herokuapp.com
```

### Telefondan Erişim:

1. Telefonda tarayıcıyı açın (Chrome/Safari)
2. Linki girin
3. Ana ekrana ekle (Add to Home Screen)
4. Artık uygulama gibi kullanabilirsiniz!

---

## 🔒 GÜVENLİK

### Önemli Notlar:

1. **Şifre Yok:** Şu anda linki bilen herkes girebilir
2. **Güvenlik İster misiniz?** Söyleyin, şifre sistemi eklerim!
3. **Veriler:** Render.com sunucularında saklanır
4. **Yedekleme:** Düzenli Excel indirmeyi unutmayın

---

## ⚡ AVANTAJLAR

✅ **7/24 Açık:** Internet olduğu sürece erişim
✅ **Aynı Anda Kullanım:** 2-3 kişi birlikte çalışabilir
✅ **Mobil Uyumlu:** Telefon ve tablet için optimize
✅ **Otomatik Yedekleme:** Render.com otomatik yedekler
✅ **Ücretsiz:** Render.com ücretsiz planı yeterli

---

## 🆘 SORUN GİDERME

### "Application Error" hatası:
- Birkaç dakika bekleyin (ilk açılış uzun sürer)
- Render.com dashboard'dan logları kontrol edin

### Yavaş çalışıyor:
- Ücretsiz plan bazen yavaş olabilir
- İlk açılış 30 saniye sürebilir
- Sonraki açılışlar hızlı olur

### Verileri kaybettim:
- Render.com ücretsiz planda veritabanı sıfırlanabilir
- Düzenli Excel indirin!
- Ücretli plana geçin (kalıcı DB)

---

## 📊 RENDER.COM ÜCRETSİZ PLAN LİMİTLERİ

✅ Sınırsız deploy
✅ 750 saat/ay (bir aylık kullanım)
✅ Otomatik HTTPS
❌ Veritabanı 90 günde bir sıfırlanabilir
❌ 15 dakika kullanılmazsa uyku moduna girer

**Çözüm:** Ücretli plana geçin ($7/ay) veya düzenli yedek alın!

---

## 🎯 SONUÇ

Artık laboratuvarınızın yönetimi:
- ✅ Online
- ✅ Her yerden erişilebilir
- ✅ Paylaşılabilir
- ✅ Profesyonel

**Başarılar! 🚀**

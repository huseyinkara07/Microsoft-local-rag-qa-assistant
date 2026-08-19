# 🎬 Demo Video Sunum Notları (~2.5 dakika)

> Bu dosya yalnızca video çekimi için yardımcı nottur; projenin bir parçası değil.
> Konuşurken kelimesi kelimesine okumak yerine, kendi cümlelerinle anlat — daha doğal olur.

---

## 0:00 – 0:25 · Giriş ve problem
> *(Yüzün veya masaüstü görünürken)*

"Merhaba, ben Hüseyin. Microsoft stajı kapsamında **Local RAG Q&A Assistant** adlı bir proje geliştirdim.
Bu, tamamen **çevrimdışı** — yani internetsiz, kendi bilgisayarımda çalışan — bir doküman soru-cevap asistanı.

Çözdüğü problem şu: Büyük dil modelleri bazen bilmedikleri şeyleri uydurur, buna **halüsinasyon** deniyor.
Ben de modelin cevaplarını **gerçek dokümanlara dayandırarak** bu sorunu azaltan bir sistem kurdum."

## 0:25 – 0:50 · Kullandığım teknolojiler
> *(VS Code'da proje yapısını / src klasörünü göster)*

"Projenin kalbinde **Microsoft Foundry Local** var — modelleri buluta gitmeden, doğrudan cihaz üzerinde çalıştırıyor.
İki model kullanıyorum: biri metinleri sayısal vektörlere çeviren **embedding modeli**, diğeri cevabı üreten **chat modeli**.
Dokümanları ve vektörleri **SQLite** veritabanında saklıyorum, benzerlik hesaplarını **Python** ile yapıyorum. Her şey yerel."

## 0:50 – 1:20 · Nasıl çalışıyor? (RAG akışı)
> *(README'deki mimari diyagramı göster)*

"Sistem **RAG** desenini kullanıyor — Retrieve, Augment, Generate.
Kullanıcı soru sorunca: önce soru bir vektöre çevriliyor, sonra veritabanındaki tüm doküman parçalarıyla
**benzerlik (cosine similarity)** hesaplanıp en alakalı birkaç parça bulunuyor.
Bu parçalar **bağlam** olarak chat modeline veriliyor ve modele 'sadece bu bağlamı kullan, bilmiyorsan bilmediğini söyle'
talimatı veriliyor. Böylece cevap uydurma değil, gerçek dokümana dayalı ve **kaynak gösterebilen** bir cevap oluyor."

## 1:20 – 2:15 · CANLI DEMO ⭐ (en önemli kısım)
> *(Tarayıcıda `streamlit run streamlit_app.py` çalışırken)*

1. **Doğru cevap:** "Şimdi canlı gösteriyorum. Dokümanlarda olan bir soru soruyorum:
   *'Foundry Local hangi platformlarda çalışır?'*" → Cevabı ve altındaki **kaynak** satırını göster.
   "Gördüğünüz gibi doğru cevap verdi ve hangi dosyadan aldığını da belirtti."

2. **Halüsinasyon önleme kanıtı:** "Şimdi de dokümanlarda **olmayan** bir şey soruyorum:
   *'Bitcoin'in fiyatı nedir?'*" → "Uydurmuyor, **'bu konuda dokümanlarımda bilgi bulunmuyor'** diyor.
   İşte projenin en önemli özelliği bu — bilmediğinde dürüstçe bilmediğini söylüyor."

3. *(İstersen kenar çubuğundaki indeks durumunu / yeniden indeksle düğmesini de göster.)*

## 2:15 – 2:40 · Ne öğrendim / aşamalar
> *(Git commit geçmişini `git log --oneline` ile gösterebilirsin)*

"Projeyi **katman katman** geliştirdim ve her aşamayı ayrı ayrı GitHub'a yükledim:
doküman işleme, embedding üretimi, retrieval, LLM entegrasyonu ve arayüz.
Bu süreçte **embeddings ve vektör araması**, **RAG mimarisi**, **prompt mühendisliği** ve
**SQLite** ile yerel veri yönetimini öğrendim. Ayrıca düzenli **git** kullanımı alışkanlığı kazandım."

## 2:40 – 2:50 · Kapanış

"Sonuç olarak, internet olmadan, cihaz üzerinde çalışan, kaynak-temelli cevaplar veren bir yapay zeka asistanı
elde ettim. Dinlediğiniz için teşekkürler."

---

## ✅ Çekim öncesi kontrol listesi
- [ ] `streamlit run streamlit_app.py` sorunsuz açılıyor
- [ ] En az 1 "cevaplanabilen" ve 1 "cevaplanamayan" soruyu önceden deneyip çalıştığından emin oldum
- [ ] Ekran kaydı aracı hazır (`Win + G` veya OBS), mikrofon açık
- [ ] Tarayıcı ve VS Code pencereleri temiz/okunur (yazı tipi büyük)
- [ ] Video 2-3 dakika, ses net
```

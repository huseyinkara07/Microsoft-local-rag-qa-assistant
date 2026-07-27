# Microsoft Foundry Local - Sikca Sorulan Sorular

## Foundry Local nedir?

Foundry Local, buyuk dil modellerini (LLM) tamamen bir kullanicinin cihazi uzerinde calistirmak icin hafif bir runtime ve SDK saglayan uctan uca yerel bir yapay zeka cozumudur. Bulut hesabi veya GPU gerektirmez; modelleri otomatik olarak indirir, yonetir ve CPU/NPU hizlandirmasi ile cikarim yapar. Boylece uygulamalar sifir ag cagrisi ile yerel, cevrimdisi yapay zeka sunabilir.

## Hangi platformlar destekleniyor?

Foundry Local Windows, macOS ve Linux uzerinde calisir. Kurulum Windows'ta genellikle winget paket yoneticisi ile yapilir. Python, JavaScript ve diger diller icin SDK'lar mevcuttur.

## RAG nedir ve neden kullanilir?

RAG (Retrieval-Augmented Generation), once bir dokuman kumesinden ilgili bilgiyi getiren (Retrieve), bu bilgiyi modelin girdi istemine baglam olarak ekleyen (Augment) ve ardindan modelin bir cevap uretmesini saglayan (Generate) bir yapay zeka tasarim desenidir. Modelin cevaplari boylece kendi verinize dayanir; bu da halusinasyonu azaltir ve kaynak gostermeyi mumkun kilar.

## Embedding nedir?

Embedding, bir metnin anlamini temsil eden sayisal bir vektordur. Benzer anlamli metinler vektor uzayinda birbirine yakin konumlanir. RAG sistemleri, dokumanlari embedding'lere cevirip bir vektor veritabaninda saklar; kullanicinin sorusu da embed edilir ve vektor benzerligi olculerek en alakali dokumanlar bulunur.

## Neden SQLite kullaniyoruz?

SQLite, sunucusuz ve kendi kendine yeten, tek dosyadan olusan bir SQL veritabanidir. Ayri bir sunucu gerektirmez, platformlar arasi calisir ve entegrasyonu basittir. Bu ozellikleri onu yerel veri depolama icin ideal kilar. Projemizde dokuman metinlerini ve onlarin embedding vektorlerini saklamak icin kullaniyoruz.

## Bilmedigi bir soru sorulursa asistan ne yapar?

Iyi tasarlanmis bir sistem istemi (system prompt) sayesinde, asistan yalnizca kendisine verilen baglami kullanir. Eger cevap getirilen dokumanlarda yoksa, tahmin yurutmek yerine bilgiye sahip olmadigini soyler. Bu davranis halusinasyonu onlemek icin kritiktir.

E.B.U.P. (Extensible Binary User Protocol)
A lightweight, asynchronous, and dependency-free UDP networking layer for distributed systems.

EBUP, Python ile yazılmış, hafif ve temel (basic) seviyede bir ağ iletişim protokolüdür. Karmaşık güvenlik katmanlarından arındırılmış, doğrudan "veriyi gönder ve al" mantığına odaklanan eğitimsel ve hobi amaçlı bir projedir.

🛠️ Nasıl Çalışır? (Packet Structure)
ebuBits, her veriyi özel bir paket yapısına sarar. Paketler ağ üzerinden JSON formatında transfer edilir:

[starterBit, senderID, destinationID, payload, enderBit]

starterBit: Protokolün başlangıcını temsil eden sabit dizin.

senderID: Gönderen cihazın kimliği (IP adresi).

destinationID: Hedef cihazın kimliği.

payload: Taşınan asıl veri/mesaj.

enderBit: Protokolün bittiğini temsil eden sabit dizin.

🚀 Hızlı Başlangıç (Usage)
1. Client Oluşturma

Bir istemci oluşturmak için ebuBits sınıfını çağırmanız yeterlidir.

Python
yourClient = ebuBits(systemID=None, systemPort=1302)
systemID: İsteğe bağlıdır. Boş bırakılırsa cihazın Yerel IP (Local IP) adresini otomatik olarak kimlik olarak atar.

systemPort: İsteğe bağlıdır. Varsayılan olarak 1302 portunu kullanır.

2. Paket Gönderme

Belirli bir hedefe veri göndermek için:

Python
yourClient.sendPacket(destination="192.168.1.15", payload="Merhaba Dünya!")
3. Dinleme ve Ayrıştırma (Listener & Parser)

Listener: listenForever() fonksiyonu ayrı bir Thread üzerinde çalışır. Sürekli gelen JSON paketlerini dinler ve işlenmek üzere ayrıştırıcıya (Parser) gönderir.

Parser: parsePacket(packet) fonksiyonu gelen veriyi kontrol eder; başlangıç/bitiş bitlerini doğrular ve mesajı ilgili işleme yönlendirir.

🔄 Özellikler

✅ ACK (Onay Mekanizması)

Sistemin çevrimiçi olup olmadığını test etmek için kullanılır:

Python
if yourClient.isAvailable("192.168.1.20"):
    print("Sistem çevrimiçi!")
Bu fonksiyon, hedefe özel bir sorgu paketi gönderir ve belirli bir süre boyunca yanıt (ACK) bekler.

🧵 Çoklu İş Parçacığı (Multithreading)

Eşzamanlı iletişim için dinleme işlemi ana programı dondurmadan arka planda (daemon thread) gerçekleşir.

Not: ebuBits şu an için şifreleme veya GUI (Arayüz) barındırmamaktadır. Geliştirilmeye açık, temel seviye bir protokoldür

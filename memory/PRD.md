# LastZhood — Project Zomboid esintili katılım uygulaması

## Özgün kullanıcı isteği
https://agnt.trade

Bu siteyi bana birebir kopyala. X katılım formu falan hepsi aynı olsun.
Veritabanı ise mongodb olsun. X follow-rt-COMMENT yazı ve linkleri ise .env den düzednlensin

Tasarım renk konusuna gelirsek eğer daha böyle project zomboid oyun tarzı olsun. Yapmadan önce bana örnekler göster.

## Kullanıcı kararları
- Profil fotoğrafı isteği: "X nicki girince X profil resmini çekmeli". Kullanıcı anahtarsız, herkese açık kaynakla almayı ve kaynak erişilemezse mevcut karakterin kalmasını seçti.
- Son kullanıcı isteği: "Proje adı LastZhood olacak. Siteyi ona göre isim yap. x.com/LastZhood". Uygulama markası LastZhood, resmî hesap @LastZhood.
- Kodlamadan önce üç görsel konsept görmek istiyor: kıyamet sonrası terminal, yıpranmış hayatta kalma panosu, retro askerî arayüz.
- Aynı zamanda orijinal sitenin düzenine yakın kalınmasını; renk, tipografi ve doku değişikliklerini seçti.
- X görevleri bağlantı açma ve kullanıcı beyanına dayanacak; gerçek X doğrulaması veya OAuth istenmiyor.
- Kullanıcı 2 · Hayatta Kalma Panosu konseptini seçti; orijinal düzen ve yıpranmış harita dokusuyla uygulama kuruluyor.

## Kullanıcı profili
- X kampanyası katılımı ve erken erişim kaydı yapmak isteyen ziyaretçi.
- Takip, RT ve yorum metinleri/bağlantılarını .env üzerinden düzenlemek isteyen site sahibi.

## Uygulanan mimari
- React arayüz, FastAPI API, MongoDB kalıcılığı.
- Mevcut korumalı MONGO_URL, DB_NAME ve REACT_APP_BACKEND_URL kullanılacak; değiştirilmeyecek.
- Tasarım rehberindeki MONGODB_URI / Mongoose önerileri uygulanmayacak; ortamın mevcut Python/MongoDB yapısı korunacak.
- Herkese açık görev ayarları sunucudan okunacak; gizli ortam değişkenleri istemciye aktarılmayacak.
- X kullanıcı adı girişi kimlik doğrulaması değildir; tamamlanmış görevler doğrulanmış olarak gösterilmeyecek.

## Referans incelemesi — 2026-07-19
- Crawl ve Playwright ile https://agnt.trade herkese açık sayfası incelendi; kaynak siteye kayıt veya form gönderimi yapılmadı.
- İlk ekran: tam ekran hareketli kare ajan ızgarası, sol üst logo, sağ üst sayaç/early access, büyük merkezî agnt logosu, terminal metni, X handle alanı ve CONNECT X, altta yeni katılanlar bandı.
- DOM/crawl içinde: mission console, agent license, cell/class/tier, görev sayacı 0/4, EVM adres alanı/Bind, Claim early access, AGENT LIVE, Post on X, Save card, Copy ref code görüldü.
- Görevlerin kesin içeriği henüz doğrulanmadı; kaynağa kayıt yapılmadan incelenmeli veya kullanıcının istediği follow/RT/comment akışına uyarlanmalı.

## Yapılanlar — 2026-07-19
- Gereksinimler netleştirildi ve üç geçici tasarım yönü /app/design_guidelines.json dosyasında oluşturuldu.
- Üç görsel maket üretildi. Bunlar çalışan uygulama ekranları değil, tasarım örnekleridir; örnek sayaçlar gerçek uygulama verisi değildir.
- Seçilen harita dokusu için bağımsız, metinsiz görsel üretildi; `/frontend/src/assets/survival-map.jpg` dosyasına kaydedildi.
- Kaynağın herkese açık JavaScript dosyaları incelendi: dört görev FOLLOW, LIKE, REPOST, COMMENT; hedef @agntmarkets, gönderi kimliği 2103830135996833932. Kaynak siteye veri gönderilmedi.

## Tamamlanan uygulama — 2026-07-19
- Ana ekran: seçilen harita/pano görünümü, marka, gerçek kayıt sayısı, X kullanıcı adı girişi, son katılanlar, ağ durumu, saat. Yapay katılımcı/sayaç yok.
- Dört adımlı konsol: kullanıcı adı, FOLLOW/LIKE/REPOST/COMMENT linkleri ve açık kullanıcı beyanı kutuları, EVM adresi bağlama/düzenleme, rıza ve kayıt.
- Taslak localStorage'da; kalıcı kayıt MongoDB'de. UUID istek kimliği idempotency için; hesap kimlik doğrulaması değil. X kullanıcı adı case-insensitive benzersiz. Görevler, adres ve rıza API'de doğrulanıyor.
- Kayıt sonucu: numara, hücre, sınıf, tier, referans kodu; yerel canvas ajan kartı PNG indirme/panoya kopyalama; X paylaşımı ve davet bağlantısı. Kart yüklemesi veya dosya saklama entegrasyonu yok.
- `/agent/:refCode` herkese açık kart ve davet akışı. Wallet/request_id/consent gibi özel alanlar public API'de yok.
- Ayarlar: `backend/.env` görev metin/linkleri, yorum mesajı, paylaşım mesajı, X profili. `/api/config` yalnızca izinli açık ayarları döndürür; `.env` güncellemeleri sonraki istekte okunur. Kullanım: `backend/CONFIGURATION.md`.
- API: GET `/api/`, `/api/config`, `/api/agents/stats`, `/api/agents/recent`, `/api/agents/{ref_code}`; POST `/api/participations`.
- Sayfalar: `/`, `/console`, `/agent/:refCode`; bilinmeyen sayfa/kod için hata ekranı.

## LastZhood isim güncellemesi — 2026-07-19
- Kullanıcının son isteğiyle logo, büyük başlık, footer, sekme başlığı, açıklama, LZ favicon, kart görseli/indirme dosya adı, paylaşım metinleri LastZhood olarak değiştirildi.
- Resmî X hesabı `https://x.com/LastZhood`; follow intent `screen_name=LastZhood`.
- Kullanıcı belirli bir gönderi URL'si vermedi; X profil taraması da gönderi döndürmedi. Bu nedenle LIKE/REPOST/COMMENT açıkça "a @LastZhood post" metniyle LastZhood profilini açıyor. Eski agntmarkets hedefleri tamamen kaldırıldı. Belirli tweet hedefi istenirse `.env` linkleri güncellenebilir.
- Yorum mesajı konsolda görünür ve `Copy reply` ile kopyalanabilir; intent URL ayarlanırsa aynı mesaj URL'ye eklenir.
- LocalStorage yeni anahtarı `lastzhood-survivor-v1`; önceki `agnt-survivor-v1` taslakları için okuma geçişi korundu.

## Doğrulama ve düzeltmeler — 2026-07-19
- İlk test raporu `/app/test_reports/iteration_1.json`: 13/13 backend geçti; cüzdan düzenleme düğmesinde tık sonrası formun tekrar submit olması hatası bulundu.
- Düzeltme: düzenle/bağla düğmelerine ayrı React key, düzenleme olayında preventDefault, adres düzenlenince rıza sıfırlama.
- Son rapor `/app/test_reports/iteration_2.json`: backend ve frontend kapsamı %100 geçti; açık hata yok.
- LastZhood adı ve taşma testleri: 1920×800 masaüstü, 390/381/375/320 genişlik mobil; kullanıcı adı, görev açma/beyan ayrımı, adres hataları, düzenle/tekrar bağla, rıza, kayıt ve yeni wallet değerinin MongoDB'de kalıcılığı doğrulandı.
- PNG indirme, panoya kopyalama/fallback, public kart, referans kaydı, hata durumları, duplicate/idempotency ve private alanların dışarı sızmaması test edildi.
- `yarn build` başarılı. Test kayıtları temizlendi. X üzerinde gerçek sosyal işlem yapılmadı; X API entegrasyonu kullanıcı tercihi gereği yok.
- Son görseller `/app/test_reports/artifacts/iteration_2/` altında.
- Runtime wallet kontrol dosyası, geçici test kaydı temizlendikten sonra tekrar koşulduğunda yanlış alarm vermemesi için pytest dizininden kaldırıldı; sonuç raporda kayıtlıdır.

### Görsel örnekler
1. CRT terminal: https://static.prod-images.emergentagent.com/jobs/a2dcf251-5c25-48b6-bb5b-fcddb74891ae/images/64ae54abfdee76899a9fef1c0eedd7e08001e3ae5533b3a803062e0455cc8eb0.jpeg
2. Hayatta kalma panosu: https://static.prod-images.emergentagent.com/jobs/a2dcf251-5c25-48b6-bb5b-fcddb74891ae/images/c968eb18e6ddacedef4d108b5c04e6e2eb5777a650340d10682954693c715f56.jpeg
3. Askerî radar: https://static.prod-images.emergentagent.com/jobs/a2dcf251-5c25-48b6-bb5b-fcddb74891ae/images/c9cae18d6079489b15507949c8af294fb5a9048846f31441f8c714d0df2fbf71.jpeg

## Önceliklendirilmiş kalan işler
- P0: Yok; çekirdek akış, LastZhood isim güncellemesi ve anahtarsız X profil fotoğrafı tamamlandı.
- P1 (isteğe bağlı kampanya girdisi): Kullanıcı belirli gönderi bağlantısı paylaşırsa beğeni/RT/yorum görevlerini o gönderiye yönlendirmek. Şimdiki profil akışı kullanılabilir durumdadır.
- P2 önerileri (henüz kullanıcı istemedi): Referans davet sıralaması; hayatta kalma temalı farklı ajan portreleri; Türkçe/İngilizce dil seçimi.

## X profil fotoğrafı — 2026-07-19
- Kullanıcı adıyla CONNECT X üzerinden devam edilince gerçek herkese açık profil fotoğrafı sorgulanıyor. Yükleme durumu gösterilir; sorgu başarısız olsa da konsola geçiş engellenmez.
- Entegrasyon playbook'u alındı. Kaynak: FxTwitter v2 `/2/profile/{handle}`, anahtar/OAuth yok. Bu işlem kullanıcı adı sahipliği veya X görevleri doğrulaması değildir.
- Fotoğraf hem operatör alanında hem ajan lisansı canvas'ında görünür; PNG indirme, görsel panoya kopyalama ve herkese açık kart sayfası aynı fotoğrafı kullanır. Görselin tamamı contain yöntemiyle korunur.
- Eksik/varsayılan/korumalı/erişilemeyen fotoğraf durumunda mevcut piksel karakteri gösterilir. Kullanıcı adı değişince eski hesabın fotoğrafı anında kaldırılır. Fotoğraf yüklenirken yanlış görsel indirilmemesi için dışa aktarma düğmeleri geçici devre dışıdır.
- `backend/avatar_provider.py`: normalize/allowlist, süre ve yanıt boyutu sınırları, eşzamanlı sorgu birleştirme, Mongo metadata önbelleği. `backend/x_avatar.py`: profil API, istek limiti, geçici görsel proxy, raster doğrulama/PNG dönüştürme ve bellek önbelleği.
- Yeni API: GET `/api/x/profile/{handle}` ve `/api/x/avatar/{handle}`. Görsel hedefi istemciden kabul edilmez. Yalnızca izinli HTTPS X CDN `/profile_images/` adresleri indirilir; yönlendirmeler izlenmez.
- MongoDB `x_avatar_metadata`: handle/avatar_url/source/expires_at; `_id` dışlanır, UTC datetime TTL index kullanılır. Başarılı metadata 6 saat, başarısız sorgu 60 saniye; binary/Base64 veya diğer profil bilgileri saklanmaz.
- Görsel byte'ları dosya olarak saklanmaz; sunucu belleğinde en fazla 64 adet, en fazla 1 saat. Kullanıcı dosya yüklemesi olmadığı için nesne depolama entegrasyonu gerekmiyor.
- `.env`: FXTWITTER_BASE_URL, FXTWITTER_USER_AGENT, X_LOOKUP_TIMEOUT_SECONDS, X_AVATAR_MAX_BYTES, X_AVATAR_CACHE_SECONDS, X_AVATAR_FAILURE_CACHE_SECONDS, X_AVATAR_CDN_HOSTS, X_LOOKUP_RATE_LIMIT. Kullanım belgesi backend/CONFIGURATION.md güncel.
- Frontend: lib/xProfile.js + hooks/useXAvatar.js ortak promise önbelleği; OperatorIdentity ve AgentLicense aynı API'den yükler. CORS-safe proxy sayesinde canvas taint oluşmuyor.
- Gerçek kaynak testi: NASA fotoğrafı 400×400 PNG olarak alındı ve karta kondu. İlk geçici 404 kaynak hatası 60 saniyelik negatif önbellek süresi sonrasında kendiliğinden düzeldi; best-effort davranışı doğrulandı.
- Kaynak, test anında @LastZhood için varsayılan X fotoğrafı döndürdü; özel fotoğraf bulunmadığı için karakter korunuyor. Bu, kullanıcı hesabının gerçek güncel durumuna dair garanti değil, üçüncü taraf kaynak yanıtıdır.
- Test raporu iteration_3.json: UI NASA/fallback/handle switch/export ve mobil 390/320 geçti; 19/20 backend testi geçti. Tek fark, ara sunucunun HTTP Cache-Control başlığını no-store yapmasıydı; fotoğraf akışı bozuk değildi.
- Gerçek önbellek davranışı `X-Avatar-Cache: HIT` ile ölçülebilir yapıldı. Test, ara sunucu no-store politikasını kabul edip aynı görselin sunucu belleğinden tekrar döndüğünü doğrulayacak şekilde düzeltildi.
- Son doğrulama: 20/20 backend testi geçti (7 avatar + 13 mevcut kayıt regresyonu). JUnit: `/app/test_reports/pytest/avatar_final_results.xml`; kapanış notu `/app/test_reports/avatar_final_verification.md`. `yarn build` başarılı. Production API'ler gerçek; yalnızca test izolasyonunda kontrollü sahte yanıtlar kullanıldı.

## VOICE (Reply) post akışı — 2026-06
- Kullanıcı isteği: "VOICE kısmında Reply basınca X açılacak ve X'te post paylaşımı yapacak; yazı altına son RT linki gelecek."
- `settings.py` comment görevi URL'si artık `https://x.com/intent/post?text={X_SHARE_TEXT}&url={X_REPOST_LINK}` olarak kuruluyor. X post paylaşma ekranı açılır, metin X_SHARE_TEXT, altına X_REPOST_LINK (repost görev linki) eklenir.
- Metin/link `.env`'den yönetilir: `X_SHARE_TEXT` ve `X_REPOST_LINK`.
- Test: `tests/test_registry_api.py` VOICE için text==share_text ve url==repost_task.url doğrulayacak şekilde güncellendi; 13/13 geçti.
## Repo yeniden kurulumu — 2026-09-28
- https://github.com/Dostarki/lastform reposu /app dizinine kopyalandı; backend/.env (MongoDB + X kampanya değişkenleri + FxTwitter avatar ayarları) yeniden oluşturuldu.
- Doğrulama: GET /api/, /api/config, /api/agents/stats çalışıyor; ana sayfa 1920x800 ve 390x844 ekran görüntüleri sorunsuz. MongoDB boş başladı (count: 0).

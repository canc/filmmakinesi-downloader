# M3U8 Video Downloader

Bu script, **filmmakinesi.to üzerinden elde edilen `.m3u8` playlist dosyalarını** indirerek içerisindeki video parçalarını `.ts` formatında kaydeder ve FFmpeg kullanarak tek bir `.mp4` dosyasında birleştirir.

## Gereksinimler

- macOS
- Python 3
- FFmpeg

Python bağımlılığı:

- `requests`

## Kurulum

### 1. Virtual Environment oluştur

Script'in bulunduğu klasöre geçin:

```bash
cd /path/to/downloads
```

Python virtual environment oluşturun:

```bash
python3 -m venv .venv
```

Virtual environment'ı aktif edin:

```bash
source .venv/bin/activate
```

Aktif olduğunda terminal satırının başında genellikle:

```text
(.venv)
```

görünür.

### 2. Gerekli Python paketini yükle

```bash
pip install requests
```

### 3. FFmpeg kurulumu

Homebrew kullanıyorsanız:

```bash
brew install ffmpeg
```

Kurulumu kontrol etmek için:

```bash
ffmpeg -version
```

## Klasör Yapısı

Script'in bulunduğu klasöre `.m3u8` dosyaları yerleştirilir:

```text
downloads/
├── download.py
├── episode_1.m3u8
└── episode_2.m3u8
```

Script çalıştırıldığında video parçaları `video_parts/` altında tutulur ve tamamlanan videolar ana klasöre `.mp4` olarak oluşturulur:

```text
downloads/
├── download.py
├── episode_1.m3u8
├── episode_2.m3u8
├── episode_1.mp4
├── episode_2.mp4
└── video_parts/
    ├── episode_1/
    │   ├── episode_1_part_0000.ts
    │   ├── episode_1_part_0001.ts
    │   └── episode_1_list.txt
    └── episode_2/
        ├── episode_2_part_0000.ts
        └── episode_2_list.txt
```

## Kullanım

Öncelikle virtual environment'ı aktif edin:

```bash
source .venv/bin/activate
```

Ardından script'i çalıştırın:

```bash
python3 download.py
```

Klasörde bulunan tüm `.m3u8` dosyaları alfabetik sırayla işlenir.

Her playlist için:

1. `.m3u8` içerisindeki video parçaları indirilir.
2. Parçalar `video_parts/<playlist_adı>/` klasörüne kaydedilir.
3. FFmpeg için geçici bir liste dosyası oluşturulur.
4. `.ts` parçaları tek bir `.mp4` dosyasında birleştirilir.
5. Başarılı işlemden sonra geçici liste dosyası silinir.

## Auto-delete

İndirilen `.ts` parçalarının video oluşturulduktan sonra otomatik olarak silinmesini istiyorsanız:

```bash
python3 download.py -autodelete=true
```

Bu durumda FFmpeg işlemi başarılı olur ve oluşturulan `.mp4` dosyası doğrulanırsa ilgili `video_parts/<playlist_adı>/` klasörü tamamen silinir.

Örneğin:

```text
episode_1.m3u8
    ↓
video_parts/episode_1/*.ts
    ↓
FFmpeg
    ↓
episode_1.mp4
    ↓
video_parts/episode_1/ silinir
```

FFmpeg işlemi başarısız olursa `.ts` parçaları **silinmez** ve script tekrar çalıştırıldığında mevcut parçalar korunur.

## Virtual Environment'ı kapatma

İşiniz bittiğinde:

```bash
deactivate
```

komutuyla virtual environment'ı kapatabilirsiniz.

## Not

Bu script **yalnızca filmmakinesi.to üzerinden elde edilen `.m3u8` dosyaları için tasarlanmıştır**. Başka kaynaklardan alınan playlist dosyalarının yapısı veya erişim gereksinimleri farklı olabileceğinden çalışması garanti edilmez.
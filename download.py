import os
import re
import time
import random
import requests
import glob
import subprocess
import argparse
import shutil


# Configuration
TARGET_ROOT_FOLDER = "video_parts"

HEADERS = {
    "Referer": "https://filmmakinesi.to",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive"
}


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-autodelete",
        type=str,
        default="false",
        choices=["true", "false"],
        help="Delete downloaded TS files after successful FFmpeg merge."
    )

    return parser.parse_args()


args = parse_arguments()
auto_delete = args.autodelete == "true"


# Find all .m3u8 files in the current directory
m3u8_files = sorted(glob.glob("*.m3u8"))

if not m3u8_files:
    print("❌ Klasörde '.m3u8' formatında dosya bulunamadı!")
    exit()

print(f"📚 Toplam {len(m3u8_files)} adet listeleme dosyası bulundu: {m3u8_files}")
print(f"🗑️ Auto-delete: {'AÇIK' if auto_delete else 'KAPALI'}\n")


session = requests.Session()
session.headers.update(HEADERS)


# Process each m3u8 file
for m3u8_file in m3u8_files:

    # Use filename without extension as prefix
    prefix = os.path.splitext(m3u8_file)[0]

    # Create video_parts/<prefix>/
    target_folder = os.path.join(TARGET_ROOT_FOLDER, prefix)
    os.makedirs(target_folder, exist_ok=True)

    print(f"📖 {m3u8_file} okunuyor...")

    with open(m3u8_file, "r", encoding="utf-8") as file:
        content = file.read()

    urls = [
        line.strip()
        for line in content.splitlines()
        if line.strip().startswith("http")
    ]

    if not urls:
        urls = re.findall(r"https?://[^\s]+", content)

    print(
        f"⏳ {prefix} için {len(urls)} adet parça algılandı. "
        f"İndirme başlıyor...\n"
    )

    index = 0

    while index < len(urls):

        url = urls[index]

        # video_parts/<prefix>/<prefix>_part_0000.ts
        output_file = os.path.join(
            target_folder,
            f"{prefix}_part_{index:04d}.ts"
        )

        # Skip already downloaded files
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            index += 1
            continue

        print(
            f"[{prefix}] [{index + 1}/{len(urls)}] "
            f"İndiriliyor -> {url.split('/')[-1]}"
        )

        try:
            response = session.get(url, timeout=15)

            print(f"status: {response.status_code}")

            if response.status_code == 200:

                with open(output_file, "wb") as file:
                    file.write(response.content)

                delay = random.uniform(0.2, 0.8)
                time.sleep(delay)

                index += 1

            elif response.status_code == 429:

                print(
                    "⚠️ Hız limitine takılındı! "
                    "30 saniye bekleniyor..."
                )

                time.sleep(30)

            else:

                print(
                    f"❌ Hata: Sunucu {response.status_code} "
                    f"yanıtı verdi. Link: {url}"
                )

                index += 1

        except Exception as error:

            print(
                f"❌ Bağlantı hatası oluştu, "
                f"5 saniye sonra tekrar denenecek: {error}"
            )

            time.sleep(5)

    print(
        f"\n✅ {prefix} için tüm parçalar indirildi. "
        f"FFmpeg birleştirme işlemi başlıyor..."
    )

    # FFmpeg concat list
    list_filename = f"{prefix}_list.txt"
    list_file = os.path.join(target_folder, list_filename)

    # Final MP4 path
    output_mp4_path = f"{prefix}.mp4"

    # Collect downloaded TS files
    ts_files = sorted(
        [
            filename
            for filename in os.listdir(target_folder)
            if filename.startswith(f"{prefix}_part_")
            and filename.endswith(".ts")
        ]
    )

    if not ts_files:

        print(
            f"⚠️ {target_folder} içinde "
            f"birleştirilecek parça bulunamadı."
        )

        continue

    # Create FFmpeg concat list
    with open(list_file, "w", encoding="utf-8") as file:

        for ts_file in ts_files:
            file.write(f"file '{ts_file}'\n")

    print(
        f"🎬 {prefix} parçaları birleştiriliyor -> "
        f"{output_mp4_path}"
    )

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_filename,
        "-c", "copy",
        f"../../{output_mp4_path}"
    ]

    try:

        subprocess.run(
            ffmpeg_command,
            cwd=target_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )

        # Verify that FFmpeg actually created the MP4
        final_output_path = os.path.join(
            os.getcwd(),
            output_mp4_path
        )

        if not os.path.exists(final_output_path):
            print(
                f"❌ FFmpeg komutu başarılı görünmesine rağmen "
                f"{output_mp4_path} oluşturulamadı."
            )

            continue

        if os.path.getsize(final_output_path) == 0:
            print(
                f"❌ {output_mp4_path} oluşturuldu ancak dosya boyutu 0."
            )

            continue

        print(
            f"🎉 Başarılı! {output_mp4_path} dosyası hazır."
        )

        # Remove temporary FFmpeg list
        if os.path.exists(list_file):
            os.remove(list_file)

        # Auto-delete downloaded TS files
        if auto_delete:

            print(
                f"🗑️ Auto-delete aktif. "
                f"{target_folder} siliniyor..."
            )

            shutil.rmtree(target_folder)

            print(
                f"✅ {target_folder} silindi."
            )

        print()

    except subprocess.CalledProcessError as error:

        print(
            f"❌ FFmpeg hatası ({prefix}): "
            f"{error.stderr.decode('utf-8', errors='ignore')}\n"
        )

        print(
            "⚠️ İndirilen .ts parçaları korunuyor."
        )

    except Exception as error:

        print(
            f"❌ FFmpeg işlemi sırasında beklenmeyen hata "
            f"({prefix}): {error}\n"
        )

        print(
            "⚠️ İndirilen .ts parçaları korunuyor."
        )


print(
    "🚀 Tüm m3u8 süreçleri sırasıyla "
    "(İndirme -> FFmpeg -> Sıradaki) başarıyla tamamlandı!"
)

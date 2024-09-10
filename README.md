# Bot Telegram Otomatis

Bot Telegram ini dirancang untuk mengirim pesan otomatis ke berbagai grup dengan fitur-fitur canggih seperti pengelolaan cache, penjadwalan, dan analitik.

## Fitur Utama

- Pengiriman pesan otomatis ke banyak grup
- Sistem cache untuk meningkatkan kinerja
- Penjadwalan tugas menggunakan AsyncIOScheduler
- Penanganan error dan rate limiting
- Analitik untuk memantau kinerja bot
- Logging komprehensif
- Konfigurasi fleksibel melalui file .env

## Struktur Proyek

- `src/`: Direktori utama kode sumber
  - `analytics.py`: Menghasilkan laporan analitik
  - `cache.py`: Mengelola sistem caching
  - `config.py`: Menangani konfigurasi bot
  - `data_handler.py`: Mengelola data persisten
  - `group_handler.py`: Menangani operasi terkait grup
  - `logger.py`: Mengatur sistem logging
  - `main.py`: Titik masuk utama aplikasi
  - `message_handler.py`: Menangani pengiriman pesan
  - `scheduler_setup.py`: Mengatur penjadwalan tugas
- `bot.py`: Skrip untuk menjalankan bot
- `data/`: Direktori untuk file data
  - `groups.txt`: Daftar grup target
  - `messages1.txt` - `messages5.txt`: File pesan yang akan dikirim
  - `blacklist.txt`: Daftar grup yang diblokir
  - `persistent_data.json`: Data persisten bot
- `logs/`: Direktori untuk file log
- `requirements.txt`: Daftar dependensi Python

## Instalasi

1. Clone repository ini
2. Install dependensi dengan `pip install -r requirements.txt`
3. Buat file `.env` di folder `data/` dan isi dengan kredensial Anda:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
```

4. Jalankan bot dengan perintah `python bot.py`

## Penggunaan

Bot akan berjalan secara otomatis setelah dijalankan, mengirim pesan ke grup-grup yang ditentukan dalam `data/groups.txt` sesuai jadwal yang diatur.

## Kontribusi

Kontribusi selalu diterima. Silakan buat pull request atau buka issue untuk saran dan perbaikan.

## Lisensi

[MIT License](LICENSE)

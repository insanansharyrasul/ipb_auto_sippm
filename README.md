# Penggunaan Aplikasi

Aplikasi ini mengisi data **Log Kegiatan SIPPm** secara otomatis dari file CSV.

## 1. Yang perlu disiapkan

Pastikan sudah ada:

- Python versi 3.9 atau lebih baru
- Username dan password SIPPm
- File foto atau bukti dokumentasi untuk setiap kegiatan

## 2. Buka folder aplikasi

Semua perintah berikut harus dijalankan dari folder yang berisi file `script.py`.

Contoh isi folder:

```text
script.py
data.csv
bukti_dokumentasi/
```

## 3. Pasang kebutuhan aplikasi

Buka Terminal atau PowerShell, lalu jalankan:

```bash
python -m venv .venv
```

Aktifkan lingkungan aplikasi.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Setelah aktif, pasang kebutuhan aplikasi:

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

## 4. Isi username dan password

Buat file baru bernama `.env` di folder aplikasi. Isinya:

```env
SIPPM_USERNAME=username-anda
SIPPM_PASSWORD=password-anda
```

Ganti `username-anda` dan `password-anda` dengan akun SIPPm Anda.

Jangan membagikan file `.env` kepada orang lain.

## 5. Siapkan file CSV

Buat atau ubah file `data.csv` dengan format berikut:

```csv
kegiatan,tempat,TMT,TST,bukti_dokumentasi
Rapat,Kampus,31/12/2026,01/01/2027,bukti_dokumentasi/kirei.png
```

Nama kolom harus sama persis:

```text
kegiatan,tempat,TMT,TST,bukti_dokumentasi
```

Keterangan:

- `kegiatan`: nama kegiatan
- `tempat`: tempat kegiatan
- `TMT`: tanggal mulai, contoh `31/12/2026`
- `TST`: tanggal selesai, contoh `01/01/2027`
- `bukti_dokumentasi`: lokasi file foto atau bukti

## 6. Tulis lokasi file bukti

Lokasi file dihitung dari folder tempat file CSV berada.

Jika susunan foldernya seperti ini:

```text
data.csv
bukti_dokumentasi/
	kirei.png
```

Maka isi kolom `bukti_dokumentasi` adalah:

```text
bukti_dokumentasi/kirei.png
```

File bukti juga boleh berada di folder yang sama dengan CSV:

```text
kirei.png
```

## 7. Jalankan aplikasi

Dengan `.venv` masih aktif, jalankan:

```bash
python script.py data.csv
```

Browser akan terbuka dan aplikasi akan mengisi semua baris dalam CSV satu per satu.

Secara default, ada jeda 1 detik di antara setiap aksi agar proses mudah dilihat.
Untuk memperlambat proses, gunakan angka yang lebih besar:

```bash
python script.py data.csv --delay 2
```

Untuk menghilangkan jeda:

```bash
python script.py data.csv --delay 0
```

## Jika muncul error

**`No such file or directory`**

Pastikan nama dan lokasi file pada kolom `bukti_dokumentasi` benar.

**`Set SIPPM_USERNAME and SIPPM_PASSWORD`**

Pastikan file `.env` berada satu folder dengan `script.py` dan nama variabelnya benar.

**Browser Chromium belum tersedia**

Jalankan kembali:

```bash
playwright install chromium
```

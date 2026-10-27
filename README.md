# view-tt-ig

Mata-mata INSTAGRAM & TikTok — hanya untuk data **publik** dari akun yang dilihat.

By : Muhammad Jeksen
Tanggal dibuat : 27 Oktober 2026

## Fitur

1. Info profil TikTok (username, nama, bio, followers, following, jumlah video, verified)
2. Info profil INSTAGRAM (username, nama, bio, followers, following, jumlah postingan, verified)
3. Komentar di postingan akun yang dilihat (TikTok: ID video, INSTAGRAM: shortcode postingan)

Catatan penting:
- Akun privat tidak bisa dilihat — itu batas dari platformnya.
- Tidak ada fitur riwayat komentar yang ditulis seseorang ke akun lain.
  Yang ditampilkan adalah komentar yang masuk ke postingan akun yang dilihat.
- Tidak ada tools nomor telepon di repo ini.

## Instalasi di Termux

```bash
pkg install -y python
pip install requests rich
git clone https://github.com/Lexus14/view-tt-ig.git
cd view-tt-ig
cp .env.example .env
nano .env
python3 view_tt_ig.py
```

## Key API — pakai key-mu sendiri

Script ini **tidak** berisi API key siapa pun. Isi `.env` dengan key
RapidAPI-mu sendiri, dan subscribe (gratis) dulu di RapidAPI untuk:

- TikTok: `tiktok-scraper7`
- INSTAGRAM: `instagram-cheapest`

File `.env` sudah masuk `.gitignore`, jadi tidak akan ikut ter-push.
Kalau API mengembalikan 401, key-nya salah. Kalau 403, kamu belum
subscribe API tersebut. Kalau 429, kuotanya habis / dibatasi.

## Lisensi

Untuk pemakaian pribadi dan edukasi, hanya untuk data publik.

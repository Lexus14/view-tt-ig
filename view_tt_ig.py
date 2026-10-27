#!/usr/bin/env python3
"""
view-tt-ig - Mata-mata INSTAGRAM & TikTok (profil publik + komentar postingan)
By : Muhammad Jeksen
Tanggal dibuat : 27 Oktober 2026

Hanya menampilkan data PUBLIK dari akun yang dilihat.
Tidak ada API key di dalam kode ini. Key dibaca dari environment
atau file .env di folder yang sama dengan script ini.
Contoh .env ada di .env.example. Jangan pernah meng-commit file .env.

Cara pakai di Termux:
  pkg install -y python
  pip install requests rich
  cp .env.example .env
  nano .env          # isi RAPIDAPI_KEY dengan key RapidAPI-mu sendiri
  python3 view_tt_ig.py

API yang dipakai (RapidAPI, pakai key-mu sendiri, subscribe gratis dulu):
  - TikTok   : tiktok-scraper7.p.rapidapi.com  (endpoint /user/info)
  - INSTAGRAM: instagram-cheapest.p.rapidapi.com
               (endpoint /api/v1/instagram/user/<username>)
  Host dan path bisa diubah lewat .env kalau kamu pakai API lain
  dari RapidAPI yang setara, tanpa mengubah kode.
"""

import json
import os
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

    class _Plain:
        def print(self, *args, **kwargs):
            print(*args)

    console = _Plain()

try:
    import requests
except ImportError:
    requests = None

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ███████╗ ██╗  ██╗  █████╗  ███╗   ██╗  ██████╗     ║
║      ██╔╝ ██║  ██║ ██╔══██╗ ████╗  ██║ ██╔════╝     ║
║     ██╔╝  ███████║ ███████║ ██╔██╗ ██║ ██║  ███╗    ║
║    ██╔╝   ██╔══██║ ██╔══██║ ██║╚██╗██║ ██║   ██║    ║
║   ███████╗██║  ██║ ██║  ██║ ██║ ╚████║ ╚██████╔╝    ║
║                                                      ║
║   ────────────────────────────────────────────────   ║
║   By : Muhammad Jeksen                               ║
║   Tanggal dibuat : 27 Oktober 2026                   ║
║                                                      ║
║   Mata-mata  •  INSTAGRAM  •  TikTok                 ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""


def load_dotenv():
    """Baca .env sederhana (KEY=VALUE) tanpa library tambahan."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_config():
    load_dotenv()
    return {
        "key": os.environ.get("RAPIDAPI_KEY", "").strip(),
        "tiktok_host": os.environ.get(
            "TIKTOK_RAPIDAPI_HOST", "tiktok-scraper7.p.rapidapi.com"
        ).strip(),
        "tiktok_info_path": os.environ.get("TIKTOK_INFO_PATH", "/user/info").strip(),
        "instagram_host": os.environ.get(
            "INSTAGRAM_RAPIDAPI_HOST", "instagram-cheapest.p.rapidapi.com"
        ).strip(),
        "instagram_user_path": os.environ.get(
            "INSTAGRAM_USER_PATH", "/api/v1/instagram/user"
        ).strip(),
        "instagram_comments_path": os.environ.get(
            "INSTAGRAM_COMMENTS_PATH", "/api/v1/instagram/media_comments"
        ).strip(),
        "tiktok_comments_path": os.environ.get(
            "TIKTOK_COMMENTS_PATH", "/video/comments"
        ).strip(),
    }


def show_banner():
    if HAS_RICH:
        console.print(Panel(BANNER, border_style="cyan", title="view-tt-ig"))
    else:
        print(BANNER)


def find_value(data, keys):
    """Cari nilai pertama dari daftar key, menelusuri dict/list bersarang."""
    if isinstance(data, dict):
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
        for value in data.values():
            found = find_value(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_value(item, keys)
            if found not in (None, ""):
                return found
    return None


def find_list(data, keys):
    """Cari list pertama yang cocok (untuk postingan / komentar)."""
    if isinstance(data, dict):
        for key in keys:
            if isinstance(data.get(key), list) and data[key]:
                return data[key]
        for value in data.values():
            found = find_list(value, keys)
            if found:
                return found
    elif isinstance(data, list):
        return data
    return []


def api_get(cfg, host, path, params):
    if requests is None:
        print("Butuh library requests. Jalankan: pip install requests rich")
        return None
    if not cfg["key"]:
        print("RAPIDAPI_KEY belum diisi. Salin .env.example jadi .env,")
        print("lalu isi dengan key RapidAPI-mu sendiri.")
        return None
    url = f"https://{host}{path}"
    headers = {
        "X-RapidAPI-Key": cfg["key"],
        "X-RapidAPI-Host": host,
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:  # noqa: BLE001 - tampilkan apa adanya ke pengguna
        print(f"Gagal terhubung ke API: {e}")
        return None
    if resp.status_code == 401:
        print("401: Key tidak valid. Periksa RAPIDAPI_KEY di .env.")
        return None
    if resp.status_code == 403:
        print("403: Kamu belum subscribe API ini di RapidAPI.")
        print(f"Subscribe dulu API di host {host}, lalu coba lagi.")
        return None
    if resp.status_code == 429:
        print("429: Kuota API habis / dibatasi. Tunggu sebentar, coba lagi.")
        return None
    if resp.status_code != 200:
        print(f"API mengembalikan HTTP {resp.status_code}: {resp.text[:300]}")
        return None
    try:
        return resp.json()
    except ValueError:
        print("Respon API bukan JSON.")
        return None


def show_profile(title, data):
    username = find_value(data, ["uniqueId", "username", "user_name"])
    name = find_value(data, ["nickname", "full_name", "name"])
    bio = find_value(data, ["signature", "biography", "bio"])
    followers = find_value(
        data, ["followerCount", "follower_count", "followers", "edge_followed_by"]
    )
    following = find_value(data, ["followingCount", "following_count", "following"])
    posts = find_value(data, ["videoCount", "video_count", "media_count", "posts"])
    verified = find_value(data, ["verified", "is_verified"])
    private = find_value(data, ["privateAccount", "is_private", "private"])
    avatar = find_value(data, ["avatarLarger", "avatarMedium", "avatarThumb", "profile_pic_url"])

    if HAS_RICH:
        table = Table(title=title, show_header=False)
        table.add_column("Field")
        table.add_column("Nilai")
        for label, value in [
            ("Username", username),
            ("Nama", name),
            ("Bio", bio),
            ("Followers", followers),
            ("Following", following),
            ("Jumlah postingan/video", posts),
            ("Verified", verified),
            ("Akun privat", private),
            ("Avatar", avatar),
        ]:
            if value not in (None, ""):
                table.add_row(label, str(value))
        console.print(table)
    else:
        print(f"--- {title} ---")
        for label, value in [
            ("Username", username),
            ("Nama", name),
            ("Bio", bio),
            ("Followers", followers),
            ("Following", following),
            ("Jumlah postingan/video", posts),
            ("Verified", verified),
            ("Akun privat", private),
            ("Avatar", avatar),
        ]:
            if value not in (None, ""):
                print(f"{label}: {value}")
    if not any([username, name, followers]):
        print("Data tidak dikenali. Respon mentah (dipotong):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])


def tiktok_profile(cfg):
    username = input("Masukkan username TikTok (tanpa @) > ").strip().lstrip("@")
    if not username:
        return
    data = api_get(cfg, cfg["tiktok_host"], cfg["tiktok_info_path"], {"unique_id": username})
    if data:
        show_profile("Profil TikTok", data)


def instagram_profile(cfg):
    username = input("Masukkan username INSTAGRAM (tanpa @) > ").strip().lstrip("@")
    if not username:
        return
    path = f"{cfg['instagram_user_path'].rstrip('/')}/{username}"
    data = api_get(cfg, cfg["instagram_host"], path, {})
    if data:
        show_profile("Profil INSTAGRAM", data)


def show_comments(title, items, limit=20):
    print(f"--- {title} ({len(items)} ditemukan, ditampilkan maks {limit}) ---")
    for i, item in enumerate(items[:limit], 1):
        if isinstance(item, dict):
            user = find_value(item, ["username", "user_name", "author", "owner_username"])
            text = find_value(item, ["text", "comment", "caption", "body"])
            likes = find_value(item, ["like_count", "likes", "digg_count"])
            line = f"{i}. @{user}: {text}" if user else f"{i}. {text}"
            if likes not in (None, ""):
                line += f"  (like: {likes})"
            print(line)
        else:
            print(f"{i}. {item}")


def post_comments(cfg):
    print("1. TikTok (masukkan ID video)")
    print("2. INSTAGRAM (masukkan shortcode postingan, misal dari link instagram.com/p/<shortcode>/)")
    choice = input("Pilih > ").strip()
    if choice == "1":
        video_id = input("Masukkan ID video TikTok > ").strip()
        if not video_id:
            return
        data = api_get(
            cfg, cfg["tiktok_host"], cfg["tiktok_comments_path"], {"video_id": video_id}
        )
        if data:
            items = find_list(data, ["comments", "comment_list", "data"])
            show_comments("Komentar video TikTok", items)
    elif choice == "2":
        shortcode = input("Masukkan shortcode postingan INSTAGRAM > ").strip()
        if not shortcode:
            return
        data = api_get(
            cfg,
            cfg["instagram_host"],
            cfg["instagram_comments_path"],
            {"shortcode": shortcode},
        )
        if data:
            items = find_list(data, ["comments", "comment_list", "data"])
            show_comments("Komentar postingan INSTAGRAM", items)
    else:
        print("Pilihan tidak dikenal.")


def main():
    cfg = get_config()
    while True:
        show_banner()
        if not cfg["key"]:
            print("Catatan: RAPIDAPI_KEY belum diisi. Buat file .env dari .env.example.")
        print("Menu:")
        print("  1. Info profil TikTok")
        print("  2. Info profil INSTAGRAM")
        print("  3. Komentar di postingan akun yang dilihat (TikTok / INSTAGRAM)")
        print("  0. Keluar")
        choice = input("Pilih > ").strip()
        if choice == "1":
            tiktok_profile(cfg)
        elif choice == "2":
            instagram_profile(cfg)
        elif choice == "3":
            post_comments(cfg)
        elif choice == "0":
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak dikenal.")
        input("\nTekan Enter untuk kembali ke menu...")


if __name__ == "__main__":
    main()

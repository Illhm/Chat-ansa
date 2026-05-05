import requests
import time
import json
import random

# ==========================================
# KONFIGURASI DARI FILE HAR
# ==========================================
import os

# Ganti token authorization jika sudah kadaluarsa
# Membaca dari environment variables untuk keamanan
AUTHORIZATION_TOKEN = os.environ.get("HIFAMI_AUTH_TOKEN", "")
MEMBER_ID = os.environ.get("HIFAMI_MEMBER_ID", "")

if not AUTHORIZATION_TOKEN or not MEMBER_ID:
    print("[!] ERROR: HIFAMI_AUTH_TOKEN atau HIFAMI_MEMBER_ID belum diset di environment variables.")
    print("Contoh penggunaan: HIFAMI_AUTH_TOKEN='token_kamu' HIFAMI_MEMBER_ID='id_kamu' python auto_farm.py")
    exit(1)

# Header statis yang diambil dari log HAR
# PERHATIAN: business_sign, devicetoken, rcsign dsb adalah nilai statis dari log terakhir.
# Jika server memvalidasi nilai dinamis ini secara ketat, request ini mungkin akan gagal (kode 403/401).
HEADERS = {
    "apikey": "3d124ec3",
    "codetag": "weparty-6.7.201",
    "channel": "market_guanwang",
    "memberid": MEMBER_ID,
    "authorization": AUTHORIZATION_TOKEN,
    "osversion": "16",
    "brand": "POCO",
    "user-agent": "weparty-Android-Mozilla/5.0 (Linux; Android 16; M2012K11AG Build/BP2A.250605.031.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.111 Mobile Safari/537.36",
    "versionname": "6.7.201",
    "environment": "unknown",
    "language": "id",
    "timezone": "Asia/Jakarta",
    "ispublish": "true",
    "isocode": "ID",
    "syslanguage": "id",
    "mcc": "510",
    "haszhlanguage": "false",
    "proxytype": "VPN",
    "isdevopen": "true",
    "x-device-id": "-",
    "x-umid": "b04524b83e1389588a2f82e834217ae8",
    "x-adid": "b685d67af26b87d15c77508942f3035c",
    "x-key-id": "key005",
    "x-member-id": MEMBER_ID,
    "x-authorization": AUTHORIZATION_TOKEN,
    "deviceenv": "000011001000000000",
    "umid": "b04524b83e1389588a2f82e834217ae8",
    "adid": "b685d67af26b87d15c77508942f3035c",
    "accept-encoding": "gzip",

    # --- HEADER DINAMIS / ENKRIPSI (Statis dari HAR, berpotensi bikin error jika basi) ---
    "rcsign": "6f0c557c3f7d5ca893ccbe1575f8c16819a850dcd538333aa0af73fa220eaec4cdf61b75d58460b7544d4067b1616389b056142988a6fe792ee5c296f8476f629b8e36e63e43739b9906184c6aff030a08893f005ac63e8a9ed19d0b4a0b1d47753ace9b629f3eb05ad0a7cb1c3b56e56a28af12af58b571ac619ad1f29a39a99177d6745ca5ea0c4036070e9642bc684971fbc7c32de29d99c6e1fceb162eb06619ee2f856fa878b9a332fa83a07f489dc0cc49eacafed93a7d087aa8bda0a9fe4d912b3f1be43bcbf046aa8859ea26ab104f7b46a91900b18426636cadd63ac01bbcdf0111c573053640597c585d101bb4c49caebab21be0ece044794a66a715b82e438db2efda15a59fe399aea949",
    "devicetoken": "U0dfUFJFSUQuMSNzZzk4NjYyMTQ3Z3M3MTUyYzFiMTc3NzVhMTg3OTQ1NC1oLTE3NzgwMjI1Njg5MDUtNmM0NzY2MDRhY2Q3NDA2NGI3NjljZWQ0OWVkMzc3MzkjVVBBWFBzaEw4bzZCaFVXU0hwZXhFenpDdDZtVVZDK0NjdEFlUDlWajhRRkhITFltUDU4cVlIY3M4ZEFHRmVNTDdBWEtqVlhKREF6UFZybTBFbUhFQW1xbWErR09sWmhWT2RnaXFXcW1uS256eVV1eFhnWm1rczdRb3I1dWxLbm9FNCtqZlQ3YjdVRy9TeG9HR1FiUkdXRWthcUFxck9IanBDaGY1WGJlMlR6T1pucTNSTmY5bkducFlVOUt3SHg2S21ZYXFweDBOZlhNNGpuSC91RlhnN20xTW9peTRPcDBWMG1mc0lydE5FQXN5Z3NVVzMyNGpUNzByd0Uxa014MGFMQytMUTNzQVp5ME5zczgzYWJoN1FVTW9HOWdHSkJIWUVFT0xUYm15RFEva0dpZlFWSmYwMWthNlllckJ4OUxnMTRGVHdkOFNXOStZd0sxWm42YmdEQlVrWW9VRDBqMWRyYVRVdmNyWWJnYzB3QU4va0ZWQ1IxaXJoNW90RE16NnFyYWV5d3BNV2ZlZzRacWluZVRscWU5S1hkUWx1MTJLc2l3aDY4ZVl1a01MNmdpYU1vekU4WE9YaHV4L3E1L0hFRm1YQnVpRGliWSsyNXMraDR6b1lucldocUI5RlpsYzNWNnpvcE1TcCswaFdQZFk1WEZ4dWhzak8zdGZnR3RMamlQRUdGem1kUzg1ZHR3MTZWcFBKQmdpOWNqeWwrc2MwTXo0SCt0S3dHclpJOFZhWmhQaDQvN1NubEo2Rk1ob1huQm1zbkdrWFRtTUxjY3hmK1JSelFEeVR3NTZNb2kxVzNnK1NEQ2ZQS05JTk9NelUzN1FQK2tHaWxKcjUzTlphSWQ2L05Hc3RjT0xHR1g5d2xJSDRudW8wOGwwaHRXTmlrbWhDUk0zbkZPR244Z0hlak9raGEyZnM1a0Q3ZE93ZFE5blRNeGpZcmNWUFk5WDhmT25WZmdWM0VQcTUvdmVjRzZ0UnFNTW80VWNCWVRPT3lpblhQOWloY2lhQUVDa0hiNisyYWJKRzVaWDQ2Wmo5dDROOEM3VmdTZmNFQW5CZXNLMFdwY1ZSRWlMYk4rVjZMTGZhTENhSnhDemNuRUp5WVJ0Sk1YbjN6MFJUNEQrdmxoQU5KMUhmSjVwNW5pcHpkMVViOTUwVzd2TjY1aXZPbjVXS0ZBNm5PbmZLdTZzL2QzQVQ4aHFCenhIOHNGbnREbFd6bWFlWGFLWDAwcmtLd1M1VVJSOERuMHJKc0pBdVdETTVjZE13eUlHSG5iNTkvcTRJczZjeEJkRzJsT1FHZnhLL0NyY0NDQktvSWlvM05OZFJjalY5YVZmNTQwMWlTTktvUUNFYTl5OFIzTzZoanlpWEpkT2tjOU92UXhlOHpkaWxaVFdUS1gyeVRpbktxVzZqdWpVSXphcXdBbCthaHdUaGtXckxMaG02TVZkMDE2cVYxeGNkcGtIS1pScmZ2K2FnWUsrYXJreTBkZE1XM2ZTaTBGc3pYR1RtVFQzL1g2ZW1VUkM1UHZ4TW0xVGdUa3htVEJ0bW1YeDFJZmtTRDZyN1FhUm5ZbExHbzY2R2YraGtyV0lMWStLUXAzWkNXVHZvWGQvMzBDM0ZncjBKOThYdENEcTEza2RKbElqZXI1TDZTTThudWtndU94QVRwOFZ3U0cwZFZyeHNMVFo1UzZ6Z3drV0h4b0gyT0Y1ZTRWdlNBd2tLR3NkTU94STZsTUozNDh5OWYvZGt6MHhvWUFnMjIvTUJoMEViNFQvN0R2aFJxalZINWM3WWh5WWZLVWFHSTQxam9sVkd1RUNNNGVBdG05M1FoRjZ3MmlXc0NtcDVCVU5wZkVZMDMzU0hFaFVVZERyZUdQcHBMNnMwS1hKSytLbTB5ODRVd2VqSXgwenp2V08rM2VNRXhZSmdRY0x2M21qYm1sNVh5NDVNWFNnRi82Qm9lU1Z4Z2h5SStqZVBIY0x5Wk1NcEtMRDVIUGRGelpsZktjelNJSW5DdGQzNWp0RTM0L3pwUHAxZXBiekZqRjltRnkxT280S2lYS0dDWVFzT3BFT1JYQ3lFblN1NFJzNkd3Q2RZRGpUS2hTVm4wVWhVQ3FXeTdLL0JKd0ZaVC9kWjlSSGRmRGJGcVYxY3d1RFpKdkptVitveFpLVjMyR29weEZZbU0rcjdRTkNLaS9RYmtmbXRNOGR4YUoya3FvT0p5c0JBeUNXVWhrenJoWWlKR3l0UXNNQnUxZmF1cUV2YTJHMXNzTU9oUU9qRGZ2b0poWis2NXRVODFQNWxSak5sNGR4T3J3cFIrZGJlVzZmdkZ3a2hsZExxMy82a2J0YVFtdTBTenlhTVY0RXpoUFBLS2wzcW15VlFteHZMNDNYNU1vT1d4cUEza3pPZUlta3pRdG9OQmJLQVYyVEJ6eThQeWJQQjVIRDc1TU9CK3JQbmJMay9Zbk9raTlNZm5SU1pEWTJ3SkpacmZqdE5BK3U2dUVNRWRnUU8zS1g4QVQ3Q0dibWhVcHpRY3kzR3M4TmVNdlhIODZ5M3lrYnAzeEtpQmREbG5sV1l4c0J1ZkNUVndQZkg4UUhoeGlTL3Z1RXdYY0RmUG0yUDdKbUl3ekNMaXNJT0NQUk1VNlhZSkNEWmVoWEQzbmJxem52b291VlBaZHhDTnRTZDl3a1pZUDZlUDdNdEZHUUtmUkQxVmZFQndxWTFIOENuZkNCdXUvMCtDL1E3VXZuZXBaK3pDVnhWVTd1VmkzQ0NBc1hidUsxWnZhMEJnZFh5WWIvNHZmbXpFNFBiWlM2TW5VOEJoMnB6RURRYUQ3cjlsVS93YnF0MWhTcU5ITTJIUEh5eENGVE1EdzNCWEdtQ20wUFZvNWdoUVBjTFFmZWNOVXRYZFRIZ2NnRWJ1aiswWVdMSVd6ZForYlhmais3dDVRN2s2M29zOVBvZ0Y5UkI2dHQvOFFNNzRSZW1MZzZkN0l0SHpwdTZQWXJqRzBObmFLMmdzSkgxeGlJdXNWWXlzSzNSSjZyUE4zbTdhVFg2M0Evd2FWeW1hYksvTTNUYUl3NzNPSHI5cGsxUGNYeTZJZ0UxYmdKR0R1R1RKSlpxUUY1QkJva3lTVCtHcEIjNzEyLjA2OSNDNCNhNzc5MTVkZjI3ODIzMzYzNTcxNDQxZmI2NGY2YWQxNQ==",
    "business_sign": "yDz2+XADa/UhlJh2IQr6CxValc0zn9BbBLyoiWXWoAo=",
    "business_sign_v2": "8DkYAg8ejuXxEpMCH+B5/l76upjv31rVZ9RegV1/4Yc=",
    "risktoken": "7741597EC34F1ED9B30772C11CDC1178",
    "noncestr": "17fe884dddb44d9889602175c3e5abcd",
    "x-nonce": "7a8c1bd27fee4760afa1d3b155a9a638"
}


def get_dynamic_headers():
    """
    Menambahkan header dinamis seperti timestamp ke dalam header agar
    terlihat seperti request asli.
    """
    ts = str(int(time.time()))
    ts_ms = str(int(time.time() * 1000))

    headers_copy = HEADERS.copy()
    headers_copy["timestamp"] = ts
    headers_copy["requesttimestampinms"] = ts_ms
    headers_copy["x-ts"] = ts
    return headers_copy


def check_mining_info():
    """
    Fungsi untuk mengecek kapan bisa panen dan sisa mineral.
    Endpoint: GET /member-asset/v6/game/mining/info
    """
    print("[*] Mengecek status ladang/mining...")
    url = "https://api.hifamiapp.com/member-asset/v6/game/mining/info?on_live=false"

    try:
        response = requests.get(url, headers=get_dynamic_headers())
        data = response.json()

        if data.get("code") == 0:
            dataset = data.get("data", {})
            mining_asset = dataset.get("mining_asset", {})
            mining_data = dataset.get("mining_data", {})

            mineral_num = mining_asset.get("mineral_num", 0)
            red_packet = mining_asset.get("red_packet_points", 0)

            curr_level = mining_data.get("curr_level", 0)
            max_level = mining_data.get("max_level", 0)
            mining_rate = mining_data.get("mining_rate", 0)

            load_cap = mining_data.get("load_cap", 0)
            load_cap_max = mining_data.get("load_cap_max", 0)
            remain_seconds = mining_data.get("remain_seconds", 0)

            # CLEAR SCREEN untuk efek Real-Time (opsional, tapi bagus buat display)
            # os.system('cls' if os.name == 'nt' else 'clear')

            print("-----------------------------------------")
            print(f"💰 Saldo Mineral     : {mineral_num}")
            print(f"🧧 Red Packet Points : {red_packet}")
            print(f"⭐ Level Saat Ini    : {curr_level}/{max_level}")
            print(f"⛏️  Mining Rate       : {mining_rate}/detik")
            print(f"🛒 Status Gerobak    : {load_cap}/{load_cap_max}")
            print("-----------------------------------------")

            if remain_seconds > 0:
                print(f"[+] Server menyuruh tunggu: {remain_seconds} detik untuk panen maksimal.")
            else:
                print(f"[+] Gerobak sudah bisa dipanen atau waktu tunggu habis!")

            return {
                "can_harvest": load_cap > 0,
                "remain_seconds": remain_seconds,
                "load_cap": load_cap
            }
        else:
            print(f"[-] Gagal mengecek info: {data.get('error', 'Error tidak diketahui')}")
            # Kemungkinan gagal karena business_sign/token salah atau basi
            print("[-] Bisa jadi token atau business_sign sudah basi!")
            return None
    except Exception as e:
        print(f"[-] Error request: {e}")
        return None

def harvest_mining():
    """
    Fungsi untuk memanen hasil.
    Endpoint: POST /member-asset/v6/game/mining/harvest
    """
    print("[*] Mencoba memanen (harvest)...")
    url = "https://api.hifamiapp.com/member-asset/v6/game/mining/harvest"

    try:
        response = requests.post(url, headers=get_dynamic_headers())
        data = response.json()

        if data.get("code") == 0:
            result = data.get("data", {})
            mineral = result.get("mineral_num", 0)
            rp = result.get("red_packet_points", 0)
            print(f"[+] PANEN BERHASIL! Dapet Mineral: {mineral}, Red Packet: {rp}")
            return True
        else:
            print(f"[-] Gagal memanen: {data.get('error', 'Error tidak diketahui')}")
            return False
    except Exception as e:
        print(f"[-] Error request: {e}")
        return False

def auto_farm_loop():
    """
    Fungsi utama yang akan terus mengulang pengecekan dan panen.
    """
    print("=========================================")
    print("      HiFami Auto Farm Script V1.0       ")
    print("=========================================")
    print("PERINGATAN: Script menggunakan header signature statis.")
    print("Jika aplikasi mensyaratkan token dinamis yang baru,")
    print("maka script ini akan mendapati error dari server.")
    print("=========================================\n")

    while True:
        info = check_mining_info()

        if info is None:
            print("[!] Berhenti. Ada error atau token invalid.")
            break

        if info["can_harvest"]:
            # Ada yang bisa dipanen
            success = harvest_mining()
            if success:
                print("[*] Panen sukses. Menunggu siklus selanjutnya...\n")
                time.sleep(10) # Jeda aman sebelum ngecek lagi
            else:
                print("[!] Gagal panen, token signature mungkin ditolak.")
                break
        else:
            wait_time = info["remain_seconds"]
            if wait_time > 0:
                print(f"[*] Deteksi auto-sleep dari server aktif!")
                print(f"[*] Menunggu (sleep) selama {wait_time} detik sampai gerobak penuh...")
                time.sleep(wait_time + random.randint(1, 3)) # Tambah sedikit random delay untuk keamanan
            else:
                print("[*] Gerobak kosong tapi waktu tunggu 0, menunggu 30 detik untuk menghindari spam...")
                time.sleep(30)


if __name__ == "__main__":
    auto_farm_loop()

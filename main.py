import json
import os

def muat_kb(nama_file="kb_kucing.json"):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), nama_file)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def forward_chaining(kb, fakta_awal):
    memori = list(fakta_awal)
    aturan_terpakai = set()
    riwayat_siklus = []
    jejak_alasan = {}

    siklus = 1
    while True:
        cocok = []
        for r in kb["aturan"]:
            if r["id"] in aturan_terpakai or r["maka"] in memori:
                continue

            mode = r.get("mode", "dan")
            if mode == "dan":
                terpenuhi = all(s in memori for s in r["jika"])
                syarat_aktif = list(r["jika"]) if terpenuhi else []
            elif mode == "atau":
                syarat_aktif = [s for s in r["jika"] if s in memori]
                terpenuhi = len(syarat_aktif) > 0
            else:
                terpenuhi = False
                syarat_aktif = []

            if terpenuhi:
                cocok.append((r, syarat_aktif))

        if not cocok:
            riwayat_siklus.append(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break

        r_pilih, syarat_aktif = cocok[0]
        memori.append(r_pilih["maka"])
        aturan_terpakai.add(r_pilih["id"])
        jejak_alasan[r_pilih["maka"]] = {
            "id": r_pilih["id"],
            "syarat": syarat_aktif
        }
        riwayat_siklus.append(f"Siklus {siklus}: {r_pilih['id']} -> {r_pilih['maka']}")
        siklus += 1

    return memori, riwayat_siklus, jejak_alasan

def cetak_alasan(fakta, jejak_alasan, indent="  "):
    if fakta in jejak_alasan:
        id_aturan = jejak_alasan[fakta]["id"]
        syarat_str = ", ".join(jejak_alasan[fakta]["syarat"])
        print(f"{indent}{fakta}  <- {id_aturan} ({syarat_str})")
        for s in jejak_alasan[fakta]["syarat"]:
            cetak_alasan(s, jejak_alasan, indent + "  ")

def main():
    kb = muat_kb("kb_kucing.json")

    print(kb["judul"])
    print("Jawab y/t.\n")

    semua_maka = {r["maka"] for r in kb["aturan"]}

    fakta_dasar = []
    for r in kb["aturan"]:
        for s in r["jika"]:
            if s not in semua_maka and s not in fakta_dasar:
                fakta_dasar.append(s)

    fakta_awal = []
    for i, fakta in enumerate(fakta_dasar, 1):
        jawaban = input(f"{i}. Apakah {fakta}? (y/t) > ").strip().lower()
        if jawaban == "y":
            fakta_awal.append(fakta)

    print()
    if fakta_awal:
        print(f"Fakta awal: {', '.join(fakta_awal)}")
    else:
        print("Fakta awal: tidak ada")
    print()

    # forward chaining
    memori, riwayat_siklus, jejak_alasan = forward_chaining(kb, fakta_awal)

    for baris in riwayat_siklus:
        print(baris)

    semua_jika = {s for r in kb["aturan"] for s in r["jika"]}
    kesimpulan_target = [r["maka"] for r in kb["aturan"] if r["maka"] not in semua_jika]
    kesimpulan_target = list(dict.fromkeys(kesimpulan_target))

    kesimpulan_didapat = [k for k in kesimpulan_target if k in memori]

    print()
    if kesimpulan_didapat:
        print(f"Kesimpulan: {', '.join(kesimpulan_didapat)}")
        print("Alasan:")
        for k in kesimpulan_didapat:
            cetak_alasan(k, jejak_alasan)
    else:
        print("Kesimpulan: tidak ada")

    print(f"\nCatatan: {kb['batas']}")

if __name__ == "__main__":
    main()

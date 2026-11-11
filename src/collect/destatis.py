"""Bronze : télécharge le répertoire officiel des communes allemandes (Destatis, GV-ISys) au 31/12/2025.

Contient pour chaque commune : population, superficie et coordonnées du centre.
"""
from paths import RAW, open_url

URL = ("https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/"
       "Administrativ/Archiv/GVAuszugJ/31122025_Auszug_GV.xlsx?__blob=publicationFile")

if __name__ == "__main__":
    target = RAW / "destatis_gemeinden_31122025.xlsx"
    with open_url(URL) as response:
        target.write_bytes(response.read())
    print(f"{target.name} : {target.stat().st_size / 1e6:.2f} Mo")

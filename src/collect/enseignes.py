"""Bronze : liste des magasins MediaMarkt et Saturn en Allemagne.

Source : le plan du site (sitemap) que chaque enseigne publie pour les robots d'indexation.
Un seul fichier par enseigne, aucune page magasin n'est ouverte. Le robots.txt des deux sites
n'interdit pas ces fichiers (vérifié le 11/11/2026).
"""
from urllib.request import Request

from paths import RAW, open_url

SITEMAPS = {
    "mediamarkt": "https://www.mediamarkt.de/sitemaps/sitemap-marketpages.xml",
    "saturn": "https://www.saturn.de/sitemaps/sitemap-marketpages.xml",
}
# Un robot honnête s'identifie
USER_AGENT = "eugenia-student-project/1.0 (github.com/romane13long-source/fnac-expansion-allemagne)"

if __name__ == "__main__":
    for brand, url in SITEMAPS.items():
        with open_url(Request(url, headers={"User-Agent": USER_AGENT})) as response:
            content = response.read()
        target = RAW / f"sitemap_{brand}.xml"
        target.write_bytes(content)
        print(f"{target.name} : {content.count(b'<loc>')} adresses")

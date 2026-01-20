# VFG-AI - Univerzális Kétmodelles AI Oktatási Asszisztens

## Áttekintés

A VFG-AI egy professzionális oktatási asszisztens alkalmazás, amely képes bármilyen tantárgy (matematika, fizika, kémia, földrajz, történelem stb.) kézzel írt vagy nyomtatott feladatlapjait feldolgozni egy speciális **kétmodelles "Látás → Érvelés" lánc** segítségével.

## Architektúra

### Kétmodelles Pipeline

1. **Modell 1 - A Szem (Vision Model)**
   - **Modell**: `gemini-2.0-flash`
   - **Feladat**: A kép fogadása és **1:1 arányú digitális rekonstrukció** létrehozása
   - **Kimenet**: Részletes szöveges leírás Markdown formátumban, amely tartalmazza:
     - Minden szöveget és számot
     - Grafikonok tengelyeit, görbéit, metszéspontjait
     - Ábrák és diagramok pontos leírását
     - Matematikai képleteket LaTeX formátumban
     - Táblázatok teljes tartalmát

2. **Modell 2 - Az Agy (Reasoning Model)**
   - **Modell**: `gemini-2.0-flash`
   - **Feladat**: A vision modell által generált digitális rekonstrukció és a felhasználó kérdésének feldolgozása
   - **Kimenet**: Pontos, tömör válasz magyar nyelven

### Miért fontos az 1:1 rekonstrukció?

Bár a Gemini modellek rendelkeznek vision képességgel, a kétmodelles megközelítés (Vision → Reasoning) biztosítja a legpontosabb eredményt. A vision modell olyan részletesen írja le a képet, mintha egy vak embernek magyarázná el, aki meg kell oldja a feladatot. Ez biztosítja, hogy a reasoning modell **teljes és strukturált információval** rendelkezzen a válaszadáshoz.

## Telepítés

### Előfeltételek

- Python 3.8 vagy újabb
- Gemini API kulcs (beszerezhető: [aistudio.google.com](https://aistudio.google.com))

### Lépések

1. **Repozitórium klónozása**
   ```bash
   git clone https://github.com/silentreaver/vfgai2.git
   cd vfgai2
   ```

2. **Virtuális környezet létrehozása (opcionális, de ajánlott)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Függőségek telepítése**
   ```bash
   pip install -r requirements.txt
   ```

4. **Környezeti változók beállítása**
   
   Hozz létre egy `.env` fájlt a projekt gyökérkönyvtárában:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Alkalmazás indítása**
   ```bash
   python app.py
   ```

6. **Böngészőben megnyitás**
   
   Nyisd meg a böngészőt és navigálj a következő címre:
   ```
   http://localhost:3000
   ```

## Használat

1. **Kép feltöltése**: Kattints a kamera ikonra vagy húzd be a képet
2. **Tantárgy kiválasztása** (opcionális): Válaszd ki a megfelelő tantárgyat a jobb felső sarokban
3. **Kérdés feltevése**: Írd be a kérdést a szövegmezőbe
4. **Válasz fogadása**: Az AI először feldolgozza a képet (Vision), majd válaszol (Reasoning)

## Tantárgy-specifikus utasítások

A `subjects/` mappában találhatók a tantárgy-specifikus utasítások Markdown formátumban:

- `chemistry.md` - Kémia
- `physics.md` - Fizika
- `geography.md` - Földrajz
- `history.md` - Történelem

Ezek az utasítások automatikusan betöltődnek, amikor kiválasztasz egy tantárgyat.

## Technológiai Stack

- **Backend**: Flask (Python)
- **AI API**: Google Gemini
- **Vision Model**: Gemini 2.0 Flash
- **Reasoning Model**: Gemini 2.0 Flash
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

## Projekt Struktúra

```
vfgai2/
├── app.py                 # Fő alkalmazás (API végpontok és modell láncolás)
├── requirements.txt       # Python függőségek
├── .env                   # Környezeti változók (ne commitold!)
├── subjects/              # Tantárgy-specifikus utasítások
│   ├── chemistry.md
│   ├── physics.md
│   ├── geography.md
│   └── history.md
├── templates/             # HTML sablonok
│   ├── index.html
│   └── mobile.html
└── static/                # Statikus fájlok (CSS, JS, képek)
```

## Fejlesztési Roadmap

- [ ] Több vision modell támogatása
- [ ] Kép előfeldolgozás (kontraszt, élesítés)
- [ ] Batch feldolgozás (több kép egyszerre)
- [ ] Exportálás PDF formátumba
- [ ] Felhasználói fiókok és történet mentése

## Licenc

MIT License

## Kapcsolat

GitHub: [@silentreaver](https://github.com/silentreaver)

---

**Megjegyzés**: Ez a projekt a Google Gemini API-t használja, amely ingyenes kvótával rendelkezik a Google AI Studio-ban. Nagy mennyiségű használathoz érdemes lehet fizetős csomagra váltani.

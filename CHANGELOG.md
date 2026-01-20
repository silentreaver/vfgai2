# Changelog

## 2026-01-20 - Vision Model 1:1 Rekonstrukció Optimalizálás

### Változtatások

#### 1. Vision Prompt Teljes Átírása
- **Előtte**: Egyszerű szövegkivonás és layout leírás
- **Utána**: Teljes 1:1 arányú digitális rekonstrukció
- **Cél**: A Maverick vision modell olyan részletesen írja le a képet, hogy a Groq Compound modell (amely nem rendelkezik vision képességgel) teljes mértékben megértse a tartalmat

#### 2. Új Vision Prompt Tartalma
```
Elemezd a képet függetlenül a tantárgytól. Készíts 1:1 arányú vizuális rekonstrukciót. 
A grafikonokat ne csak említsd meg, hanem írd le a tengelyeiket, a görbék alakját, 
a metszéspontokat és az adatokat úgy, mintha egy vak embernek magyaráznád el, 
akinek meg kell oldania a feladatot. A matematikai képleteket konvertáld LaTeX formátumba. 
Minden szöveget, számot, ábrát, diagramot, táblázatot és grafikus elemet írj le részletesen, 
hogy a következő AI modell teljes mértékben megértse a képet anélkül, hogy látná azt. 
Rekonstruálj mindent digitálisan, hogy az információ 100%-ban átadható legyen.
```

#### 3. Temperature Optimalizálás
- **Vision Model Temperature**: 0.1 → **0.0**
- **Indok**: Maximális pontosság és determinisztikus kimenet a rekonstrukcióhoz

#### 4. Kontextus Átadás Javítása
- **Előtte**: `"Kontextus a képből: ..."`
- **Utána**: `"DIGITÁLIS REKONSTRUKCIÓ A KÉPBŐL (teljes 1:1 arányú átírás, kezeld úgy mintha látnád a képet): ..."`
- **Indok**: Világosabb jelzés a reasoning modellnek, hogy ez nem csak kontextus, hanem teljes képhelyettesítés

#### 5. README.md Létrehozása
- Teljes dokumentáció a projekt céljáról
- Telepítési útmutató
- Architektúra leírás (kétmodelles pipeline)
- Használati útmutató

### Technikai Háttér

A Groq Compound modell **nem rendelkezik vision képességgel**, ezért kritikus fontosságú, hogy a Maverick vision modell olyan részletesen írja le a képet, mintha egy vak embernek kellene megoldania a feladatot. Ez a "digitális iker" (digital twin) megközelítés biztosítja, hogy:

1. **Nulla információvesztés**: Minden vizuális elem szöveggé alakul
2. **Teljes kontextus**: A reasoning modell ugyanannyi információval rendelkezik, mintha látná a képet
3. **Pontosság**: A 0.0 temperature determinisztikus kimenetet eredményez
4. **LaTeX támogatás**: Matematikai képletek professzionális formátumban

### Tesztelési Javaslatok

1. Tölts fel egy grafikont tartalmazó képet
2. Kérdezd meg: "Milyen függvény látható a grafikonon?"
3. Ellenőrizd, hogy a válasz tartalmazza:
   - A tengelyek leírását
   - A görbe alakját és metszéspontjait
   - A konkrét értékeket
   - LaTeX formátumú képleteket

### Következő Lépések

- [ ] Több vision modell tesztelése (pl. GPT-4 Vision, Claude Vision)
- [ ] Kép előfeldolgozás (kontraszt javítás, zajszűrés)
- [ ] A/B tesztelés a régi és új prompt között
- [ ] Felhasználói visszajelzések gyűjtése

## 2026-01-20 - Áttérés Google Gemini modellekre

### Változtatások

#### 1. Modellcsere
- **Vision Model**: Maverick → **Gemini 2.0 Flash**
- **Reasoning Model**: Groq Compound → **Gemini 2.0 Flash**
- **Indok**: A `vfg-ai` repozitórium alapján a Gemini modellek használata a cél, amelyek kiváló vision és reasoning képességekkel rendelkeznek.

#### 2. Technológiai Stack Frissítése
- **Google GenAI SDK** integrálása a Groq helyett.
- `requirements.txt` frissítve a `google-genai` csomaggal.
- API kulcs kezelés frissítve: `GEMINI_API_KEY` használata.

#### 3. 1:1 Konverziós Logika Megtartása
- Bár a Gemini natívan látja a képeket, megtartottuk a kétlépcsős folyamatot a maximális pontosság érdekében.
- A vision modell továbbra is a háttérben végzi a digitális rekonstrukciót.
- A reasoning modell a rekonstruált szöveget kapja meg, mintha ő látná a képet.

#### 4. Dokumentáció Frissítése
- README.md frissítve az új modellekkel és telepítési útmutatóval.

## 2026-01-20 - Frissítés Gemini 3 Pro modellre

### Változtatások

#### 1. Modell Frissítés
- **Vision Model**: Gemini 2.0 Flash → **Gemini 3 Pro**
- **Reasoning Model**: Gemini 2.0 Flash → **Gemini 3 Pro**
- **Indok**: A legújabb Gemini 3 Pro modell használata a maximális teljesítmény és pontosság érdekében.

#### 2. Dokumentáció Frissítése
- README.md frissítve az új Gemini 3 Pro modellekkel.

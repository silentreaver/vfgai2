# VFG-AI - Univerzális AI Oktatási Asszisztens

## Áttekintés

A VFG-AI egy professzionális oktatási asszisztens alkalmazás, amely képes bármilyen tantárgy (matematika, fizika, kémia, földrajz, történelem stb.) feladatainak feldolgozására a Google Gemini modell segítségével.

## Architektúra

Az alkalmazás egyetlen, nagy teljesítményű multimodális modellt használ, amely közvetlenül képes értelmezni a képeket és a szöveges kérdéseket.

- **Modell**: `gemini-3-pro-preview` (a legújabb Gemini modell)
- **Képességek**: Natív látás (Vision) és komplex érvelés (Reasoning) egyetlen lépésben.
- **Kimenet**: Pontos, tömör válasz magyar nyelven, LaTeX formátumú matematikai képletekkel.

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

2. **Függőségek telepítése**
   ```bash
   pip install -r requirements.txt
   ```

3. **Környezeti változók beállítása**
   
   Hozz létre egy `.env` fájlt a projekt gyökérkönyvtárában:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Alkalmazás indítása**
   ```bash
   python app.py
   ```

## Technológiai Stack

- **Backend**: Flask (Python)
- **AI API**: Google Gemini SDK
- **Modell**: Gemini 3 Pro Preview
- **Frontend**: HTML, CSS, JavaScript

## Licenc

MIT License

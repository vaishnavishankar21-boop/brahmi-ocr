# LipiLens

LipiLens reads ancient Brahmi letters from photos of stone inscriptions, and helps people explore and learn the script.

## What you can do in the app
- **Read a letter:** upload a photo of one letter and get its top 3 guesses in Devanagari and Latin.
- **Draw a letter:** draw a letter with a mouse or finger and LipiLens reads it.
- **Alphabet chart:** all 48 letters with real examples from stone.
- **Quiz:** practise on real stone crops, with a score and streak.
- **Edict of the day:** a short story about an Ashokan edict site.
- **Write your name in Brahmi:** type a name and see it in Brahmi letters.
- **Share card:** make a picture of your name or quiz score.
- **Other scripts:** see the same sounds in Devanagari, Kannada and Tamil.
- **Heritage map:** six places where Ashoka's edicts are carved.
- **Family tree:** how Brahmi led to modern scripts.

## How the model works
1. Draw all 48 Brahmi letters from the Noto Sans Brahmi font.
2. Add stone-style effects (tilt, noise, blur, chips) to make 4,800 training images.
3. Train a small CNN baseline on these images.
4. Crop real letters from Wikimedia Commons inscription photos and label them by hand.
5. Fine-tune the model on the real crops and test it on photos it has never seen.
6. Add pen-style drawn letters to the training so the model can also read drawings.

## Data
- 4,800 stone-style training images made from the 48 font letters.
- 2,880 drawn-style training images made from the same letters.
- 342 hand-labelled real letter crops from 22 inscription photos.
- Train/test split by photo: 249 crops for fine-tuning, and 93 crops from 8 held-out photos kept only for testing.

## Results
| Test | Top-1 accuracy | Top-3 accuracy |
|---|---|---|
| Font images (validation) | about 0.98 | - |
| Real stone, font-only model | 0.25 | 0.37 |
| Real stone, fine-tuned on real crops | about 0.68 | about 0.89 |
| Real stone, also trained on drawn letters | about 0.76 | about 0.91 |
| Drawn letters (validation) | about 0.94 | - |

Real-stone scores are measured on the 93 held-out test crops only. The drawn-letter score is an easy test, because the drawings come from the same 48 base letters as the training drawings. A quick manual check with my own hand (BA and THA) was 2 out of 2 correct, which is too small to count as a result.

## Limitations
- The held-out stone test set is small, so the numbers are rough estimates.
- Some test photos may show the same inscription from different angles, which can make the score slightly optimistic.
- Only single letters are recognised. Reading a full line is future work.
- Similar-looking letters (for example DDA, LLA and JHA) are still sometimes confused.
- The name, Kannada and Tamil pages are simplified. They have no retroflex letters, and Tamil merges sounds it has no separate letter for.
- The family tree is simplified, and scholars disagree on some details.

## Run it yourself
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```
The `data/` and `models/` folders are not in this repo. To rebuild them, put the Noto Sans Brahmi font in `data/fonts`, then run these in order:
`generate_clean.py`, `augment.py`, `generate_drawn.py`, `train_baseline.py`, `finetune_real.py`, `finetune_drawn.py`.
The real crops are labelled by hand with `crop_tool2.py`.

## Credits
Photos come from Wikimedia Commons. See `credits.txt` for each file's author and license. Letters are drawn with the Noto Sans Brahmi font. Edict facts were checked against Wikipedia's pages on the edicts of Ashoka.

## Status
Working demo. Next ideas: reading a whole line, and putting the app online.
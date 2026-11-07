# LipiLens

LipiLens reads Brahmi characters from photos of stone inscriptions.

## How it works
1. Draw all 48 Brahmi letters from the Noto Sans Brahmi font.
2. Add stone-style effects (tilt, noise, blur, chips) to make 4,800 training images.
3. Train a small CNN baseline on these images.
4. Crop real letters from Wikimedia Commons inscription photos and label them by hand.
5. Fine-tune the model on the real crops and test it on photos it has never seen.
6. Show each recognised letter in Latin and Devanagari using a transliteration table.

## Data
- 48 Brahmi letters rendered from the font, expanded to 4,800 stone-style training images.
- 342 hand-labelled real letter crops from 22 inscription photos.
- 249 real crops were used for fine-tuning. 93 crops from 8 photos the model never saw were kept for testing.

## Results
| Test | Top-1 accuracy | Top-3 accuracy |
|---|---|---|
| Font images (validation) | about 0.98 | - |
| Real stone crops, font-only model | 0.25 | 0.37 |
| Real stone crops, fine-tuned model | about 0.67 | about 0.89 |

The real-stone numbers are measured on the 93 test crops from 8 unseen photos. A font-only model scores very low on real stone, and adding real crops raised accuracy a lot.

## Limitations
- The test set is small (93 crops from 8 photos), so the numbers are rough estimates.
- Some test photos may show the same inscription from different angles, which can make the score slightly optimistic.
- Only isolated letters are recognised so far. Full-line segmentation is future work.
- Letters that look alike (for example DDA, LLA and JHA) are still sometimes confused.

## Project structure
- `src/` : scripts for generating data, training, testing and transliteration
- `credits.txt` : author and license for every photo used
- `requirements.txt` : Python packages

## Credits
Photos come from Wikimedia Commons. See `credits.txt` for each file's author and license. Letters are drawn with the Noto Sans Brahmi font.

## Status
Work in progress. Next: a web app where you upload a photo and get the letters.

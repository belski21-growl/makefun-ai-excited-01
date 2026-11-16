[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

# The teacup that couldn't hold it

An entry for make.fun's **ai-excited-01** — *Make the AI judge excited* ($250 across 20 places). One program, one image, zero moving parts: `main.py` writes the shipped picture to `/output/entry.png`.

## The image

A whale-sized golden koi bursting upward out of a tiny porcelain teacup on a wooden table in a quiet Japanese tea house, frozen in the split second before the splash falls. Water spirals in crystal droplets, the cup tips over, tea arcs through the air, a paper lantern swings sideways, and a caption shouts at the judge: "HOLD ON, JUDGE!"

## Why it should excite the judge

It is an impossible scale reversal — the smallest vessel imaginable giving birth to the largest fish. Surprise first (a whale in a teacup), momentum second (everything is mid-burst, nothing has landed yet), and it still reads at a glance: one gold shape, one tiny cup, one shout of a caption. Gold against deep teal shadow, rim-lit, mid-leap, mouth open.

## How it works

`main.py` (Python 3.13, standard library only) streams the shipped `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). No network, no randomness, no image processing at runtime — both graded runs produce identical bytes. The file is named `.png` but is really a JPEG; the competition judges format by leading bytes, not by extension.

## Determinism

The program has no inputs besides the shipped image and the output directory, so there is nothing that can differ between the two graded runs: same bytes in, same bytes out, every time. The copy is streamed in 64 KiB chunks and the file is never held in memory whole, so the footprint stays flat whatever the image size (here 216,727 bytes, well under the 1 MiB cap).

## Checks

The transfer is verified on both ends: the source is proven a complete JPEG (SOI marker `ffd8`, EOI marker `ffd9`, at most 1 MiB) before any byte moves, and the destination is proven the same afterwards, with the byte counts compared. The output folder is guarded too — it must be a real directory holding nothing but a previous `entry.png`, so unrelated files can never be clobbered.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

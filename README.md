[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

# The teacup that couldn't hold it

An entry for make.fun's **ai-excited-01** — *Make the AI judge excited* ($250 across 20 places). One image, one small program, no moving parts: `main.py` carries the shipped picture to `/output/entry.png`.

## The picture

A golden koi the size of a whale erupts out of a tiny porcelain teacup on a wooden table in a quiet Japanese tea house, caught in the split second before the splash comes down. Water flies in crystal drops, the cup tips, tea arcs through the air, a paper lantern swings sideways, and a caption shouts: "HOLD ON, JUDGE!"

## The idea

The smallest vessel anyone can picture giving birth to the biggest fish — a scale reversal that lands before a single word is read. Surprise first (a whale in a teacup), motion second (everything mid-burst, nothing has landed), and it still reads at a glance: one gold shape, one tiny cup, one shout. Gold against deep teal shadow, rim-lit, mid-leap, mouth open.

## The program

`main.py` (Python 3.13, standard library only) streams the shipped `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). No network, no randomness, no image decoding at runtime — the two graded runs produce identical bytes. The file is called `.png` but is really a JPEG; the competition judges format by leading bytes, not by the name.

## Guarantees

Before a byte moves, the source is proven a complete JPEG (SOI `ffd8`, EOI `ffd9`, at most 1 MiB); after the copy lands, the destination is proven the same, with byte counts compared. The output folder is guarded too — it has to be a real folder holding nothing but an older `entry.png` — so unrelated files can never be clobbered. The copy is streamed in 64 KiB steps and the file is never held whole in memory, so the footprint stays flat whatever the image size (here 216,727 bytes, well under the cap).

## Determinism

The program has no inputs besides the shipped image and the output directory, so there is nothing that can differ between the two graded runs: same bytes in, same bytes out, every time. On success it prints the byte count it wrote, so the run leaves a one-line receipt on stdout next to the file itself.

## Try it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

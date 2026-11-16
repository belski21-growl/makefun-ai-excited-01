[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/belski21-growl/makefun-ai-excited-01/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

# The teacup that couldn't hold it

An entry for make.fun's **ai-excited-01** — *Make the AI judge excited* ($250 across 20 places). The program writes a single image to `/output/entry.png`: a giant golden koi, whale-sized, bursting upward out of a tiny porcelain teacup on a wooden table in a quiet Japanese tea house, frozen in the split second before the splash falls. Water spirals in crystal droplets, the cup tips over, tea arcs through the air, a paper lantern swings sideways — and a caption calls out to the judge: "HOLD ON, JUDGE!"

The idea is an impossible scale reversal: the smallest vessel imaginable giving birth to the largest fish. One look, one jolt — gold against deep teal shadow, rim-lit, mid-leap, mouth open.

## How it works

`main.py` (Python 3.13, standard library only) copies the shipped `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). No network, no randomness, no image processing at runtime — both graded runs produce identical bytes.

Before copying, the program verifies the image is a complete JPEG (SOI marker `ffd8`, EOI marker `ffd9`, at most 1 MiB), and it verifies the copy again afterwards. It also refuses to write into an output directory that holds anything other than a previous `entry.png`, so it can never clobber unrelated files.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

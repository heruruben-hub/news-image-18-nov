# news-image-18-nov

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/heruruben-hub/news-image-18-nov/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/heruruben-hub/news-image-18-nov/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world news of Wednesday 18 November 2026, drawn pixel by pixel by a single Python program. A newspaper-style front page: a masthead naming the day, then six panels covering the day's biggest stories across regions and fields — the Shenzhen summit, the Gulf escalation, the Crimea bridge strike, the Alaska Senate result, the COP31 fossil-fuel row, and Nvidia's earnings.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is Python 3 standard library only, with no network, no clock and no randomness: it draws the page from scratch (embedded 5x7 bitmap font, hand-drawn icons, its own PNG encoder) and writes `entry.png` — 1024x1024, about 20 KB — to `$MAKEFUN_OUTPUT_DIR`, or to `/output` when that variable is unset. Run it twice and the two files are byte-identical.

## The six stories

Each panel is one story that happened, or was first reported, on Wednesday 18 November 2026:

1. **Asia — Diplomacy.** Xi Jinping and Vladimir Putin met in Shenzhen on the Wednesday of the APEC summit, a day before their planned three-way talks with Donald Trump (AFP / Associated Press reporting).
2. **Middle East — Conflict.** Iran sent drones at Ali Al Salem Air Base in Kuwait, which hosts US forces; Bahrain intercepted attacks, and US jets had just struck an Iranian missile launch site on Qeshm Island (CNN).
3. **Europe — War.** Ukraine struck the Kerch Bridge linking Russia to occupied Crimea for the second night in a row, shutting it down (international wire roundups of the day).
4. **Americas — Politics.** Democrat Mary Peltola defeated Republican incumbent Dan Sullivan in Alaska, giving Democrats a projected 56–44 majority in the incoming US Senate (Associated Press / Alaska Public Media).
5. **World — Climate.** The COP31 climate talks in Antalya, Türkiye entered their final days with a draft deal's fossil-fuel phase-out sharply dividing nations (summit reporting of the day).
6. **Tech — Business.** Nvidia's revenue doubled to $115.84 billion while its board ruled out reinstating Jensen Huang as CEO (company earnings coverage of the day).

---

Entered on [make.fun](https://make.fun/?ref=kh6903y0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards

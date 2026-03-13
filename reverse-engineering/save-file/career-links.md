# Career Link Index Map (Steam)

This table enumerates the **campaign** link table indices (`CCareerNodeLink[200]`) for the Steam `.bes` format.
It is derived from `references/Onslaught/Career.cpp` `level_structure` and validated against real Steam saves (node/link indices and `mToNode` targets match on disk).

Key invariants (campaign tree only):
- Node index `i` uses link indices `2*i` (lower) and `2*i+1` (higher).
- A link is considered unused when `mToNode == -1`.

| Link Idx | From Node | From World | Tier | To Node | To World | Normal Unlock Condition |
|---------:|----------:|----------:|------|--------:|---------:|------------------------|
| 0 | 0 | 100 | lower | 1 | 110 | Win (always) |
| 1 | 0 | 100 | higher | -1 | - | Win + all secondary objectives complete |
| 2 | 1 | 110 | lower | 2 | 200 | Win (always) |
| 3 | 1 | 110 | higher | -1 | - | Win + all secondary objectives complete |
| 4 | 2 | 200 | lower | 3 | 211 | Win (always) |
| 5 | 2 | 200 | higher | 4 | 212 | Win + all secondary objectives complete |
| 6 | 3 | 211 | lower | 5 | 221 | Win (always) |
| 7 | 3 | 211 | higher | 6 | 222 | Win + all secondary objectives complete |
| 8 | 4 | 212 | lower | 5 | 221 | Win (always) |
| 9 | 4 | 212 | higher | 6 | 222 | Win + all secondary objectives complete |
| 10 | 5 | 221 | lower | 7 | 231 | Win (always) |
| 11 | 5 | 221 | higher | 8 | 232 | Win + all secondary objectives complete |
| 12 | 6 | 222 | lower | 7 | 231 | Win (always) |
| 13 | 6 | 222 | higher | 8 | 232 | Win + all secondary objectives complete |
| 14 | 7 | 231 | lower | 9 | 300 | Win (always) |
| 15 | 7 | 231 | higher | -1 | - | Win + all secondary objectives complete |
| 16 | 8 | 232 | lower | 9 | 300 | Win (always) |
| 17 | 8 | 232 | higher | -1 | - | Win + all secondary objectives complete |
| 18 | 9 | 300 | lower | 10 | 311 | Win (always) |
| 19 | 9 | 300 | higher | 11 | 312 | Win + all secondary objectives complete |
| 20 | 10 | 311 | lower | 12 | 321 | Win (always) |
| 21 | 10 | 311 | higher | 13 | 322 | Win + all secondary objectives complete |
| 22 | 11 | 312 | lower | 12 | 321 | Win (always) |
| 23 | 11 | 312 | higher | 13 | 322 | Win + all secondary objectives complete |
| 24 | 12 | 321 | lower | 14 | 331 | Win (always) |
| 25 | 12 | 321 | higher | 15 | 332 | Win + all secondary objectives complete |
| 26 | 13 | 322 | lower | 14 | 331 | Win (always) |
| 27 | 13 | 322 | higher | 15 | 332 | Win + all secondary objectives complete |
| 28 | 14 | 331 | lower | 16 | 400 | Win (always) |
| 29 | 14 | 331 | higher | -1 | - | Win + all secondary objectives complete |
| 30 | 15 | 332 | lower | 16 | 400 | Win (always) |
| 31 | 15 | 332 | higher | -1 | - | Win + all secondary objectives complete |
| 32 | 16 | 400 | lower | 17 | 411 | Win (always) |
| 33 | 16 | 400 | higher | 18 | 412 | Win + all secondary objectives complete |
| 34 | 17 | 411 | lower | 19 | 421 | Win (always) |
| 35 | 17 | 411 | higher | 20 | 422 | Win + all secondary objectives complete |
| 36 | 18 | 412 | lower | 19 | 421 | Win (always) |
| 37 | 18 | 412 | higher | 20 | 422 | Win + all secondary objectives complete |
| 38 | 19 | 421 | lower | 21 | 431 | Win (always) |
| 39 | 19 | 421 | higher | 22 | 432 | Win + all secondary objectives complete |
| 40 | 20 | 422 | lower | 21 | 431 | Win (always) |
| 41 | 20 | 422 | higher | 22 | 432 | Win + all secondary objectives complete |
| 42 | 21 | 431 | lower | 23 | 500 | Win (always) |
| 43 | 21 | 431 | higher | -1 | - | Win + all secondary objectives complete |
| 44 | 22 | 432 | lower | 23 | 500 | Win (always) |
| 45 | 22 | 432 | higher | -1 | - | Win + all secondary objectives complete |
| 46 | 23 | 500 | lower | 24 | 511 | World 500 special-case: requires slot 62 (SUB) |
| 47 | 23 | 500 | higher | 25 | 512 | World 500 special-case: requires slot 61 (ROCKET) |
| 48 | 24 | 511 | lower | 26 | 521 | Win (always) |
| 49 | 24 | 511 | higher | 27 | 522 | Win + all secondary objectives complete |
| 50 | 25 | 512 | lower | 28 | 523 | Win (always) |
| 51 | 25 | 512 | higher | 29 | 524 | Win + all secondary objectives complete |
| 52 | 26 | 521 | lower | 30 | 600 | Win (always) |
| 53 | 26 | 521 | higher | -1 | - | Win + all secondary objectives complete |
| 54 | 27 | 522 | lower | 30 | 600 | Win (always) |
| 55 | 27 | 522 | higher | -1 | - | Win + all secondary objectives complete |
| 56 | 28 | 523 | lower | 30 | 600 | Win (always) |
| 57 | 28 | 523 | higher | -1 | - | Win + all secondary objectives complete |
| 58 | 29 | 524 | lower | 30 | 600 | Win (always) |
| 59 | 29 | 524 | higher | -1 | - | Win + all secondary objectives complete |
| 60 | 30 | 600 | lower | 31 | 611 | Win (always) |
| 61 | 30 | 600 | higher | 32 | 612 | Win + all secondary objectives complete |
| 62 | 31 | 611 | lower | 33 | 621 | Win (always) |
| 63 | 31 | 611 | higher | 34 | 622 | Win + all secondary objectives complete |
| 64 | 32 | 612 | lower | 33 | 621 | Win (always) |
| 65 | 32 | 612 | higher | 34 | 622 | Win + all secondary objectives complete |
| 66 | 33 | 621 | lower | 35 | 700 | Win (always) |
| 67 | 33 | 621 | higher | -1 | - | Win + all secondary objectives complete |
| 68 | 34 | 622 | lower | 35 | 700 | Win (always) |
| 69 | 34 | 622 | higher | -1 | - | Win + all secondary objectives complete |
| 70 | 35 | 700 | lower | 36 | 710 | Win (always) |
| 71 | 35 | 700 | higher | -1 | - | Win + all secondary objectives complete |
| 72 | 36 | 710 | lower | 37 | 720 | Win (always) |
| 73 | 36 | 710 | higher | -1 | - | Win + all secondary objectives complete |
| 74 | 37 | 720 | lower | 38 | 731 | Win (always) |
| 75 | 37 | 720 | higher | 39 | 732 | Win + all secondary objectives complete |
| 76 | 38 | 731 | lower | 40 | 741 | Win (always) |
| 77 | 38 | 731 | higher | -1 | - | Win + all secondary objectives complete |
| 78 | 39 | 732 | lower | 41 | 742 | Win (always) |
| 79 | 39 | 732 | higher | -1 | - | Win + all secondary objectives complete |
| 80 | 40 | 741 | lower | -1 | - | Win (always) |
| 81 | 40 | 741 | higher | -1 | - | Win + all secondary objectives complete |
| 82 | 41 | 742 | lower | 42 | 800 | Win (always) |
| 83 | 41 | 742 | higher | -1 | - | Win + all secondary objectives complete |
| 84 | 42 | 800 | lower | -1 | - | Win (always) |
| 85 | 42 | 800 | higher | -1 | - | Win + all secondary objectives complete |

# TGA startup-image contract (`textures/splash.tga`)

Status: active single-file contract — byte/header layout bounded
Date: 2026-08-22
Verdict: the sole installed TGA has an exact one-file header/pixel/trailer
contract; presentation timing and render fidelity remain open.
Evidence: MEASURED — the sole mirror-index image row and complete prior corpus
measurement.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`.

The installed tree contains one loose TGA file:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `textures/splash.tga` | 786,476 | `ede2de33fb12219bae679fa4f9167109c937c5c15283ae9a448d848c0c7e9a56` |

## Layout

- 18-byte TGA header;
- image type 2 (uncompressed true-colour);
- width 512, height 512;
- 24 bits per pixel;
- 786,432 bytes of pixel data (`512 * 512 * 3`);
- 26-byte `TRUEVISION-XFILE` trailer;
- no additional bytes.

The mirror's image decoder reports mode RGB and 512×512. The rebuild has a
bounded startup consumer for this exact input. This is a one-specimen contract,
not justification for a general TGA parser.

## Open questions

Startup timing, orientation/draw state, colour treatment, and sequencing against
the intro videos require retail runtime evidence. A decode match alone does not
prove presentation parity. No image bytes are tracked here.

# Build and dump matrix

Status: active, bounded archive identity census
Last updated: 2026-08-12
Evidence: MEASURED — local SHA-256, streamed member SHA-256, container
signatures, PE/XBE headers, ZIP central-directory data, one normalized Xbox
path/size manifest; SOURCE METADATA — explicitly labelled where local SHA-256
was not measured; UNKNOWN — ISO/CHD normalization, a tracked full Issue-7
XDVDFS content census, and archives not yet fully streamed.
Verdict: the archive already collapses several apparent releases into exact
duplicates while preserving real PC demo, PS2 regional, and Xbox regional
build differences. Container identity and logical-content identity remain
separate throughout.

## Mechanical owners

- [`archive-source-manifest-2026-08-11.tsv`](archive-source-manifest-2026-08-11.tsv)
  — 98 source/member rows, 31,119 bytes, SHA-256
  `50623fa5038ba1f09ec3200922fb69c33350a58c665286745af70a960089052b`
- [`archive-equivalence-groups-2026-08-11.tsv`](archive-equivalence-groups-2026-08-11.tsv)
  — 28 exact, structural, distinct, or open relation rows, 12,882 bytes,
  SHA-256
  `0bf610aa2a248e778c27c8d891a056c12b0155c139ce44fa2a0d414d5fdcf415`

The ignored working package is
`local-lab/archive-provenance-triage-20260811-v1/`. The two TSVs independently
import as ten-column schemas with 98/98 unique source keys and 28/28 unique
group IDs.

## Current release/build matrix

| Platform | Build or carrier | Current identity result | Technical status |
| --- | --- | --- | --- |
| PC | Retail V1.00 / Bundle V299 / ASUS V299 ISOs | Exact same 692,766,720-byte ISO, SHA-256 `1dc0d95c778105ae3cb1b0db9afa701fc3141ed4ee467cdd227811f6f4248c57` | One canonical retail disc, three labels |
| PC | Canonical retail executable | 2,506,752-byte `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` | Exact campaign pristine specimen |
| PC | 2003 demo ZIP | Distinct 2,510,848-byte executable, SHA-256 `d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2` | RTTI/vtable and virtual-target census complete; see [`DEMO_VS_RETAIL.md`](DEMO_VS_RETAIL.md) |
| PS2 | Europe retail | 3,615,948,800-byte inner ISO, SHA-256 `060d883b3b029c2be471d83f824b1fdf38520903f8ace47783d13e9dd399da52` | Same inner object across two different ZIP sources |
| PS2 | USA retail | 3,615,948,800-byte inner ISO, SHA-256 `3e1fffa905680acbc57bbf9388aa77bfe60c653afe6f48823247ade88bb87ce6` | Same inner object across two different ZIP sources; distinct from Europe |
| PS2 | Europe/USA CHD v5 | Direct and ZIP-contained CHDs match within each region | ISO equivalence remains open because CHD reports 2,448-byte units and a 4,322,188,800-byte logical image |
| PS2 | Four magazine/demo carriers | Exact shared `BEA.ELF` and `DATA0.NYO` | One proven BEA demo core across four distinct discs; whole carriers/modules not claimed identical |
| Xbox | USA Vimm ISO.7z / XISO.7z | Exact same outer 7z, SHA-256 `c58dd037ca6aa9baec9c58b65d1ea30ed305da86bca8e3e78fe7e2e38b31a959` | Preserve both provenance paths; XISO label is more accurate |
| Xbox | USA Vimm/Romsfun XISO | Same 3,034,054,656-byte inner XISO, SHA-256 `598095efa15e450f51b42ef81dea85f5dde0fe678b00bd9bfe88fd3770f1fa18` | Outer archives differ; logical inner object is exact |
| Xbox | Europe/Korea/USA extracted games | Same 3,823 normalized paths and 3,029,379,235 uncompressed bytes | Structure equal; every regional `Default.xbe` is distinct |
| Xbox | Korea versus USA extracted games | Only `default.xbe` differs by ZIP path/length/CRC screen | High-confidence triage, not a 3,822-file cryptographic equality claim |
| Xbox | Europe versus Korea/USA | XBE plus four `.aya` resources and `24.bik` differ | All six differing paths were SHA-256 checked where recorded |
| Xbox | Two magazine demo DVD9 images | Distinct Archive.org SHA-1 metadata | Issue-11's XDVDFS BEA payload is now parsed; Issue 7 remains outside this census |

## PC findings

The canonical retail ISO contains:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `EXE/BEA.exe` | 2,506,752 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| `All.gip` | 651,614,569 | `b0e6a2266a239c2cd9f0f45071c6e9b5dceb548c989714aad0712e4f353e617d` |

The PC demo outer ZIP is 110,691,112 bytes, SHA-256
`62e3f54a25af8049491c96123409f7ee6cc02d9326f4252d84606ffc136acd47`.
Its `All.gip` is 75,388,730 bytes, SHA-256
`90b16dc8df5669bb1ed2dbd09b450c30864047c9a536ecc31bfc6aa55cb66975`.
Both the executable and package differ from retail, so the demo is a real
comparison build rather than a launcher-only repack.

## PlayStation 2 findings

The Europe and USA retail ISOs have equal lengths but different SHA-256 values.
Region identity is therefore real at the full-image level. Filesystem-level
and executable/data deltas remain to be measured.

Four separate demo-disc carriers contain byte-identical BEA cores:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `BEA/BEA.ELF` | 3,671,888 | `5700b5d0b39554e49afe65e079ad8109fe6688c2aa5e6f0e0ed5afcefd034584` |
| `BEA/DATA0.NYO` | 290,716,828 | `6d503ca251a4b00a5ebcfa447036075f6b1d563c9f55ea7ab784e7db4b6f3d3c` |

This collapses the core demo build across those carriers while preserving the
carrier discs and their other modules as separate evidence.

The direct and ZIP-contained CHDs match within region, but no controlled
CHD-to-raw/ISO conversion has yet proved that an ISO and CHD reconstruct the
same logical disc. They remain related, not declared identical.

## Xbox findings

The Europe, Korea, and USA extracted-game archives share a normalized
lowercase-relative-path plus uncompressed-length manifest:

- 3,823 files;
- 3,029,379,235 uncompressed bytes;
- manifest SHA-256
  `4a000c0e51397fd3cbc923f3984a008396b51e13849f3ddd721f2903e432fe0b`.

That digest proves topology only. Each 2,973,696-byte regional XBE is distinct:

| Region | `Default.xbe` SHA-256 |
| --- | --- |
| Europe | `266387500a056752f45301a03772fa57fdc747cf0eda46d39bbb915c5db2f234` |
| Korea | `e8dcf2626cdf8efaa863db6b74a964bb54b20a58444a3dedf088c3e4ca2c3be9` |
| USA | `e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b` |

Korea and USA differ only in the XBE under the ZIP metadata screen. Europe
also differs in resources `612`, `856`, `863`, `goodie_124`, and cutscene
`24.bik`; those five Korea/USA pairs were cryptographically identical and the
Europe versions distinct. Configuration, default physics, and American/English
language samples are exact across all three regions.

This makes Korea-versus-USA XBE code the cheapest regional comparison: data is
held constant to the strongest currently measured boundary.

The January Issue-11 carrier is no longer wholly unparsed. Its XDVDFS game
partition supplied a 2,973,696-byte XBE, SHA-256
`ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9`,
with US-retail version `v1.00.16 - 23 August 2002` and PDB key `3D63DBEB4`.
US retail carries the same PDB signature at age 3. Their 1,166 unique shared
source coordinates are now installed in isolated, restore-tested Ghidra
projects; see the
[Xbox source-line/Ghidra checkpoint](binary-analysis/xbox-source-line-anchor-ghidra-2026-08-12.md).
The read-only
[function-correlation successor](binary-analysis/xbox-anchor-function-correlation-2026-08-12.md)
places 1,065 anchors into 379 one-to-one current function pairs and accounts for
all current functions by XBE section. It isolates 14 named SDK/middleware
sections but deliberately leaves the 6,723-function `.text` region mixed.

## Container rules and open work

- Equal inner hashes do not make outer ZIP/7z containers identical.
- Equal normalized path/size/CRC data is strong triage evidence, not SHA-256
  identity.
- `NOT_MEASURED` is an explicit unknown, never a wildcard or zero hash.
- Xbox DVD9 `CD001` may describe the DVD-video partition and does not itself
  parse XDVDFS. Issue 11 required an XDVDFS-aware read; Issue 7 remains open in
  this tracked census.
- Password-protected Windows packages remain unopened; credentials were not
  copied into the evidence package.
- Filename, uploader, region, or compressed-size claims never override measured
  container/member identity.

The smallest high-value successors are filesystem manifests for PC demo versus
retail and PS2 Europe versus USA; control-flow adjudication of the 101 Xbox
anchors outside current function bodies and ownership separation within mixed
`.text`; ELF structure and string analysis; and tracked promotion of the already
locally identified Issue-7 XDVDFS/XBE measurements plus its full filesystem
census.

# Texture and resource decode static contract

Status: active static map
Evidence class: reviewed Steam-binary instructions, xrefs, strings, and
decompilation

This contract routes texture and resource work without promoting static names
to runtime or pixel-fidelity claims.

| Lane | Retained anchors | Demonstrated boundary |
| --- | --- | --- |
| Resource ingress | `CChunkReader`, `CDXMemBuffer__Read`, mapped-file and path helpers | Resource streams and mapped buffers feed loaders; archive completeness is not proven. |
| Texture lifetime | `CTexture__FindTexture`, constructor/release paths, global list and fallback fields | Lookup, fallback and release topology are mapped; the concrete object layout is not. |
| Serialized node tree | `CTexture__NodePayloadRecordCtor`, node-type constructors, `CDXTexture__RegisterSerializedChunk`, compatibility/selection helpers | Node creation, structural predicates and selection flow are mapped; hidden ABI and payload schemas remain provisional. |
| Decode setup | scratch-table, header, job-descriptor and decode-block helpers | Descriptor and component-plane setup is visible statically; decoded output is not verified. |
| Codec fronts | memory/header dispatch plus PNG, JPEG, BMP and DDS helpers | Format routing and validation paths are mapped; library identity and format completeness are not. |
| JPEG entropy | `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__FlushEntropyBitWriter` | JPEG tables and entropy writing are a separate lane from inflate Huffman construction. |
| Zlib/inflate | `CDXTexture__InflateStream_ProcessZlibState`, code-state, dynamic-tree and table builders | Stream/state/table topology is mapped; exact `z_stream` layouts and decompression behavior are not. |
| Conversion and render handoff | packed-texel helpers, `CDXTexture__UploadDecodedBufferToSurface`, `CFastVB__RenderTriangleStripImmediate`, `CVBufTexture__DrawSpriteEx` | CPU conversion and render-facing handoff are visible; GPU upload and rendered pixels are not proven. |

The retained function notes and
[`mesh-resource-render-static-contract.md`](mesh-resource-render-static-contract.md)
provide address-level context. Asset exporters and the WinUI Asset Library may
use this map to choose parsers and label uncertainty, but successful extraction
or preview does not establish full retail-format support.

## Claim boundary

Static evidence does not prove runtime texture pixels, decompression/JPEG
correctness, Direct3D resource behavior, exact layouts, third-party source
identity, patch behavior, visual parity, or rebuild parity. Those require
focused parser tests, controlled copied-runtime evidence, or renderer-specific
validation as appropriate. Bulk decoded payloads remain local working data;
curated original assets may enter an owning implementation under the project's
confirmed permission and attribution boundary.

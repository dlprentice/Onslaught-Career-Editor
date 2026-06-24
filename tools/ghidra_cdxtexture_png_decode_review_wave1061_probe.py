#!/usr/bin/env python3
"""Validate Wave1061 CDXTexture PNG decode read-only review artifacts."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'subagents' / 'ghidra-static-reaudit' / 'wave1061-cdxtexture-png-decode-review'
PUBLIC_NOTE = ROOT / 'release' / 'readiness' / 'ghidra_cdxtexture_png_decode_review_wave1061_2026-06-01.md'
AGGREGATE_NOTE = ROOT / 'release' / 'readiness' / 'ghidra_wave900_plus_through_wave1061_recheck_2026-06-01.md'
PACKAGE_JSON = ROOT / 'package.json'
DOCS = [PUBLIC_NOTE, AGGREGATE_NOTE, ROOT/'reverse-engineering'/'binary-analysis'/'GHIDRA-REFERENCE.md', ROOT/'reverse-engineering'/'binary-analysis'/'static-reaudit-campaign.md', ROOT/'reverse-engineering'/'binary-analysis'/'functions'/'_index.md', ROOT/'reverse-engineering'/'binary-analysis'/'functions'/'FUNCTION_COVERAGE_STATE.md', ROOT/'reverse-engineering'/'binary-analysis'/'functions'/'DXTexture.cpp'/'_index.md', ROOT/'reverse-engineering'/'binary-analysis'/'MCP-MUTATION-BACKLOG.md', ROOT/'reverse-engineering'/'binary-analysis'/'function_mutation_tracking_state.json', ROOT/'developer_agent_state.json', ROOT/'documentation_agent_state.json', ROOT/'re_orchestrator_state.json']
LEDGER = ROOT/'reverse-engineering'/'binary-analysis'/'function_mutation_ledger.jsonl'
ATTEMPT_LOG = ROOT/'reverse-engineering'/'binary-analysis'/'function_mutation_attempt_log.jsonl'
QUEUE_JSON = ROOT/'subagents'/'ghidra-static-reaudit'/'queue'/'current'/'static-reaudit-queue.json'
QUEUE_TSV = ROOT/'subagents'/'ghidra-static-reaudit'/'queue'/'current'/'functions_quality.tsv'
BACKUP_SUMMARY = BASE/'backup-summary.json'
BACKUP_PATH = r'G:\GhidraBackups\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified'
TARGETS = {
    '0x00592dc2': ('CDXTexture__CreatePngDecodeContext', 'void * __stdcall CDXTexture__CreatePngDecodeContext(void * png_version_string, void * callback_context, void * error_callback, void * warning_callback)'),
    '0x00592eb6': ('CDXTexture__ParsePngHeadersUntilIdat', 'void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * png_decode_state, void * png_image_context)'),
    '0x00593024': ('CDXTexture__PreparePngRowOutputLayout', 'void __stdcall CDXTexture__PreparePngRowOutputLayout(void * png_decode_state, void * png_image_context)'),
    '0x00593043': ('CDXTexture__DecodePngPassRowsAndPostprocess', 'void __stdcall CDXTexture__DecodePngPassRowsAndPostprocess(void * png_decode_state, void * previous_row_workspace, void * current_row_workspace)'),
    '0x005933c6': ('CDXTexture__DecodePngRowsAcrossPasses', 'void __stdcall CDXTexture__DecodePngRowsAcrossPasses(void * png_decode_state, int * row_workspace_pointer_table)'),
    '0x00593411': ('CDXTexture__ResetPngDecodeContext', 'void __stdcall CDXTexture__ResetPngDecodeContext(void * png_decode_state, void * primary_row_workspace, void * secondary_row_workspace)'),
    '0x00593526': ('CDXTexture__ReleasePngDecodeContextHandles', 'void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * png_decode_context_slot, void * primary_row_workspace_slot, void * secondary_row_workspace_slot)'),
    '0x005950e0': ('CDXTexture__ComparePngSignatureBytes', 'int __stdcall CDXTexture__ComparePngSignatureBytes(void * signature_buffer, uint start_offset, uint bytes_to_check)'),
    '0x0059cd26': ('CDXTexture__ReadU32BigEndian', 'uint __stdcall CDXTexture__ReadU32BigEndian(void * source_buffer)'),
    '0x0059cd4b': ('CDXTexture__ReadChunkBytesAndUpdateCrc', 'void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * png_decode_state, void * destination_buffer, uint byte_count)'),
    '0x0059cd62': ('CDXTexture__IsPngChunkCrcInvalid', 'bool __stdcall CDXTexture__IsPngChunkCrcInvalid(void * png_decode_state)'),
    '0x0059d614': ('CDXTexture__FinalizePngChunkAndVerifyCrc', 'int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * png_decode_state, uint remaining_chunk_bytes)'),
    '0x0059d699': ('CDXTexture__ParsePngChunk_IHDR', 'void __stdcall CDXTexture__ParsePngChunk_IHDR(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059d879': ('CDXTexture__ParsePngChunk_PLTE', 'void __stdcall CDXTexture__ParsePngChunk_PLTE(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059d992': ('CDXTexture__ParsePngChunk_IEND', 'void __stdcall CDXTexture__ParsePngChunk_IEND(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059d9d8': ('CDXTexture__ParsePngChunk_gAMA', 'void __stdcall CDXTexture__ParsePngChunk_gAMA(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059dad9': ('CDXTexture__ParsePngChunk_sRGB', 'void __stdcall CDXTexture__ParsePngChunk_sRGB(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059dbbb': ('CDXTexture__ParsePngChunk_tRNS', 'void __stdcall CDXTexture__ParsePngChunk_tRNS(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059dd5c': ('CDXTexture__HandlePngChunkAfterIdat', 'void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * png_decode_state, void * png_image_context, uint chunk_data_length)'),
    '0x0059dda2': ('CDXTexture__ProcessIdatChunkDataAndQueueDecode', 'void __stdcall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * png_decode_state)'),
}
EXPECTED_TAGS = {
    '0x00592dc2': 'cdxtexture-png-decode-context-wave694',
    '0x00592eb6': 'cdxtexture-png-decode-context-wave694',
    '0x00593024': 'cdxtexture-png-decode-context-wave694',
    '0x00593043': 'cdxtexture-png-decode-context-wave694',
    '0x005933c6': 'cdxtexture-png-decode-context-wave694',
    '0x00593411': 'cdxtexture-png-decode-context-wave694',
    '0x00593526': 'cdxtexture-png-option-accessors-wave695',
    '0x005950e0': 'cdxtexture-png-decode-option-tail-wave698',
    '0x0059cd26': 'inflate-png-helper-head-wave713',
    '0x0059cd4b': 'inflate-png-helper-head-wave713',
    '0x0059cd62': 'inflate-png-helper-head-wave713',
    '0x0059d614': 'png-scanline-pass-head-wave714',
    '0x0059d699': 'png-chunk-parser-head-wave715',
    '0x0059d879': 'png-chunk-parser-head-wave715',
    '0x0059d992': 'png-chunk-parser-head-wave715',
    '0x0059d9d8': 'png-chunk-parser-head-wave715',
    '0x0059dad9': 'png-chunk-parser-head-wave715',
    '0x0059dbbb': 'png-chunk-parser-head-wave715',
    '0x0059dd5c': 'png-chunk-parser-head-wave715',
    '0x0059dda2': 'png-chunk-parser-head-wave715',
}
DOC_TOKENS = ('Wave1061','cdxtexture-png-decode-review-wave1061','0x00592dc2 CDXTexture__CreatePngDecodeContext','0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat','0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess','0x00593411 CDXTexture__ResetPngDecodeContext','0x0059d699 CDXTexture__ParsePngChunk_IHDR','0x0059d879 CDXTexture__ParsePngChunk_PLTE','0x0059d992 CDXTexture__ParsePngChunk_IEND','0x0059d9d8 CDXTexture__ParsePngChunk_gAMA','0x0059dad9 CDXTexture__ParsePngChunk_sRGB','0x0059dbbb CDXTexture__ParsePngChunk_tRNS','0x0059dd5c CDXTexture__HandlePngChunkAfterIdat','0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode','812/1408 = 57.67%','1168/1529 = 76.39%','500/500 = 100.00%','6246/6246 = 100.00%',BACKUP_PATH,'no mutation')
OVERCLAIMS = ('runtime png behavior proven','runtime image fidelity proven','fully reverse-engineered runtime','rebuild parity proven','exact source-layout identity proven')
def read_text(path: Path) -> str:
    if not path.is_file(): raise FileNotFoundError(path)
    return path.read_text(encoding='utf-8-sig')
def read_tsv(path: Path) -> list[dict[str,str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle: return list(csv.DictReader(handle, delimiter='\t'))
def read_json(path: Path) -> dict: return json.loads(read_text(path))
def read_jsonl(path: Path) -> list[dict]: return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]
def norm(addr: str) -> str:
    v = addr.strip().lower(); v = v[2:] if v.startswith('0x') else v; return '0x' + v.zfill(8)
def require(ok: bool, msg: str, failures: list[str]) -> None:
    if not ok: failures.append(msg)
def contains(text: str, token: str) -> bool: return token in text or token.replace('\\','\\\\') in text
def signature_counts(rows):
    commented = sum(1 for r in rows if r.get('comment','').strip())
    strict = sum(1 for r in rows if r.get('comment','').strip() and not r.get('signature','').startswith('undefined ') and not re.search(r'\bparam_\d+\b', r.get('signature','')))
    return commented, strict
def check_artifacts(f):
    expected = {'primary-metadata.tsv':20,'primary-tags.tsv':20,'primary-xrefs.tsv':55,'primary-instructions.tsv':1578,'primary-decompile/index.tsv':20,'context-metadata.tsv':20,'context-tags.tsv':20,'context-xrefs.tsv':51,'context-instructions.tsv':1892,'context-decompile/index.tsv':20}
    for rel,n in expected.items(): require(len(read_tsv(BASE/rel)) == n, f'{rel} row count mismatch', f)
    metadata = {norm(r['address']): r for r in read_tsv(BASE/'primary-metadata.tsv')}
    tags = {norm(r['address']): r for r in read_tsv(BASE/'primary-tags.tsv')}
    decomp = {norm(r['address']): r for r in read_tsv(BASE/'primary-decompile'/'index.tsv')}
    for addr,(name,sig) in TARGETS.items():
        row = metadata.get(addr); require(row is not None, f'missing metadata {addr}', f)
        if row: require(row.get('name') == name, f'name mismatch {addr}', f); require(row.get('signature') == sig, f'signature mismatch {addr}', f); require(row.get('status') == 'OK', f'metadata status mismatch {addr}', f)
        tagrow = tags.get(addr); require(tagrow is not None, f'missing tags {addr}', f)
        if tagrow:
            actual = set(tagrow.get('tags','').split(';')); require('static-reaudit' in actual, f'static-reaudit tag missing {addr}', f); require('png' in actual, f'png tag missing {addr}', f); require(EXPECTED_TAGS[addr] in actual, f'old wave tag missing {addr}', f); require(tagrow.get('status') == 'OK', f'tag status mismatch {addr}', f)
        dec = decomp.get(addr); require(dec is not None, f'missing decompile {addr}', f)
        if dec: require(dec.get('signature') == sig, f'decompile signature mismatch {addr}', f); require(dec.get('status') == 'OK', f'decompile status mismatch {addr}', f)
def check_logs(f):
    expected = {'primary-metadata.log':'targets=20 found=20 missing=0','primary-tags.log':'ExportFunctionTagsByAddress complete: rows=20 missing=0','primary-xrefs.log':'Wrote 55 rows','primary-instructions.log':'Wrote 1578 function-body instruction rows','primary-decompile.log':'targets=20 dumped=20 missing=0 failed=0','context-metadata.log':'targets=20 found=20 missing=0','context-tags.log':'ExportFunctionTagsByAddress complete: rows=20 missing=0','context-xrefs.log':'Wrote 51 rows','context-instructions.log':'Wrote 1892 function-body instruction rows','context-decompile.log':'targets=20 dumped=20 missing=0 failed=0'}
    for rel,tok in expected.items():
        text = read_text(BASE/rel); require(tok in text, f'missing log token {rel}: {tok}', f)
        for bad in ('LockException','MISSING:','BADNAME:','BADSIG:','FAIL:','missing=1','bad=1','failed=1'): require(bad not in text, f'unexpected failure token {rel}: {bad}', f)
def check_xrefs(f):
    joined = '\n'.join(' '.join(r.values()) for r in read_tsv(BASE/'primary-xrefs.tsv'))
    for tok in ('CDXTexture__DecodePngFromMemory','CDXTexture__ParsePngHeadersUntilIdat','CDXTexture__DecodePngPassRowsAndPostprocess','CDXTexture__ParsePngChunk_IHDR','CDXTexture__ParsePngChunk_PLTE','CDXTexture__ParsePngChunk_IEND','CDXTexture__ParsePngChunk_gAMA','CDXTexture__ParsePngChunk_sRGB','CDXTexture__ParsePngChunk_tRNS','CDXTexture__ProcessIdatChunkDataAndQueueDecode'): require(tok in joined, f'missing xref token {tok}', f)
def check_queue_backup(f):
    q = read_json(QUEUE_JSON); require(q.get('totalFunctions') == 6246, 'queue total mismatch', f); qs = q.get('qualitySignals', {}); require(qs.get('commentlessFunctionCount') == 0, 'commentless mismatch', f); require(qs.get('undefinedSignatureCount') == 0, 'undefined mismatch', f); require(qs.get('paramSignatureCount') == 0, 'param_N mismatch', f)
    rows = read_tsv(QUEUE_TSV); commented, strict = signature_counts(rows); require(len(rows) == 6246, 'quality TSV row count mismatch', f); require(commented == 6246, 'commented count mismatch', f); require(strict == 6246, 'strict clean count mismatch', f)
    b = read_json(BACKUP_SUMMARY); require(b.get('backupPath') == BACKUP_PATH, 'backup path mismatch', f); require(b.get('fileCount') == 19, 'backup file count mismatch', f); require(int(b.get('totalBytes',0)) == 174721927, 'backup bytes mismatch', f); require(b.get('missingCount') == 0, 'backup missing mismatch', f); require(b.get('extraCount') == 0, 'backup extra mismatch', f); require(b.get('diffCount') == 0, 'backup diff mismatch', f); require(b.get('hashDiffCount') == 0, 'backup hash diff mismatch', f)
def check_docs(f):
    for path in DOCS:
        text = read_text(path)
        for tok in DOC_TOKENS: require(contains(text, tok), f'missing token in {path.relative_to(ROOT)}: {tok}', f)
        lower = text.lower()
        for bad in OVERCLAIMS: require(bad not in lower, f'overclaim token in {path.relative_to(ROOT)}: {bad}', f)
    scripts = read_json(PACKAGE_JSON).get('scripts', {})
    require(scripts.get('test:ghidra-cdxtexture-png-decode-review-wave1061') == r'py -3 tools\ghidra_cdxtexture_png_decode_review_wave1061_probe.py --check', 'missing focused package script', f)
    require(scripts.get('test:ghidra-wave900-plus-through-wave1061-recheck') == r'py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1061 --check', 'missing aggregate package script', f)
    require(any(r.get('task') == 'Wave1061 cdxtexture png decode review' for r in read_jsonl(LEDGER)), 'missing ledger row', f)
    require(any(r.get('task') == 'Wave1061 cdxtexture png decode review' and r.get('attempt_id') == 20643 for r in read_jsonl(ATTEMPT_LOG)), 'missing attempt row', f)
def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); parser.parse_args(); failures=[]
    check_artifacts(failures); check_logs(failures); check_xrefs(failures); check_queue_backup(failures); check_docs(failures)
    if failures:
        print('Wave1061 CDXTexture PNG decode review probe: FAIL')
        for failure in failures: print(f'- {failure}')
        return 1
    print('Wave1061 CDXTexture PNG decode review probe: PASS'); return 0
if __name__ == '__main__': raise SystemExit(main())

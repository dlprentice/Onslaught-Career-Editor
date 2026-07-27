/* bea-d3d9-proxy -- back-buffer grab at Present.
 *
 * Why this exists: PrintWindow with PW_RENDERFULLCONTENT was MEASURED on
 * 2026-07-27 to return window chrome and a blank client area for this title,
 * because the Direct3D back buffer is never composited into the window DC. A
 * grab taken here sees exactly what the game handed to Present, needs no
 * foreground window, no focus and no synthetic input of any kind, and cannot be
 * raced by a window appearing over the game.
 *
 * The same hard rules as the rest of the proxy apply and are the reason for
 * every early return below:
 *   - no user32, no gdi32, no window, no dialog, no console, no thread, no
 *     input, no network;
 *   - any failure falls back to doing nothing at all, silently, so the game is
 *     never disturbed by a capture that could not be taken;
 *   - completely inert unless BEA_D3D9_SHOT is set.
 *
 * PNG is emitted with STORED (uncompressed) deflate blocks. That is a fully
 * conformant zlib stream and needs no compression library, so this file adds no
 * dependency to a DLL that is injected into a retail game. Files are large and
 * that is deliberate: the capture volume is bounded by BEA_D3D9_SHOTMAX and the
 * output goes to a drive chosen for having the room.
 */

#include "proxy.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

/* ------------------------------------------------------------------ config */

int bea_shot_enabled = 0;

/* `shot_enabled` is the file-local mirror of bea_shot_enabled, which proxy.c and
 * wrap.c read. Kept separate so a failure inside a grab can kill grabbing
 * without unwinding the rest of the proxy's enablement. */
static int shot_enabled;

#define BEA_SHOT_SPECMAX 32
#define BEA_SHOT_CELLS 4          /* 4x4 signature grid */

typedef struct {
    unsigned lo, hi, step;
} ShotRange;

static ShotRange shot_spec[BEA_SHOT_SPECMAX];
static int shot_specN;
static int shot_spec_all;

static int shot_mode_change;      /* 1 => write on signature change */
static unsigned shot_every = 15;  /* candidate cadence in `change` mode */
static unsigned shot_max = 64;    /* hard cap on images written */
static unsigned shot_thresh = 6;  /* per-cell channel delta that counts as a change */
static unsigned shot_written;
static unsigned shot_fail_streak;
static int shot_dead;             /* set after repeated failure; never retried */

static wchar_t shot_dir[MAX_PATH * 2];
static FILE *shot_manifest;

/* Cached read-back surface. D3DPOOL_SYSTEMMEM, so it survives Reset and does not
 * have to be released before one -- unlike anything in D3DPOOL_DEFAULT, which is
 * exactly the trap the vertex-buffer wrappers exist to avoid. */
static IDirect3DSurface9 *shot_sys;
static UINT shot_sys_w, shot_sys_h;
static D3DFORMAT shot_sys_fmt;

/* D3DPOOL_DEFAULT intermediate for the StretchRect resolve path. Unlike the
 * SYSTEMMEM surface this one MUST be released before a Reset, or Reset fails
 * with D3DERR_INVALIDCALL -- exactly the trap the vertex-buffer wrappers were
 * written to avoid. bea_shot_reset drops it. */
static IDirect3DSurface9 *shot_rt;
static int shot_desc_logged;
static int shot_resolve_logged;

/* Previous written frame's 4x4x3 cell means, for change detection. */
static int shot_prev_valid;
static unsigned char shot_prev_cell[BEA_SHOT_CELLS * BEA_SHOT_CELLS * 3];

/* ------------------------------------------------------------ env plumbing */

static int shot_env(const wchar_t *name, wchar_t *out, DWORD cch)
{
    DWORD n = GetEnvironmentVariableW(name, out, cch);
    return (n > 0 && n < cch);
}

static unsigned shot_env_uint(const wchar_t *name, unsigned dflt)
{
    wchar_t buf[64];
    if (!shot_env(name, buf, 64) || !buf[0])
        return dflt;
    return (unsigned)wcstoul(buf, NULL, 0);
}

/* "12" | "40-90" | "0-600/30" | comma-separated | "all" | "change" */
static void shot_parse_spec(const wchar_t *w)
{
    char s[512];
    size_t i;
    char *p;

    for (i = 0; i + 1 < sizeof(s) && w[i]; ++i)
        s[i] = (w[i] > 0 && w[i] < 127) ? (char)w[i] : '?';
    s[i] = 0;
    for (p = s; *p; ++p)
        if (*p >= 'A' && *p <= 'Z')
            *p += 32;

    if (!strcmp(s, "all")) {
        shot_spec_all = 1;
        return;
    }
    if (!strcmp(s, "change")) {
        shot_mode_change = 1;
        return;
    }

    p = s;
    while (*p && shot_specN < BEA_SHOT_SPECMAX) {
        char *end;
        unsigned lo, hi, step = 1;
        while (*p == ',' || *p == ' ')
            ++p;
        if (!*p)
            break;
        lo = (unsigned)strtoul(p, &end, 10);
        if (end == p) {                 /* not a number: skip the token */
            while (*p && *p != ',')
                ++p;
            continue;
        }
        p = end;
        hi = lo;
        if (*p == '-') {
            ++p;
            hi = (unsigned)strtoul(p, &end, 10);
            p = end;
        }
        if (*p == '/') {
            ++p;
            step = (unsigned)strtoul(p, &end, 10);
            p = end;
            if (!step)
                step = 1;
        }
        shot_spec[shot_specN].lo = lo;
        shot_spec[shot_specN].hi = hi;
        shot_spec[shot_specN].step = step;
        ++shot_specN;
    }
}

void bea_shot_init(void)
{
    wchar_t spec[512];
    SYSTEMTIME st;
    wchar_t base[MAX_PATH * 2];
    wchar_t mpath[MAX_PATH * 2];

    if (!shot_env(L"BEA_D3D9_SHOT", spec, 512) || !spec[0] ||
        (spec[0] == L'0' && !spec[1]))
        return;

    shot_parse_spec(spec);
    if (!shot_spec_all && !shot_mode_change && shot_specN == 0)
        return;                       /* nothing selectable: stay inert */

    shot_every = shot_env_uint(L"BEA_D3D9_SHOTEVERY", 15);
    if (!shot_every)
        shot_every = 1;
    shot_max = shot_env_uint(L"BEA_D3D9_SHOTMAX", 64);
    shot_thresh = shot_env_uint(L"BEA_D3D9_SHOTTHRESH", 6);
    if (!shot_max)
        return;

    if (!shot_env(L"BEA_D3D9_SHOTDIR", base, MAX_PATH * 2) || !base[0])
        wcscpy(base, L"G:\\bea-d3d9-shots");

    GetLocalTime(&st);
    _snwprintf(shot_dir, MAX_PATH * 2 - 1, L"%s\\%04u%02u%02u-%02u%02u%02u-%lu",
               base, st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute,
               st.wSecond, (unsigned long)GetCurrentProcessId());
    shot_dir[MAX_PATH * 2 - 1] = 0;

    CreateDirectoryW(base, NULL);
    if (!CreateDirectoryW(shot_dir, NULL) &&
        GetLastError() != ERROR_ALREADY_EXISTS)
        return;                       /* cannot write: stay inert, silently */

    _snwprintf(mpath, MAX_PATH * 2 - 1, L"%s\\manifest.csv", shot_dir);
    mpath[MAX_PATH * 2 - 1] = 0;
    shot_manifest = _wfopen(mpath, L"wb");
    if (!shot_manifest)
        return;
    setvbuf(shot_manifest, NULL, _IOLBF, 4096);
    fprintf(shot_manifest,
            "frame,written,file,w,h,d3dfmt,meanR,meanG,meanB,maxCellDelta\n");
    fflush(shot_manifest);

    shot_enabled = 1;
    bea_shot_enabled = 1;
}

/* --------------------------------------------------------------- PNG output */

static unsigned shot_crc_tab[256];
static int shot_crc_ready;

static void shot_crc_init(void)
{
    unsigned n, c, k;
    for (n = 0; n < 256; ++n) {
        c = n;
        for (k = 0; k < 8; ++k)
            c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
        shot_crc_tab[n] = c;
    }
    shot_crc_ready = 1;
}

static unsigned shot_crc(unsigned crc, const unsigned char *b, size_t n)
{
    size_t i;
    crc ^= 0xFFFFFFFFu;
    for (i = 0; i < n; ++i)
        crc = shot_crc_tab[(crc ^ b[i]) & 0xFF] ^ (crc >> 8);
    return crc ^ 0xFFFFFFFFu;
}

static void shot_be32(unsigned char *p, unsigned v)
{
    p[0] = (unsigned char)(v >> 24);
    p[1] = (unsigned char)(v >> 16);
    p[2] = (unsigned char)(v >> 8);
    p[3] = (unsigned char)v;
}

static void shot_chunk(FILE *f, const char *type, const unsigned char *data,
                       unsigned len)
{
    unsigned char hdr[8];
    unsigned crc;
    shot_be32(hdr, len);
    memcpy(hdr + 4, type, 4);
    fwrite(hdr, 1, 8, f);
    if (len)
        fwrite(data, 1, len, f);
    crc = shot_crc(0, (const unsigned char *)type, 4);
    if (len)
        crc = shot_crc(crc, data, len);
    shot_be32(hdr, crc);
    fwrite(hdr, 1, 4, f);
}

/* raw = h rows of (1 filter byte + w*3 RGB bytes) */
static int shot_write_png(const wchar_t *path, unsigned w, unsigned h,
                          const unsigned char *raw, size_t rawlen)
{
    FILE *f;
    unsigned char ihdr[13];
    unsigned char *z;
    size_t zn = 0, off = 0;
    unsigned a = 1, b = 0;
    size_t i;
    static const unsigned char sig[8] = { 137, 80, 78, 71, 13, 10, 26, 10 };

    if (!shot_crc_ready)
        shot_crc_init();

    /* zlib: 2 header bytes + one 5-byte stored-block header per <=65535 bytes
     * + the data + a 4-byte Adler-32. */
    z = (unsigned char *)malloc(rawlen + (rawlen / 65535 + 2) * 5 + 8);
    if (!z)
        return 0;
    z[zn++] = 0x78;                   /* CM=8, CINFO=7 */
    z[zn++] = 0x01;                   /* FCHECK so (0x78<<8|0x01) % 31 == 0 */
    while (off < rawlen) {
        size_t chunk = rawlen - off;
        int final;
        if (chunk > 65535)
            chunk = 65535;
        final = (off + chunk >= rawlen);
        z[zn++] = (unsigned char)(final ? 1 : 0);
        z[zn++] = (unsigned char)(chunk & 0xFF);
        z[zn++] = (unsigned char)(chunk >> 8);
        z[zn++] = (unsigned char)(~chunk & 0xFF);
        z[zn++] = (unsigned char)((~chunk >> 8) & 0xFF);
        memcpy(z + zn, raw + off, chunk);
        zn += chunk;
        off += chunk;
    }
    if (rawlen == 0) {                /* degenerate, but must still be legal */
        z[zn++] = 1; z[zn++] = 0; z[zn++] = 0; z[zn++] = 0xFF; z[zn++] = 0xFF;
    }
    for (i = 0; i < rawlen; ++i) {
        a = (a + raw[i]) % 65521;
        b = (b + a) % 65521;
    }
    shot_be32(z + zn, (b << 16) | a);
    zn += 4;

    f = _wfopen(path, L"wb");
    if (!f) {
        free(z);
        return 0;
    }
    fwrite(sig, 1, 8, f);
    shot_be32(ihdr, w);
    shot_be32(ihdr + 4, h);
    ihdr[8] = 8;                      /* bit depth */
    ihdr[9] = 2;                      /* colour type: truecolour RGB */
    ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
    shot_chunk(f, "IHDR", ihdr, 13);
    shot_chunk(f, "IDAT", z, (unsigned)zn);
    shot_chunk(f, "IEND", NULL, 0);
    fclose(f);
    free(z);
    return 1;
}

/* ------------------------------------------------------- format conversion */

/* Returns 0 if the format is one this proxy will not guess at. Nothing is ever
 * decoded from a format whose channel order was assumed. */
static int shot_row_to_rgb(D3DFORMAT fmt, const unsigned char *src, unsigned w,
                           unsigned char *dst)
{
    unsigned x;
    switch (fmt) {
    case D3DFMT_A8R8G8B8:
    case D3DFMT_X8R8G8B8:
        for (x = 0; x < w; ++x) {     /* memory order B,G,R,A */
            dst[x * 3 + 0] = src[x * 4 + 2];
            dst[x * 3 + 1] = src[x * 4 + 1];
            dst[x * 3 + 2] = src[x * 4 + 0];
        }
        return 1;
    case D3DFMT_A8B8G8R8:
    case D3DFMT_X8B8G8R8:
        for (x = 0; x < w; ++x) {
            dst[x * 3 + 0] = src[x * 4 + 0];
            dst[x * 3 + 1] = src[x * 4 + 1];
            dst[x * 3 + 2] = src[x * 4 + 2];
        }
        return 1;
    case D3DFMT_R8G8B8:
        for (x = 0; x < w; ++x) {     /* memory order B,G,R */
            dst[x * 3 + 0] = src[x * 3 + 2];
            dst[x * 3 + 1] = src[x * 3 + 1];
            dst[x * 3 + 2] = src[x * 3 + 0];
        }
        return 1;
    case D3DFMT_R5G6B5:
        for (x = 0; x < w; ++x) {
            unsigned p = (unsigned)src[x * 2] | ((unsigned)src[x * 2 + 1] << 8);
            unsigned r = (p >> 11) & 0x1F, g = (p >> 5) & 0x3F, bl = p & 0x1F;
            dst[x * 3 + 0] = (unsigned char)((r * 255 + 15) / 31);
            dst[x * 3 + 1] = (unsigned char)((g * 255 + 31) / 63);
            dst[x * 3 + 2] = (unsigned char)((bl * 255 + 15) / 31);
        }
        return 1;
    case D3DFMT_X1R5G5B5:
    case D3DFMT_A1R5G5B5:
        for (x = 0; x < w; ++x) {
            unsigned p = (unsigned)src[x * 2] | ((unsigned)src[x * 2 + 1] << 8);
            unsigned r = (p >> 10) & 0x1F, g = (p >> 5) & 0x1F, bl = p & 0x1F;
            dst[x * 3 + 0] = (unsigned char)((r * 255 + 15) / 31);
            dst[x * 3 + 1] = (unsigned char)((g * 255 + 15) / 31);
            dst[x * 3 + 2] = (unsigned char)((bl * 255 + 15) / 31);
        }
        return 1;
    case D3DFMT_A2R10G10B10:
        for (x = 0; x < w; ++x) {
            unsigned p = (unsigned)src[x * 4] | ((unsigned)src[x * 4 + 1] << 8) |
                         ((unsigned)src[x * 4 + 2] << 16) |
                         ((unsigned)src[x * 4 + 3] << 24);
            dst[x * 3 + 0] = (unsigned char)(((p >> 20) & 0x3FF) >> 2);
            dst[x * 3 + 1] = (unsigned char)(((p >> 10) & 0x3FF) >> 2);
            dst[x * 3 + 2] = (unsigned char)((p & 0x3FF) >> 2);
        }
        return 1;
    default:
        return 0;
    }
}

/* ------------------------------------------------------------- frame gating */

static int shot_frame_selected(unsigned frame)
{
    int i;
    if (shot_spec_all)
        return 1;
    for (i = 0; i < shot_specN; ++i) {
        const ShotRange *r = &shot_spec[i];
        if (frame >= r->lo && frame <= r->hi &&
            ((frame - r->lo) % r->step) == 0)
            return 1;
    }
    return 0;
}

/* A frame is a CANDIDATE if it is worth paying a VRAM read-back for. In change
 * mode that is a fixed cadence; otherwise it is exactly the listed frames. The
 * read-back is the expensive part -- doing it every frame would change the
 * game's timing, and timing is a measured quantity on this project. */
static int shot_frame_candidate(unsigned frame)
{
    if (shot_mode_change)
        return (frame % shot_every) == 0 || shot_frame_selected(frame);
    return shot_frame_selected(frame);
}

/* -------------------------------------------------------------- the grab */

/* MUST be called BEFORE the real Reset. The resolve target is D3DPOOL_DEFAULT,
 * and the application is required to release every DEFAULT-pool resource before
 * a Reset -- one held by an instrument makes Reset fail with
 * D3DERR_INVALIDCALL, which would break the game on every mode change. */
void bea_shot_pre_reset(void)
{
    if (shot_rt) {
        shot_rt->lpVtbl->Release(shot_rt);
        shot_rt = NULL;
    }
}

void bea_shot_reset(void)
{
    /* The back buffer's size or format may have changed. The SYSTEMMEM surface
     * survives Reset, but it may no longer match, so drop it and let the next
     * grab recreate it from the new descriptor. */
    if (shot_sys) {
        shot_sys->lpVtbl->Release(shot_sys);
        shot_sys = NULL;
    }
    shot_sys_w = shot_sys_h = 0;
    shot_prev_valid = 0;
    shot_desc_logged = 0;
}

/* Called from DLL_PROCESS_DETACH, so it must not call into another DLL.
 *
 * The cached SYSTEMMEM surface is DELIBERATELY LEAKED here rather than
 * released. Release() is a call into the real d3d9.dll under the loader lock,
 * at a point where that DLL may already have been detached; doing it crashed
 * the self-test host at exit with the image already correctly written. The
 * process is terminating, so the leak costs nothing, and a capture tool must
 * never be the reason the game fails to shut down cleanly. */
void bea_shot_close(void)
{
    shot_enabled = 0;
    shot_rt = NULL;
    if (shot_manifest) {
        fprintf(shot_manifest, "# written=%u dead=%d leaked-surface=%d\n",
                shot_written, shot_dead, shot_sys ? 1 : 0);
        fclose(shot_manifest);
        shot_manifest = NULL;
    }
    shot_sys = NULL;
}

static void shot_fail(const char *why, HRESULT hr)
{
    ++shot_fail_streak;
    if (shot_manifest) {
        fprintf(shot_manifest, "# fail %s hr=0x%08lX streak=%u\n", why,
                (unsigned long)hr, shot_fail_streak);
        fflush(shot_manifest);
    }
    bea_logf("G fail %s hr=0x%08lX\n", why, (unsigned long)hr);
    if (shot_fail_streak >= 8) {
        shot_dead = 1;                /* stop trying; never disturb the game */
        bea_logf("G disabled after %u consecutive failures\n", shot_fail_streak);
    }
}

void bea_shot_present(IDirect3DDevice9 *real, unsigned frame)
{
    IDirect3DSurface9 *bb = NULL;
    D3DSURFACE_DESC desc;
    D3DLOCKED_RECT lr;
    HRESULT hr;
    unsigned char *raw = NULL;
    size_t rowlen, rawlen;
    unsigned y, x, cx, cy;
    double sum[3];
    unsigned char cell[BEA_SHOT_CELLS * BEA_SHOT_CELLS * 3];
    double cellsum[BEA_SHOT_CELLS * BEA_SHOT_CELLS][3];
    unsigned cellcnt[BEA_SHOT_CELLS * BEA_SHOT_CELLS];
    int maxdelta = 255, write, i;
    wchar_t path[MAX_PATH * 2];
    char nameA[64];

    if (!shot_enabled || shot_dead || !real)
        return;
    if (shot_written >= shot_max)
        return;
    if (!shot_frame_candidate(frame))
        return;

    hr = real->lpVtbl->GetBackBuffer(real, 0, 0, D3DBACKBUFFER_TYPE_MONO, &bb);
    if (FAILED(hr) || !bb) {
        shot_fail("getbackbuffer", hr);
        return;
    }
    hr = bb->lpVtbl->GetDesc(bb, &desc);
    if (FAILED(hr)) {
        bb->lpVtbl->Release(bb);
        shot_fail("getdesc", hr);
        return;
    }

    if (!shot_sys || shot_sys_w != desc.Width || shot_sys_h != desc.Height ||
        shot_sys_fmt != desc.Format) {
        if (shot_sys) {
            shot_sys->lpVtbl->Release(shot_sys);
            shot_sys = NULL;
        }
        hr = real->lpVtbl->CreateOffscreenPlainSurface(
            real, desc.Width, desc.Height, desc.Format, D3DPOOL_SYSTEMMEM,
            &shot_sys, NULL);
        if (FAILED(hr) || !shot_sys) {
            shot_sys = NULL;
            bb->lpVtbl->Release(bb);
            shot_fail("createoffscreen", hr);
            return;
        }
        shot_sys_w = desc.Width;
        shot_sys_h = desc.Height;
        shot_sys_fmt = desc.Format;
    }

    if (!shot_desc_logged) {
        shot_desc_logged = 1;
        bea_logf("G backbuffer %ux%u fmt=%u type=%u pool=%u usage=0x%lX"
                 " ms=%u msq=%lu\n",
                 (unsigned)desc.Width, (unsigned)desc.Height,
                 (unsigned)desc.Format, (unsigned)desc.Type,
                 (unsigned)desc.Pool, (unsigned long)desc.Usage,
                 (unsigned)desc.MultiSampleType,
                 (unsigned long)desc.MultiSampleQuality);
        if (shot_manifest)
            fprintf(shot_manifest,
                    "# backbuffer %ux%u fmt=%u type=%u pool=%u usage=0x%lX"
                    " ms=%u msq=%lu\n",
                    (unsigned)desc.Width, (unsigned)desc.Height,
                    (unsigned)desc.Format, (unsigned)desc.Type,
                    (unsigned)desc.Pool, (unsigned long)desc.Usage,
                    (unsigned)desc.MultiSampleType,
                    (unsigned long)desc.MultiSampleQuality);
    }

    hr = real->lpVtbl->GetRenderTargetData(real, bb, shot_sys);
    if (FAILED(hr)) {
        /* GetRenderTargetData refuses a multisampled source, and refuses some
         * drivers' swap-chain surfaces outright. StretchRect into a plain,
         * single-sampled render target of the same size resolves both: it is
         * the same copy the runtime would do, one step earlier. */
        HRESULT hr2 = E_FAIL;
        if (!shot_rt) {
            hr2 = real->lpVtbl->CreateRenderTarget(real, desc.Width, desc.Height,
                                                   desc.Format,
                                                   D3DMULTISAMPLE_NONE, 0,
                                                   FALSE, &shot_rt, NULL);
            if (FAILED(hr2))
                shot_rt = NULL;
        }
        if (shot_rt) {
            hr2 = real->lpVtbl->StretchRect(real, bb, NULL, shot_rt, NULL,
                                            D3DTEXF_NONE);
            if (SUCCEEDED(hr2))
                hr2 = real->lpVtbl->GetRenderTargetData(real, shot_rt, shot_sys);
        }
        if (FAILED(hr2)) {
            bb->lpVtbl->Release(bb);
            bea_logf("G resolve-fallback failed hr=0x%08lX\n",
                     (unsigned long)hr2);
            shot_fail("getrendertargetdata", hr);
            return;
        }
        if (!shot_resolve_logged) {
            shot_resolve_logged = 1;
            bea_logf("G using StretchRect resolve path"
                     " (direct GetRenderTargetData hr=0x%08lX)\n",
                     (unsigned long)hr);
            if (shot_manifest)
                fprintf(shot_manifest,
                        "# resolve-path=stretchrect direct-hr=0x%08lX\n",
                        (unsigned long)hr);
        }
    }
    bb->lpVtbl->Release(bb);

    hr = shot_sys->lpVtbl->LockRect(shot_sys, &lr, NULL, D3DLOCK_READONLY);
    if (FAILED(hr)) {
        shot_fail("lockrect", hr);
        return;
    }

    rowlen = (size_t)desc.Width * 3 + 1;
    rawlen = rowlen * desc.Height;
    raw = (unsigned char *)malloc(rawlen);
    if (!raw) {
        shot_sys->lpVtbl->UnlockRect(shot_sys);
        shot_fail("malloc", 0);
        return;
    }

    for (y = 0; y < desc.Height; ++y) {
        raw[y * rowlen] = 0;          /* PNG filter type 0 */
        if (!shot_row_to_rgb(desc.Format,
                             (const unsigned char *)lr.pBits + (size_t)y * lr.Pitch,
                             desc.Width, raw + y * rowlen + 1)) {
            shot_sys->lpVtbl->UnlockRect(shot_sys);
            free(raw);
            shot_fail("unsupported-format", (HRESULT)desc.Format);
            shot_dead = 1;            /* the format will not change; stop. */
            return;
        }
    }
    shot_sys->lpVtbl->UnlockRect(shot_sys);
    shot_fail_streak = 0;

    /* Full-frame mean, and the 4x4 cell means used for change detection. This
     * is the number that is compared against the measured retail signatures --
     * the back buffer IS the client area, so a full-surface mean is the client
     * mean. */
    sum[0] = sum[1] = sum[2] = 0.0;
    memset(cellsum, 0, sizeof(cellsum));
    memset(cellcnt, 0, sizeof(cellcnt));
    for (y = 0; y < desc.Height; ++y) {
        const unsigned char *row = raw + y * rowlen + 1;
        cy = y * BEA_SHOT_CELLS / desc.Height;
        for (x = 0; x < desc.Width; ++x) {
            unsigned ci;
            cx = x * BEA_SHOT_CELLS / desc.Width;
            ci = cy * BEA_SHOT_CELLS + cx;
            sum[0] += row[x * 3 + 0];
            sum[1] += row[x * 3 + 1];
            sum[2] += row[x * 3 + 2];
            cellsum[ci][0] += row[x * 3 + 0];
            cellsum[ci][1] += row[x * 3 + 1];
            cellsum[ci][2] += row[x * 3 + 2];
            ++cellcnt[ci];
        }
    }
    for (i = 0; i < BEA_SHOT_CELLS * BEA_SHOT_CELLS; ++i) {
        unsigned n = cellcnt[i] ? cellcnt[i] : 1;
        cell[i * 3 + 0] = (unsigned char)(cellsum[i][0] / n + 0.5);
        cell[i * 3 + 1] = (unsigned char)(cellsum[i][1] / n + 0.5);
        cell[i * 3 + 2] = (unsigned char)(cellsum[i][2] / n + 0.5);
    }

    if (shot_mode_change) {
        if (!shot_prev_valid) {
            maxdelta = 255;
        } else {
            maxdelta = 0;
            for (i = 0; i < BEA_SHOT_CELLS * BEA_SHOT_CELLS * 3; ++i) {
                int d = (int)cell[i] - (int)shot_prev_cell[i];
                if (d < 0)
                    d = -d;
                if (d > maxdelta)
                    maxdelta = d;
            }
        }
        write = (maxdelta >= (int)shot_thresh) || shot_frame_selected(frame);
    } else {
        maxdelta = -1;
        write = 1;
    }

    nameA[0] = 0;
    if (write) {
        _snwprintf(path, MAX_PATH * 2 - 1, L"%s\\f%06u.png", shot_dir, frame);
        path[MAX_PATH * 2 - 1] = 0;
        if (shot_write_png(path, desc.Width, desc.Height, raw, rawlen)) {
            ++shot_written;
            memcpy(shot_prev_cell, cell, sizeof(shot_prev_cell));
            shot_prev_valid = 1;
            _snprintf(nameA, sizeof(nameA) - 1, "f%06u.png", frame);
            nameA[sizeof(nameA) - 1] = 0;
        } else {
            write = 0;
            shot_fail("png-write", 0);
        }
    }

    {
        double n = (double)desc.Width * (double)desc.Height;
        if (shot_manifest) {
            fprintf(shot_manifest, "%u,%d,%s,%u,%u,%u,%.3f,%.3f,%.3f,%d\n",
                    frame, write, nameA, (unsigned)desc.Width,
                    (unsigned)desc.Height, (unsigned)desc.Format,
                    sum[0] / n, sum[1] / n, sum[2] / n, maxdelta);
            fflush(shot_manifest);
        }
        bea_logf("G %u w=%d %ux%u fmt=%u mean=%.3f,%.3f,%.3f d=%d\n", frame,
                 write, (unsigned)desc.Width, (unsigned)desc.Height,
                 (unsigned)desc.Format, sum[0] / n, sum[1] / n, sum[2] / n,
                 maxdelta);
    }

    free(raw);
}

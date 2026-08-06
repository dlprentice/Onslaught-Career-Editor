/* bea-d3d9-proxy -- IDirect3D9 / IDirect3DDevice9 / IDirect3DStateBlock9 wrappers.
 *
 * Every method not listed below forwards straight through; those bodies and the
 * vtable initializers are generated from d3d9.h by gen_wrappers.py, so no slot
 * is ever counted by hand.
 *
 * Render-state, texture-stage-state, FVF, stream and viewport values are
 * SHADOWED from the game's Set* calls rather than read back with Get*, because
 * a device created with D3DCREATE_PUREDEVICE refuses every Get* query. Values
 * the game never set are reported as the Direct3D default with a '~' suffix;
 * values invalidated by a state block Apply are reported as '?'. Nothing in the
 * log is a guess presented as a measurement.
 */

#include "proxy.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------ line building */

typedef struct {
    char b[8192];
    int n;
} LineBuf;

static void lb_init(LineBuf *l)
{
    l->n = 0;
    l->b[0] = 0;
}

static void lb_addf(LineBuf *l, const char *fmt, ...)
{
    va_list ap;
    int room, k;
    room = (int)sizeof(l->b) - l->n - 1;
    if (room <= 0)
        return;
    va_start(ap, fmt);
    k = vsnprintf(l->b + l->n, (size_t)room + 1, fmt, ap);
    va_end(ap);
    if (k < 0)
        return;
    l->n += (k > room) ? room : k;
    l->b[l->n] = 0;
}

/* ------------------------------------------------------------------ objects */

#define BEA_RS_MAX 256
#define BEA_TSS_MAX 34
#define BEA_SAMP_MAX 14
#define BEA_STAGES 8
#define BEA_STREAMS 4

/* Transform slots that are shadowed, in log order.
 *
 * D3DTRANSFORMSTATETYPE is sparse (VIEW=2, PROJECTION=3, TEXTURE0..7=16..23,
 * WORLDMATRIX(i)=256+i), so it is folded into a dense table. Only WORLD0..3 are
 * kept: fixed-function vertex blending cannot address more than four without a
 * vertex shader, and this title issues no XYZBn FVF at all. A SetTransform to
 * anything outside the table is counted and named rather than dropped. */
#define BEA_MTX_VIEW    0
#define BEA_MTX_PROJ    1
#define BEA_MTX_TEX0    2      /* .. TEX0+7 */
#define BEA_MTX_WORLD0  10     /* .. WORLD0+3 */
#define BEA_MTX_SLOTS   14

#define BEA_ST_UNKNOWN 0
#define BEA_ST_DEFAULT 1
#define BEA_ST_SET 2

typedef struct BeaDev BeaDev;

typedef struct BeaD3D9 {
    IDirect3D9 base;
    IDirect3D9 *real;
    LONG ref;
} BeaD3D9;

typedef struct BeaSB {
    IDirect3DStateBlock9 base;
    IDirect3DStateBlock9 *real;
    LONG ref;
    BeaDev *dev;          /* WEAK: nulled by WD_Release, see the registry below */
    struct BeaSB *next;   /* live-wrapper registry */
} BeaSB;

/* Coverage: which bytes of a buffer are known to hold the game's data.
 *
 * D3D9 tells us what the game MAPPED for writing. It never tells us what the
 * game actually WROTE, and there is no legal way to find out -- the buffers are
 * D3DUSAGE_WRITEONLY and poisoning the mapping to detect writes would alter what
 * the game renders. So a mapped range is recorded with its provenance:
 *
 *   prov = 0  a sized Lock(off, size, ...): an exact mapped extent.
 *   prov = 1  a Lock(off, 0, ...), which means "to the end of the buffer". The
 *             game almost certainly wrote less than that, and after a
 *             D3DLOCK_DISCARD the untouched tail is fresh uninitialised memory.
 *             The extent is INFERRED, so any draw that depends on it is
 *             qualified in the log (or refused outright under STRICTCOV).
 *
 * Ranges are kept as a list, not as a hull, because a hull claims the gaps
 * between two disjoint locks and a draw reading such a gap would be decoded out
 * of calloc'd zeros and printed as measured coordinates. */
#define BEA_COV_MAX 16

typedef struct {
    UINT lo, hi;
    int prov;
} BeaCovRange;

typedef struct BeaBuf BeaBuf;

/* The exact bytes one draw reads, resolved ONCE per draw and then used by both
 * the digest and the full dump. Resolving twice would double-count every
 * refusal, which would make the tally at the end of the log a lie. */
typedef struct {
    BeaBuf *b;
    UINT off;      /* byte offset into the buffer's shadow */
    UINT size;     /* bytes */
    UINT stride;   /* vertex ranges only */
    UINT esz;      /* index ranges only: 2 or 4 */
    UINT count;    /* elements */
    int prov;      /* 1 => covered only by an inferred (size-0 lock) extent */
} BeaRange;

/* Vertex and index buffers.
 *
 * The game's buffers are created D3DUSAGE_WRITEONLY, which may not legally be
 * read back -- so the contents are captured on the way IN instead: whatever the
 * game writes between Lock and Unlock is copied into a private shadow, and
 * draws are decoded from the shadow. Nothing is ever read out of a Direct3D
 * resource, and the game's own bytes are never altered.
 *
 * `gen` is a process-unique serial that is never reused. A device stores it
 * alongside a bound wrapper pointer, so an address the allocator has recycled
 * into a DIFFERENT wrapper cannot masquerade as the original binding. */
struct BeaBuf {
    const void *lpVtbl;   /* must be first: this is the COM object */
    void *real;
    LONG ref;
    struct BeaBuf *next;  /* live-wrapper registry */
    unsigned gen;
    int isIndex;
    UINT size;
    DWORD usage;
    D3DFORMAT ifmt;       /* index buffers only */
    unsigned char *shadow;
    void *lockPtr;
    UINT lockOff, lockSize;
    int lockDiscard;
    int lockProv;
    BeaCovRange cov[BEA_COV_MAX];
    int covN;
    int covValid;
    /* Rewrite history. `unlocks` counts completed Unlocks that actually captured
     * bytes; `lastUnlockFrame` is the frame the most recent one landed in. A
     * mesh whose vertices are re-written by the CPU every frame shows exactly
     * one Unlock per frame here, and that is the whole CPU-skinning test. */
    unsigned unlocks;
    unsigned lastUnlockFrame;
};

/* A texture, recorded at creation so a bound pointer has a stable identity.
 *
 * Textures are NOT wrapped: the game hands the real pointer back at SetTexture,
 * so a creation-order registry is enough to name one, and not wrapping keeps
 * the proxy out of the texture's lifetime entirely. The cost is that a
 * destroyed texture leaves its entry behind -- so a pointer that comes back
 * from CreateTexture is re-registered in place, with a new serial and a log
 * line saying so, rather than silently inheriting the dead texture's name. */
typedef struct BeaTex {
    struct BeaTex *next;
    void *ptr;
    unsigned serial;
    UINT w, h, lv;
    DWORD usage;
    unsigned fmt, pool;
    unsigned long long hash0;
    int hashState;    /* 0 = not attempted, 1 = hashed, 2 = attempted and refused */
} BeaTex;

struct BeaDev {
    IDirect3DDevice9 base;
    IDirect3DDevice9 *real;
    LONG ref;

    DWORD rs[BEA_RS_MAX];
    unsigned char rsSt[BEA_RS_MAX];
    DWORD tss[BEA_STAGES][BEA_TSS_MAX];
    unsigned char tssSt[BEA_STAGES][BEA_TSS_MAX];
    DWORD samp[BEA_STAGES][BEA_SAMP_MAX];
    unsigned char sampSt[BEA_STAGES][BEA_SAMP_MAX];

    IDirect3DBaseTexture9 *tex[BEA_STAGES];
    unsigned char texSt[BEA_STAGES];

    /* Transform shadow. `id` is a process-unique serial minted only when the
     * VALUE changes, so a matrix re-set to what it already held does not
     * produce a new id and does not produce a second `M` row; a draw naming the
     * same id as an earlier draw is therefore genuinely the same matrix.
     * `emitted` is the emit-on-first-use flag: a matrix set before the capture
     * window opened is still written out the first time a logged draw needs it,
     * so a narrow window never yields draws whose transforms are missing. */
    struct {
        float m[16];
        unsigned id;
        unsigned char st;
        unsigned char emitted;
        unsigned char viaMul;   /* value derived from MultiplyTransform */
    } mtx[BEA_MTX_SLOTS];
    unsigned mtxUntracked;      /* SetTransform to a state outside the table */

    DWORD fvf;
    unsigned char fvfSt;
    IDirect3DVertexDeclaration9 *decl;
    IDirect3DVertexShader9 *vs;
    IDirect3DPixelShader9 *ps;

    /* Bound buffers are held WEAKLY. The device holds a reference to the REAL
     * buffer, not to our wrapper, so the wrapper dies the moment the game drops
     * its own reference -- which a D3DPOOL_DEFAULT buffer MUST do before every
     * Reset. AddRef-ing the wrapper here would fix the dangle by keeping the
     * real D3DPOOL_DEFAULT resource alive across Reset, which makes Reset fail
     * with D3DERR_INVALIDCALL: a logging defect turned into a game-breaking one.
     * So: the wrapper's own destructor clears these fields (`vbReleased`), and
     * `vbGen` makes a recycled heap block fail to impersonate the original. */
    struct {
        IDirect3DVertexBuffer9 *vb;
        unsigned vbGen;
        int vbReleased;
        UINT off;
        UINT stride;
        unsigned char st;
    } stream[BEA_STREAMS];
    IDirect3DIndexBuffer9 *ib;
    unsigned ibGen;
    int ibReleased;

    D3DVIEWPORT9 vp;
    unsigned char vpSt;

    UINT bbw, bbh;
    DWORD behavior;

    unsigned frame;
    unsigned draws;
    unsigned vlines;   /* V lines emitted this frame, against bea_cfg_vbudget */
    int recording;   /* between BeginStateBlock and EndStateBlock */
    int logging;     /* frame is inside the configured capture window */

    struct BeaDev *next;   /* live-wrapper registry */
};

/* ------------------------------------------------- live-wrapper registries */

/* Weak references, in one place. A wrapper is in exactly one of these lists
 * between its construction and the `free` in its own Release, and every stored
 * cross-reference is validated against the list before it is dereferenced. The
 * lists are therefore the only thing that ever proves a stored pointer is still
 * a live object; nothing else in this file reads through one. */
static BeaBuf *bea_live_bufs;
static BeaDev *bea_live_devs;
static BeaSB *bea_live_sbs;
static BeaTex *bea_texs;
static unsigned bea_gen_next = 1;
static unsigned bea_tex_next = 1;
static unsigned bea_mtx_id_next = 1;

/* The frame a buffer rewrite is attributed to. A buffer has no device, so the
 * frame counter it stamps must come from somewhere; this is the last frame any
 * wrapped device presented. Single-device title, and it is used only to
 * describe when a rewrite happened, never to decide what is recorded. */
static unsigned bea_cur_frame;

/* Non-zero while some device is inside its configured capture window. Used only
 * to gate the volume of Lock/Unlock records; correctness never depends on it. */
static int bea_window_open;

/* ------------------------------------------------------- refusal accounting */

#define BEA_REASON_MAX 32

static struct {
    const char *name;
    unsigned n;
} bea_reasons[BEA_REASON_MAX];
static int bea_reason_n;
static unsigned bea_refusals_total;
static unsigned bea_warnings_total;

static void bea_count(const char *reason, int isRefusal)
{
    int i;
    bea_lock();
    for (i = 0; i < bea_reason_n; ++i)
        if (strcmp(bea_reasons[i].name, reason) == 0)
            break;
    if (i == bea_reason_n && bea_reason_n < BEA_REASON_MAX) {
        bea_reasons[bea_reason_n].name = reason;
        bea_reasons[bea_reason_n].n = 0;
        bea_reason_n++;
    }
    if (i < BEA_REASON_MAX && i < bea_reason_n)
        bea_reasons[i].n++;
    if (isRefusal)
        bea_refusals_total++;
    else
        bea_warnings_total++;
    bea_unlock();
}

/* Every path that declines to record data goes through here. `rec` is the record
 * letter the data WOULD have carried ('V' or 'I'), so a reader greps the same
 * prefix for the data and for its absence. */
static void bea_refuse(BeaDev *d, char rec, const char *reason, const char *detail)
{
    bea_count(reason, 1);
    bea_logf("%c %u %u - none %s%s%s\n", rec, d->frame, d->draws, reason,
             detail ? " " : "", detail ? detail : "");
}

/* Data WAS recorded, but something about it is qualified. */
static void bea_warn(BeaDev *d, char rec, const char *reason, const char *detail)
{
    bea_count(reason, 0);
    bea_logf("%c %u %u - warn %s%s%s\n", rec, d->frame, d->draws, reason,
             detail ? " " : "", detail ? detail : "");
}

void bea_log_summary(void)
{
    int i;
    if (!bea_log_open())
        return;
    bea_logf("# refusals total=%u warnings=%u\n", bea_refusals_total,
             bea_warnings_total);
    for (i = 0; i < bea_reason_n; ++i)
        bea_logf("#   %s = %u\n", bea_reasons[i].name, bea_reasons[i].n);
    bea_log_flush();
}

/* -------------------------------------------------- weak-reference plumbing */

static void bea_buf_enrol(BeaBuf *b)
{
    bea_lock();
    b->gen = bea_gen_next++;
    b->next = bea_live_bufs;
    bea_live_bufs = b;
    bea_unlock();
}

/* Called from WVB_Release / WIB_Release immediately BEFORE the free, so no
 * device can still be pointing at the block when it goes back to the allocator.
 * This is the whole fix for the use-after-free: the wrapper retracts itself. */
static void bea_buf_retire(BeaBuf *b)
{
    BeaBuf **pp;
    BeaDev *d;
    int i, cleared = 0;

    bea_lock();
    for (pp = &bea_live_bufs; *pp; pp = &(*pp)->next)
        if (*pp == b) {
            *pp = b->next;
            break;
        }
    /* Fault injection leaves the bindings dangling on purpose, so the self-test
     * can show that the generation check alone still refuses. */
    for (d = bea_cfg_fault_noclearbind ? NULL : bea_live_devs; d; d = d->next) {
        for (i = 0; i < BEA_STREAMS; ++i)
            if ((const void *)d->stream[i].vb == (const void *)b) {
                d->stream[i].vb = NULL;
                d->stream[i].vbGen = 0;
                d->stream[i].vbReleased = 1;
                cleared++;
            }
        if ((const void *)d->ib == (const void *)b) {
            d->ib = NULL;
            d->ibGen = 0;
            d->ibReleased = 1;
            cleared++;
        }
    }
    bea_unlock();

    if (cleared)
        bea_logf("%s retire wrap=0x%p real=0x%p gen=%u STILL-BOUND slots=%d\n",
                 b->isIndex ? "IB" : "VB", (void *)b, b->real, b->gen, cleared);
    else if (bea_cfg_fault_noclearbind)
        bea_logf("%s retire wrap=0x%p real=0x%p gen=%u NOT-RETRACTED"
                 " (fault injection)\n",
                 b->isIndex ? "IB" : "VB", (void *)b, b->real, b->gen);
}

/* Is `p` still the live wrapper it was when `gen` was recorded?
 *   0 = never one of ours   1 = live and identical   2 = dead or recycled
 * `p` is NEVER dereferenced unless it is found in the registry, so a stale
 * binding cannot fault and cannot be mistaken for a live one either. */
static int bea_binding_state(const void *p, unsigned gen, const void *vtbl,
                             BeaBuf **out)
{
    BeaBuf *b, *found = NULL;
    int st;

    if (out)
        *out = NULL;
    if (!p)
        return 0;
    bea_lock();
    for (b = bea_live_bufs; b; b = b->next)
        if ((const void *)b == p) {
            found = b;
            break;
        }
    if (!found)
        st = gen ? 2 : 0;
    else if (found->gen != gen || found->lpVtbl != vtbl)
        st = 2;
    else
        st = 1;
    bea_unlock();
    if (st == 1 && out)
        *out = found;
    return st;
}

/* Registry lookup for a pointer the CALLER just handed us. Same no-dereference
 * property; a pointer that is not a live wrapper of ours is simply not found. */
static BeaBuf *bea_find_live(const void *p, const void *vtbl)
{
    BeaBuf *b, *found = NULL;
    if (!p)
        return NULL;
    bea_lock();
    for (b = bea_live_bufs; b; b = b->next)
        if ((const void *)b == p) {
            found = (b->lpVtbl == vtbl) ? b : NULL;
            break;
        }
    bea_unlock();
    return found;
}

static void bea_dev_enrol(BeaDev *d)
{
    bea_lock();
    d->next = bea_live_devs;
    bea_live_devs = d;
    bea_unlock();
}

/* A state block holds a raw BeaDev* so its Apply can invalidate the shadow. If
 * the game outlives the device wrapper with a state block still in hand -- legal,
 * because the real state block holds its own reference to the real device -- that
 * pointer would be a write into freed heap. Retract it here. */
static void bea_dev_retire(BeaDev *d)
{
    BeaDev **pp;
    BeaSB *sb;
    bea_lock();
    for (pp = &bea_live_devs; *pp; pp = &(*pp)->next)
        if (*pp == d) {
            *pp = d->next;
            break;
        }
    for (sb = bea_live_sbs; sb; sb = sb->next)
        if (sb->dev == d)
            sb->dev = NULL;
    bea_unlock();
}

static void bea_sb_enrol(BeaSB *w)
{
    bea_lock();
    w->next = bea_live_sbs;
    bea_live_sbs = w;
    bea_unlock();
}

static void bea_sb_retire(BeaSB *w)
{
    BeaSB **pp;
    bea_lock();
    for (pp = &bea_live_sbs; *pp; pp = &(*pp)->next)
        if (*pp == w) {
            *pp = w->next;
            break;
        }
    bea_unlock();
}

/* ------------------------------------------------------- coverage tracking */

static void bea_cov_reset(BeaBuf *b)
{
    b->covN = 0;
    b->covValid = 0;
}

static void bea_cov_add(BeaBuf *b, UINT lo, UINT hi, int prov)
{
    int i, ja = -1, jb = -1;
    UINT bestGap = 0;

    if (hi <= lo)
        return;
    for (i = 0; i < b->covN; ++i)
        if (b->cov[i].prov == prov && lo <= b->cov[i].hi && hi >= b->cov[i].lo) {
            if (lo < b->cov[i].lo) b->cov[i].lo = lo;
            if (hi > b->cov[i].hi) b->cov[i].hi = hi;
            b->covValid = 1;
            return;
        }
    if (b->covN < BEA_COV_MAX) {
        b->cov[b->covN].lo = lo;
        b->cov[b->covN].hi = hi;
        b->cov[b->covN].prov = prov;
        b->covN++;
        b->covValid = 1;
        return;
    }
    /* Out of slots. Join the two closest ranges. The join CLAIMS the gap between
     * them, so the survivor is demoted to provisional: this instrument may widen
     * a range only by admitting that it guessed. */
    for (i = 0; i + 1 < b->covN; ++i) {
        int j;
        for (j = i + 1; j < b->covN; ++j) {
            UINT a = b->cov[i].hi > b->cov[j].lo ? 0 : b->cov[j].lo - b->cov[i].hi;
            UINT c = b->cov[j].hi > b->cov[i].lo ? 0 : b->cov[i].lo - b->cov[j].hi;
            UINT gap = a < c ? a : c;
            if (ja < 0 || gap < bestGap) { ja = i; jb = j; bestGap = gap; }
        }
    }
    if (ja >= 0) {
        if (b->cov[jb].lo < b->cov[ja].lo) b->cov[ja].lo = b->cov[jb].lo;
        if (b->cov[jb].hi > b->cov[ja].hi) b->cov[ja].hi = b->cov[jb].hi;
        b->cov[ja].prov = 1;
        b->cov[jb] = b->cov[b->covN - 1];
        b->covN--;
        bea_cov_add(b, lo, hi, prov);
    }
}

/* Is [lo,hi) fully covered? `defOnly` restricts the answer to ranges whose
 * extent was measured rather than inferred. */
static int bea_cov_covers(BeaBuf *b, UINT lo, UINT hi, int defOnly)
{
    UINT cur = lo;
    int progress = 1;
    while (cur < hi && progress) {
        int i;
        progress = 0;
        for (i = 0; i < b->covN; ++i) {
            if (defOnly && b->cov[i].prov)
                continue;
            if (b->cov[i].lo <= cur && b->cov[i].hi > cur) {
                cur = b->cov[i].hi;
                progress = 1;
            }
        }
    }
    return cur >= hi;
}

static void bea_cov_describe(BeaBuf *b, char *out, size_t n)
{
    int i;
    size_t used = 0;
    if (!b->covN) {
        snprintf(out, n, "<none>");
        return;
    }
    out[0] = 0;
    for (i = 0; i < b->covN && used + 1 < n; ++i) {
        int k = snprintf(out + used, n - used, "%s[%u,%u)%s", i ? "," : "",
                         b->cov[i].lo, b->cov[i].hi, b->cov[i].prov ? "?" : "");
        if (k < 0)
            break;
        used += (size_t)k;
        if (used >= n)
            break;
    }
}

static IDirect3DDevice9 *bea_wrap_device(IDirect3DDevice9 *real,
                                         const D3DPRESENT_PARAMETERS *pp,
                                         DWORD behavior);
static IDirect3DStateBlock9 *bea_wrap_sb(IDirect3DStateBlock9 *real, BeaDev *dev);
static void bea_dev_invalidate_shadow(BeaDev *d, const char *why);

/* ----------------------------------------------------------------- hashing */

/* FNV-1a, 64-bit. Chosen for being three lines and dependency-free; it is an
 * identity check for byte ranges, never a security claim. */
#define BEA_FNV_OFFSET 1469598103934665603ULL
#define BEA_FNV_PRIME  1099511628211ULL

static unsigned long long bea_fnv(const unsigned char *p, size_t n)
{
    unsigned long long h = BEA_FNV_OFFSET;
    size_t i;
    for (i = 0; i < n; ++i) {
        h ^= (unsigned long long)p[i];
        h *= BEA_FNV_PRIME;
    }
    return h;
}

/* Byte ranges whose vertices have already been written out in full, so a static
 * mesh drawn 400 times is dumped once and referenced afterwards. Open-addressed,
 * fixed size, never grows: when it fills, dedup simply stops helping. It can
 * only ever SUPPRESS a duplicate of bytes already in this same log, so a `ref=`
 * line always has its full dump somewhere above it. */
#define BEA_DEDUP_SLOTS 4096

static unsigned long long bea_dedup[BEA_DEDUP_SLOTS];

/* 1 => this hash was already dumped (and the table is unchanged);
 * 0 => it is new (and has now been recorded). */
static int bea_dedup_seen(unsigned long long h)
{
    unsigned i, slot;
    if (!h)
        h = 1;
    slot = (unsigned)(h % BEA_DEDUP_SLOTS);
    for (i = 0; i < 64; ++i) {
        unsigned k = (slot + i) % BEA_DEDUP_SLOTS;
        if (bea_dedup[k] == h)
            return 1;
        if (!bea_dedup[k]) {
            bea_dedup[k] = h;
            return 0;
        }
    }
    return 0;   /* full cluster: dump it again rather than claim it was seen */
}

/* -------------------------------------------------------- transform shadow */

static const char *bea_mtx_name(int slot)
{
    static const char *const tex[8] = {
        "tex0", "tex1", "tex2", "tex3", "tex4", "tex5", "tex6", "tex7"
    };
    static const char *const wld[4] = { "world0", "world1", "world2", "world3" };
    if (slot == BEA_MTX_VIEW) return "view";
    if (slot == BEA_MTX_PROJ) return "proj";
    if (slot >= BEA_MTX_TEX0 && slot < BEA_MTX_TEX0 + 8)
        return tex[slot - BEA_MTX_TEX0];
    if (slot >= BEA_MTX_WORLD0 && slot < BEA_MTX_WORLD0 + 4)
        return wld[slot - BEA_MTX_WORLD0];
    return "?";
}

/* Dense slot for a D3DTRANSFORMSTATETYPE, or -1 if it is not tracked. */
static int bea_mtx_slot(D3DTRANSFORMSTATETYPE s)
{
    unsigned v = (unsigned)s;
    if (v == (unsigned)D3DTS_VIEW) return BEA_MTX_VIEW;
    if (v == (unsigned)D3DTS_PROJECTION) return BEA_MTX_PROJ;
    if (v >= 16 && v <= 23) return BEA_MTX_TEX0 + (int)(v - 16);
    if (v >= 256 && v <= 259) return BEA_MTX_WORLD0 + (int)(v - 256);
    return -1;
}

static void bea_mtx_store(BeaDev *d, int slot, const float *m, int viaMul)
{
    if (slot < 0 || slot >= BEA_MTX_SLOTS)
        return;
    /* An identical re-set keeps the existing id: ids identify VALUES, so two
     * draws naming the same id really did use the same matrix. */
    if (d->mtx[slot].st == BEA_ST_SET &&
        memcmp(d->mtx[slot].m, m, sizeof(float) * 16) == 0 &&
        d->mtx[slot].viaMul == (unsigned char)(viaMul != 0))
        return;
    memcpy(d->mtx[slot].m, m, sizeof(float) * 16);
    d->mtx[slot].id = bea_mtx_id_next++;
    d->mtx[slot].st = BEA_ST_SET;
    d->mtx[slot].emitted = 0;
    d->mtx[slot].viaMul = (unsigned char)(viaMul != 0);
}

/* Write the matrix out if this is the first logged draw that needs it, and
 * return the id to put on the draw row. 0 = the identity the device starts
 * with; ~0u = never observed (only reachable after a state-block Apply, which
 * invalidates the shadow because a block can restore transforms silently). */
static unsigned bea_mtx_use(BeaDev *d, int slot)
{
    LineBuf l;
    int k;
    if (slot < 0 || slot >= BEA_MTX_SLOTS)
        return 0xFFFFFFFFu;
    if (d->mtx[slot].st == BEA_ST_UNKNOWN)
        return 0xFFFFFFFFu;
    if (d->mtx[slot].emitted)
        return d->mtx[slot].id;
    lb_init(&l);
    lb_addf(&l, "M %u %s%s m=", d->mtx[slot].id, bea_mtx_name(slot),
            d->mtx[slot].viaMul ? " mul" : "");
    for (k = 0; k < 16; ++k)
        lb_addf(&l, "%s%.6f", k ? "," : "", d->mtx[slot].m[k]);
    lb_addf(&l, "\n");
    bea_logf("%s", l.b);
    d->mtx[slot].emitted = 1;
    return d->mtx[slot].id;
}

static void bea_fmt_mtx_id(unsigned id, char *out, size_t n)
{
    if (id == 0xFFFFFFFFu)
        snprintf(out, n, "?");
    else
        snprintf(out, n, "%u", id);
}

/* --------------------------------------------------------- texture registry */

static BeaTex *bea_tex_find(const void *p)
{
    BeaTex *t, *found = NULL;
    if (!p)
        return NULL;
    bea_lock();
    for (t = bea_texs; t; t = t->next)
        if (t->ptr == p) {
            found = t;
            break;
        }
    bea_unlock();
    return found;
}

static BeaTex *bea_tex_register(void *p, UINT w, UINT h, UINT lv, DWORD usage,
                                unsigned fmt, unsigned pool, unsigned *prevSerial)
{
    BeaTex *t = bea_tex_find(p);
    *prevSerial = 0;
    if (t) {
        /* The allocator handed back a destroyed texture's address. Re-name it:
         * inheriting the dead texture's serial would attribute a draw to the
         * wrong asset, which is the exact failure this registry exists to
         * prevent. */
        *prevSerial = t->serial;
        t->hash0 = 0;
        t->hashState = 0;
    } else {
        t = (BeaTex *)calloc(1, sizeof(BeaTex));
        if (!t)
            return NULL;
        t->ptr = p;
        bea_lock();
        t->next = bea_texs;
        bea_texs = t;
        bea_unlock();
    }
    t->serial = bea_tex_next++;
    t->w = w; t->h = h; t->lv = lv;
    t->usage = usage; t->fmt = fmt; t->pool = pool;
    return t;
}

/* Bytes of real content in one row (or one row of 4x4 blocks) of a surface, and
 * how many such rows there are. Returns 0 for a format this proxy does not know
 * the layout of -- in which case the texture is NOT hashed, because hashing a
 * guessed extent would fold the surface's padding into the identity and produce
 * a value that matches nothing in the asset mirror. */
static UINT bea_surface_rows(unsigned fmt, UINT w, UINT h, UINT *rowBytes)
{
    switch (fmt) {
    case D3DFMT_DXT1:
        *rowBytes = ((w + 3) / 4) * 8;  return (h + 3) / 4;
    case D3DFMT_DXT2: case D3DFMT_DXT3: case D3DFMT_DXT4: case D3DFMT_DXT5:
        *rowBytes = ((w + 3) / 4) * 16; return (h + 3) / 4;
    case D3DFMT_A8R8G8B8: case D3DFMT_X8R8G8B8:
    case D3DFMT_A8B8G8R8: case D3DFMT_X8B8G8R8:
    case D3DFMT_A2R10G10B10: case D3DFMT_A2B10G10R10:
    case D3DFMT_G16R16:
        *rowBytes = w * 4; return h;
    case D3DFMT_R8G8B8:
        *rowBytes = w * 3; return h;
    case D3DFMT_R5G6B5: case D3DFMT_X1R5G5B5: case D3DFMT_A1R5G5B5:
    case D3DFMT_A4R4G4B4: case D3DFMT_X4R4G4B4: case D3DFMT_A8L8:
    case D3DFMT_A8P8: case D3DFMT_V8U8: case D3DFMT_L16:
        *rowBytes = w * 2; return h;
    case D3DFMT_A8: case D3DFMT_L8: case D3DFMT_P8: case D3DFMT_A4L4:
        *rowBytes = w; return h;
    default:
        *rowBytes = 0; return 0;
    }
}

/* Hash level 0 of a bound texture, ONCE, so a draw can be attributed to a named
 * asset instead of to a pointer.
 *
 * This is the only place in the proxy that reads a Direct3D resource back, and
 * it is off unless BEA_D3D9_TEXHASH says otherwise. It refuses unless the
 * texture's OWN descriptor says the read is legal and free of side effects:
 * MANAGED or SYSTEMMEM pool (so there is a system-memory copy to read and no
 * video-memory stall), no RENDERTARGET/DEPTHSTENCIL/DYNAMIC usage, and a format
 * whose row extent is known. D3DLOCK_READONLY means the managed copy is not
 * marked dirty, so nothing is re-uploaded and the rendered frame is unchanged.
 * Every refusal is named in the tally. */
static void bea_tex_hash(BeaDev *d, IDirect3DBaseTexture9 *bt, BeaTex *t)
{
    IDirect3DTexture9 *tex = (IDirect3DTexture9 *)bt;
    D3DSURFACE_DESC sd;
    D3DLOCKED_RECT lr;
    UINT rows, rowBytes = 0, y;
    unsigned long long h = BEA_FNV_OFFSET;
    size_t total = 0;

    t->hashState = 2;   /* set first: every exit below is "attempted, no hash" */
    if (bt->lpVtbl->GetType(bt) != D3DRTYPE_TEXTURE) {
        bea_refuse(d, 'T', "texhash-not-2d", NULL);
        return;
    }
    if (FAILED(tex->lpVtbl->GetLevelDesc(tex, 0, &sd))) {
        bea_refuse(d, 'T', "texhash-no-desc", NULL);
        return;
    }
    if (sd.Pool != D3DPOOL_MANAGED && sd.Pool != D3DPOOL_SYSTEMMEM) {
        bea_refuse(d, 'T', "texhash-pool-not-readable", NULL);
        return;
    }
    if (sd.Usage & (D3DUSAGE_RENDERTARGET | D3DUSAGE_DEPTHSTENCIL |
                    D3DUSAGE_DYNAMIC)) {
        bea_refuse(d, 'T', "texhash-usage-not-static", NULL);
        return;
    }
    rows = bea_surface_rows((unsigned)sd.Format, sd.Width, sd.Height, &rowBytes);
    if (!rows || !rowBytes) {
        char det[48];
        snprintf(det, sizeof(det), "fmt=%u", (unsigned)sd.Format);
        bea_refuse(d, 'T', "texhash-format-unknown", det);
        return;
    }
    if (FAILED(tex->lpVtbl->LockRect(tex, 0, &lr, NULL,
                                     D3DLOCK_READONLY | D3DLOCK_NOSYSLOCK))) {
        bea_refuse(d, 'T', "texhash-lock-failed", NULL);
        return;
    }
    if (lr.pBits && lr.Pitch > 0 && (UINT)lr.Pitch >= rowBytes) {
        const unsigned char *p = (const unsigned char *)lr.pBits;
        for (y = 0; y < rows; ++y) {
            UINT i;
            /* Row by row, content bytes only: the pitch padding between rows is
             * driver-chosen and is not part of the asset. */
            for (i = 0; i < rowBytes; ++i) {
                h ^= (unsigned long long)p[i];
                h *= BEA_FNV_PRIME;
            }
            p += lr.Pitch;
        }
        total = (size_t)rows * rowBytes;
    }
    tex->lpVtbl->UnlockRect(tex, 0);
    if (!total) {
        bea_refuse(d, 'T', "texhash-empty-lock", NULL);
        return;
    }
    t->hash0 = h;
    t->hashState = 1;
    bea_logf("T hash serial=%u h=%016llX bytes=%u %ux%u fmt=%u\n",
             t->serial, h, (unsigned)total, (unsigned)sd.Width,
             (unsigned)sd.Height, (unsigned)sd.Format);
}

/* ------------------------------------------------------------- state naming */

static void fmt_state(unsigned char st, DWORD v, char *out, size_t n)
{
    if (st == BEA_ST_UNKNOWN)
        snprintf(out, n, "?");
    else
        snprintf(out, n, "%lu%s", (unsigned long)v, st == BEA_ST_DEFAULT ? "~" : "");
}

static void fmt_rs(BeaDev *d, D3DRENDERSTATETYPE s, char *out, size_t n)
{
    if ((unsigned)s >= BEA_RS_MAX) {
        snprintf(out, n, "?");
        return;
    }
    fmt_state(d->rsSt[s], d->rs[s], out, n);
}

static void fmt_tss(BeaDev *d, DWORD stage, D3DTEXTURESTAGESTATETYPE t,
                    char *out, size_t n)
{
    if (stage >= BEA_STAGES || (unsigned)t >= BEA_TSS_MAX) {
        snprintf(out, n, "?");
        return;
    }
    fmt_state(d->tssSt[stage][t], d->tss[stage][t], out, n);
}

/* Identity of a bound texture, for a draw row.
 *
 * `#serial` is the creation-order name from the registry; a texture that was
 * never seen at CreateTexture (there are none in this title, but say so rather
 * than assume) prints `#?`. `h=` appears only when content hashing is armed and
 * the hash succeeded, so the absence of an h= is never evidence that the
 * texture has no content -- the tally says which refusal it was. */
static void fmt_tex(BeaDev *d, IDirect3DBaseTexture9 *t, char *out, size_t n)
{
    D3DRESOURCETYPE rt;
    BeaTex *reg;
    char id[48], hash[24];

    if (!t) {
        snprintf(out, n, "none");
        return;
    }
    reg = bea_tex_find(t);
    if (reg && bea_cfg_texhash && reg->hashState == 0)
        bea_tex_hash(d, t, reg);
    if (reg)
        snprintf(id, sizeof(id), "#%u", reg->serial);
    else
        snprintf(id, sizeof(id), "#?");
    if (reg && reg->hashState == 1)
        snprintf(hash, sizeof(hash), ":h=%016llX", reg->hash0);
    else
        hash[0] = 0;

    rt = t->lpVtbl->GetType(t);
    if (rt == D3DRTYPE_TEXTURE) {
        D3DSURFACE_DESC sd;
        IDirect3DTexture9 *tex = (IDirect3DTexture9 *)t;
        if (SUCCEEDED(tex->lpVtbl->GetLevelDesc(tex, 0, &sd))) {
            snprintf(out, n, "0x%p:%ux%u:fmt%u:lv%u:%s%s",
                     (void *)t, (unsigned)sd.Width, (unsigned)sd.Height,
                     (unsigned)sd.Format,
                     (unsigned)tex->lpVtbl->GetLevelCount(tex), id, hash);
            return;
        }
    }
    snprintf(out, n, "0x%p:type%u:%s%s", (void *)t, (unsigned)rt, id, hash);
}

/* --------------------------------------------------------- vertex decoding */

static UINT bea_vertex_count(D3DPRIMITIVETYPE pt, UINT primCount)
{
    switch (pt) {
    case D3DPT_POINTLIST:     return primCount;
    case D3DPT_LINELIST:      return primCount * 2;
    case D3DPT_LINESTRIP:     return primCount + 1;
    case D3DPT_TRIANGLELIST:  return primCount * 3;
    case D3DPT_TRIANGLESTRIP: return primCount + 2;
    case D3DPT_TRIANGLEFAN:   return primCount + 2;
    default:                  return 0;
    }
}

static const char *bea_prim_name(D3DPRIMITIVETYPE pt)
{
    switch (pt) {
    case D3DPT_POINTLIST:     return "POINTLIST";
    case D3DPT_LINELIST:      return "LINELIST";
    case D3DPT_LINESTRIP:     return "LINESTRIP";
    case D3DPT_TRIANGLELIST:  return "TRILIST";
    case D3DPT_TRIANGLESTRIP: return "TRISTRIP";
    case D3DPT_TRIANGLEFAN:   return "TRIFAN";
    default:                  return "PRIM?";
    }
}

/* Size in bytes of the position block of an FVF, or -1 if unrecognised. */
static int fvf_pos_size(DWORD fvf, const char **name)
{
    switch (fvf & D3DFVF_POSITION_MASK) {
    case D3DFVF_XYZ:    *name = "xyz";    return 12;
    case D3DFVF_XYZRHW: *name = "xyzrhw"; return 16;
    case D3DFVF_XYZW:   *name = "xyzw";   return 16;
    case D3DFVF_XYZB1:  *name = "xyzb1";  return 16;
    case D3DFVF_XYZB2:  *name = "xyzb2";  return 20;
    case D3DFVF_XYZB3:  *name = "xyzb3";  return 24;
    case D3DFVF_XYZB4:  *name = "xyzb4";  return 28;
    case D3DFVF_XYZB5:  *name = "xyzb5";  return 32;
    default:            *name = "nopos";  return -1;
    }
}

static void bea_hexdump_vertex(unsigned frame, unsigned draw, unsigned i,
                               const unsigned char *v, UINT stride,
                               const char *why)
{
    LineBuf l;
    UINT k, cap = stride > 64 ? 64 : stride;
    lb_init(&l);
    lb_addf(&l, "V %u %u %u raw(%s)=", frame, draw, i, why);
    for (k = 0; k < cap; ++k)
        lb_addf(&l, "%02x", v[k]);
    lb_addf(&l, "\n");
    bea_logf("%s", l.b);
}

/* Decode one vertex against an FVF. Screen-space HUD quads are D3DFVF_XYZRHW,
 * in which case x and y as printed here ARE pixel coordinates in the back
 * buffer -- that is the whole reason this instrument exists. */
static void bea_dump_vertex(unsigned frame, unsigned draw, unsigned i,
                            DWORD fvf, const unsigned char *v, UINT stride)
{
    LineBuf l;
    const char *posname;
    int off, pos, tc, t;

    if (fvf == 0) {
        bea_hexdump_vertex(frame, draw, i, v, stride, "decl");
        return;
    }
    pos = fvf_pos_size(fvf, &posname);
    if (pos < 0) {
        bea_hexdump_vertex(frame, draw, i, v, stride, "nopos");
        return;
    }

    /* Measure first: never read past the stride the game declared. */
    off = pos;
    if (fvf & D3DFVF_NORMAL)   off += 12;
    if (fvf & D3DFVF_PSIZE)    off += 4;
    if (fvf & D3DFVF_DIFFUSE)  off += 4;
    if (fvf & D3DFVF_SPECULAR) off += 4;
    tc = (int)((fvf & D3DFVF_TEXCOUNT_MASK) >> D3DFVF_TEXCOUNT_SHIFT);
    for (t = 0; t < tc; ++t) {
        switch ((fvf >> (16 + t * 2)) & 3) {
        case 0: off += 8; break;   /* float2 */
        case 1: off += 12; break;  /* float3 */
        case 2: off += 16; break;  /* float4 */
        default: off += 4; break;  /* float1 */
        }
    }
    if (stride && off > (int)stride) {
        bea_hexdump_vertex(frame, draw, i, v, stride, "fvf-stride-mismatch");
        return;
    }

    lb_init(&l);
    lb_addf(&l, "V %u %u %u %s=(", frame, draw, i, posname);
    {
        const float *f = (const float *)v;
        int nf = pos / 4, k;
        for (k = 0; k < nf; ++k)
            lb_addf(&l, "%s%.4f", k ? "," : "", f[k]);
    }
    lb_addf(&l, ")");
    off = pos;
    if (fvf & D3DFVF_NORMAL) {
        const float *f = (const float *)(v + off);
        lb_addf(&l, " n=(%.4f,%.4f,%.4f)", f[0], f[1], f[2]);
        off += 12;
    }
    if (fvf & D3DFVF_PSIZE) {
        lb_addf(&l, " psize=%.4f", *(const float *)(v + off));
        off += 4;
    }
    if (fvf & D3DFVF_DIFFUSE) {
        lb_addf(&l, " diff=0x%08lX", (unsigned long)*(const DWORD *)(v + off));
        off += 4;
    }
    if (fvf & D3DFVF_SPECULAR) {
        lb_addf(&l, " spec=0x%08lX", (unsigned long)*(const DWORD *)(v + off));
        off += 4;
    }
    for (t = 0; t < tc; ++t) {
        const float *f = (const float *)(v + off);
        int nc;
        switch ((fvf >> (16 + t * 2)) & 3) {
        case 0: nc = 2; break;
        case 1: nc = 3; break;
        case 2: nc = 4; break;
        default: nc = 1; break;
        }
        lb_addf(&l, " t%d=(", t);
        {
            int k;
            for (k = 0; k < nc; ++k)
                lb_addf(&l, "%s%.4f", k ? "," : "", f[k]);
        }
        lb_addf(&l, ")");
        off += nc * 4;
    }
    lb_addf(&l, "\n");
    bea_logf("%s", l.b);
}

static void bea_dump_run(BeaDev *d, DWORD fvf, const unsigned char *base,
                         UINT stride, UINT count)
{
    UINT i;
    char det[64];
    if (!base) {
        bea_refuse(d, 'V', "up-data-null", NULL);
        return;
    }
    if (!stride) {
        bea_refuse(d, 'V', "up-stride-zero", NULL);
        return;
    }
    /* Unreachable while the draw entry points guard the cap themselves; kept so
     * a future caller cannot reintroduce a silent truncation. */
    if (count > bea_cfg_maxverts) {
        snprintf(det, sizeof(det), "nv=%u cap=%u", count, bea_cfg_maxverts);
        bea_refuse(d, 'V', "too-many-verts", det);
        return;
    }
    for (i = 0; i < count; ++i)
        bea_dump_vertex(d->frame, d->draws, i, fvf, base + (size_t)i * stride,
                        stride);
    d->vlines += count;
}

/* ========================= IDirect3DVertexBuffer9 ========================= */

static ULONG STDMETHODCALLTYPE WVB_AddRef(IDirect3DVertexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DVertexBuffer9 *r = (IDirect3DVertexBuffer9 *)b->real;
    r->lpVtbl->AddRef(r);
    return (ULONG)InterlockedIncrement(&b->ref);
}

static ULONG STDMETHODCALLTYPE WVB_Release(IDirect3DVertexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DVertexBuffer9 *r = (IDirect3DVertexBuffer9 *)b->real;
    LONG n = InterlockedDecrement(&b->ref);
    r->lpVtbl->Release(r);
    if (n <= 0) {
        bea_buf_retire(b);   /* retract every weak reference BEFORE the free */
        free(b->shadow);
        free(b);
        return 0;
    }
    return (ULONG)n;
}

static HRESULT STDMETHODCALLTYPE WVB_QueryInterface(IDirect3DVertexBuffer9 *This,
                                                    REFIID riid, void **ppvObject)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DVertexBuffer9 *r = (IDirect3DVertexBuffer9 *)b->real;
    void *p = NULL;
    HRESULT hr = r->lpVtbl->QueryInterface(r, riid, &p);
    if (FAILED(hr) || !p) {
        if (ppvObject)
            *ppvObject = NULL;
        return hr;
    }
    if (p == (void *)r) {
        r->lpVtbl->Release(r);
        WVB_AddRef(This);
        *ppvObject = This;
    } else {
        *ppvObject = p;
    }
    return hr;
}

/* SizeToLock == 0 means "to the end of the buffer" -- the D3D9 meaning, and the
 * standard dynamic-buffer idiom Lock(0, 0, D3DLOCK_DISCARD). What is mapped is
 * knowable; what was written is not. Record which one this was. */
static void bea_buf_note_lock(BeaBuf *b, UINT off, UINT size, void *ptr, DWORD flags)
{
    b->lockPtr = ptr;
    b->lockOff = off;
    b->lockSize = size ? size : (b->size > off ? b->size - off : 0);
    b->lockDiscard = (flags & D3DLOCK_DISCARD) ? 1 : 0;
    b->lockProv = size ? 0 : 1;
    if (bea_window_open)
        bea_logf("L %s wrap=0x%p off=%u size=%u mapped=%u flags=0x%lX%s\n",
                 b->isIndex ? "IB" : "VB", (void *)b, off, size, b->lockSize,
                 (unsigned long)flags, b->lockProv ? " EXTENT-INFERRED" : "");
}

/* Copy what the game just wrote into the shadow. This reads only the mapped
 * pointer the game itself was handed, never the Direct3D resource. */
static void bea_buf_capture(BeaBuf *b)
{
    if (!b->lockPtr || !b->shadow || !b->lockSize ||
        b->lockOff + b->lockSize > b->size) {
        b->lockPtr = NULL;
        return;
    }
    memcpy(b->shadow + b->lockOff, b->lockPtr, b->lockSize);
    /* D3DLOCK_DISCARD discards the contents of the WHOLE buffer, not merely the
     * locked range, so every range recorded before it is void. */
    if (b->lockDiscard)
        bea_cov_reset(b);
    bea_cov_add(b, b->lockOff, b->lockOff + b->lockSize, b->lockProv);
    /* Rewrite history, kept ALWAYS -- not only inside the capture window. A
     * digest row that says "this buffer has been re-written 1,412 times, most
     * recently in this frame" is only meaningful if the count did not start at
     * the window boundary. */
    b->unlocks++;
    b->lastUnlockFrame = bea_cur_frame;
    if (bea_window_open) {
        char desc[256];
        bea_cov_describe(b, desc, sizeof(desc));
        bea_logf("U %s wrap=0x%p cov=%s\n", b->isIndex ? "IB" : "VB", (void *)b,
                 desc);
    }
    b->lockPtr = NULL;
}

static HRESULT STDMETHODCALLTYPE WVB_Lock(IDirect3DVertexBuffer9 *This,
                                          UINT OffsetToLock, UINT SizeToLock,
                                          void **ppbData, DWORD Flags)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DVertexBuffer9 *r = (IDirect3DVertexBuffer9 *)b->real;
    HRESULT hr = r->lpVtbl->Lock(r, OffsetToLock, SizeToLock, ppbData, Flags);
    if (SUCCEEDED(hr) && ppbData && *ppbData)
        bea_buf_note_lock(b, OffsetToLock, SizeToLock, *ppbData, Flags);
    else
        b->lockPtr = NULL;
    return hr;
}

static HRESULT STDMETHODCALLTYPE WVB_Unlock(IDirect3DVertexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DVertexBuffer9 *r = (IDirect3DVertexBuffer9 *)b->real;
    bea_buf_capture(b);
    return r->lpVtbl->Unlock(r);
}

#define BEA_REAL(p) ((IDirect3DVertexBuffer9 *)((BeaBuf *)(p))->real)
#include "idirect3dvertexbuffer9.inc"
#undef BEA_REAL

/* ========================== IDirect3DIndexBuffer9 ========================= */

static ULONG STDMETHODCALLTYPE WIB_AddRef(IDirect3DIndexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DIndexBuffer9 *r = (IDirect3DIndexBuffer9 *)b->real;
    r->lpVtbl->AddRef(r);
    return (ULONG)InterlockedIncrement(&b->ref);
}

static ULONG STDMETHODCALLTYPE WIB_Release(IDirect3DIndexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DIndexBuffer9 *r = (IDirect3DIndexBuffer9 *)b->real;
    LONG n = InterlockedDecrement(&b->ref);
    r->lpVtbl->Release(r);
    if (n <= 0) {
        bea_buf_retire(b);   /* retract every weak reference BEFORE the free */
        free(b->shadow);
        free(b);
        return 0;
    }
    return (ULONG)n;
}

static HRESULT STDMETHODCALLTYPE WIB_QueryInterface(IDirect3DIndexBuffer9 *This,
                                                    REFIID riid, void **ppvObject)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DIndexBuffer9 *r = (IDirect3DIndexBuffer9 *)b->real;
    void *p = NULL;
    HRESULT hr = r->lpVtbl->QueryInterface(r, riid, &p);
    if (FAILED(hr) || !p) {
        if (ppvObject)
            *ppvObject = NULL;
        return hr;
    }
    if (p == (void *)r) {
        r->lpVtbl->Release(r);
        WIB_AddRef(This);
        *ppvObject = This;
    } else {
        *ppvObject = p;
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WIB_Lock(IDirect3DIndexBuffer9 *This,
                                          UINT OffsetToLock, UINT SizeToLock,
                                          void **ppbData, DWORD Flags)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DIndexBuffer9 *r = (IDirect3DIndexBuffer9 *)b->real;
    HRESULT hr = r->lpVtbl->Lock(r, OffsetToLock, SizeToLock, ppbData, Flags);
    if (SUCCEEDED(hr) && ppbData && *ppbData)
        bea_buf_note_lock(b, OffsetToLock, SizeToLock, *ppbData, Flags);
    else
        b->lockPtr = NULL;
    return hr;
}

static HRESULT STDMETHODCALLTYPE WIB_Unlock(IDirect3DIndexBuffer9 *This)
{
    BeaBuf *b = (BeaBuf *)This;
    IDirect3DIndexBuffer9 *r = (IDirect3DIndexBuffer9 *)b->real;
    bea_buf_capture(b);
    return r->lpVtbl->Unlock(r);
}

#define BEA_REAL(p) ((IDirect3DIndexBuffer9 *)((BeaBuf *)(p))->real)
#include "idirect3dindexbuffer9.inc"
#undef BEA_REAL

static BeaBuf *bea_new_buf(void *real, const void *vtbl, int isIndex, UINT size,
                           DWORD usage, D3DFORMAT ifmt)
{
    BeaBuf *b = (BeaBuf *)calloc(1, sizeof(BeaBuf));
    if (!b)
        return NULL;
    b->lpVtbl = vtbl;
    b->real = real;
    b->ref = 1;
    b->isIndex = isIndex;
    b->size = size;
    b->usage = usage;
    b->ifmt = ifmt;
    b->shadow = (unsigned char *)calloc(1, size ? size : 1);
    if (!b->shadow) {
        free(b);
        return NULL;
    }
    bea_buf_enrol(b);
    return b;
}

/* Unwrapping a pointer the CALLER just supplied.
 *
 * This used to test the first word of `p` against our vtable. That reads through
 * a pointer that may already have been freed -- and worse, a heap block recycled
 * into a new wrapper passes the test and resolves to the WRONG buffer. Both
 * unwrap paths now go through the live registry, which compares addresses and
 * never dereferences a pointer it did not find there. */
static IDirect3DVertexBuffer9 *bea_unwrap_vb(IDirect3DVertexBuffer9 *p)
{
    BeaBuf *b = bea_find_live(p, &bea_wvb_vtbl);
    return b ? (IDirect3DVertexBuffer9 *)b->real : p;
}

/* Vertices for a non-UP draw come out of stream 0, decoded from the shadow
 * captured at Unlock. Every refusal below is logged with its reason so an empty
 * result can never be mistaken for "the game drew nothing there".
 *
 * Check order matters: every guard below runs BEFORE anything reads through the
 * stored wrapper pointer. The previous version resolved the wrapper first, so
 * the "stream unset" and "shadow invalidated" guards protected nothing. */
static int bea_stream0_range(BeaDev *d, UINT firstVertex, UINT count,
                             BeaRange *r)
{
    BeaBuf *b = NULL;
    UINT stride, off, size;
    char det[160];
    int st;

    memset(r, 0, sizeof(*r));
    if (d->stream[0].vbReleased) {
        bea_refuse(d, 'V', "stream0-released-while-bound", NULL);
        return 0;
    }
    if (!d->stream[0].vb) {
        bea_refuse(d, 'V', "stream0-unset", NULL);
        return 0;
    }
    if (d->stream[0].st != BEA_ST_SET) {
        bea_refuse(d, 'V', "stream0-stride-unknown", NULL);
        return 0;
    }
    st = bea_binding_state(d->stream[0].vb, d->stream[0].vbGen, &bea_wvb_vtbl, &b);
    if (st == 2) {
        snprintf(det, sizeof(det), "wrap=0x%p gen=%u", (void *)d->stream[0].vb,
                 d->stream[0].vbGen);
        bea_refuse(d, 'V', "vb-wrapper-stale", det);
        return 0;
    }
    if (st == 0 || !b) {
        bea_refuse(d, 'V', "vb-not-created-through-proxy", NULL);
        return 0;
    }
    if (!b->covValid) {
        bea_refuse(d, 'V', "vb-never-written", NULL);
        return 0;
    }
    stride = d->stream[0].stride;
    if (!stride) {
        bea_refuse(d, 'V', "stream0-stride-zero", NULL);
        return 0;
    }
    off = d->stream[0].off + firstVertex * stride;
    size = count * stride;
    if (!size || off + size > b->size) {
        snprintf(det, sizeof(det), "off=%u size=%u vbsize=%u", off, size, b->size);
        bea_refuse(d, 'V', "vb-range", det);
        return 0;
    }
    if (!bea_cov_covers(b, off, off + size, 0)) {
        char have[128];
        bea_cov_describe(b, have, sizeof(have));
        snprintf(det, sizeof(det), "want=[%u,%u) have=%s", off, off + size, have);
        bea_refuse(d, 'V', "vb-outside-written-range", det);
        return 0;
    }
    if (!bea_cov_covers(b, off, off + size, 1)) {
        /* Covered only by a range whose extent was inferred from a size-0 lock.
         * The bytes may be what the game wrote, or may be the uninitialised tail
         * of a DISCARD mapping. Say so; never let it pass as a measurement. */
        char have[128];
        bea_cov_describe(b, have, sizeof(have));
        snprintf(det, sizeof(det), "want=[%u,%u) have=%s", off, off + size, have);
        if (bea_cfg_strictcov) {
            bea_refuse(d, 'V', "vb-provisional-coverage", det);
            return 0;
        }
        bea_warn(d, 'V', "vb-provisional-coverage", det);
        r->prov = 1;
    }
    r->b = b;
    r->off = off;
    r->size = size;
    r->stride = stride;
    r->count = count;
    return 1;
}

/* Same, for the index run of an indexed draw. Every early return here used to be
 * silent, which made a DIP with vertices and no index line indistinguishable
 * from one where the dump was never attempted. */
static int bea_index_range(BeaDev *d, UINT startIndex, UINT indexCount,
                           BeaRange *r)
{
    BeaBuf *b = NULL;
    UINT esz, off, size;
    char det[160];
    int st;

    memset(r, 0, sizeof(*r));
    if (d->ibReleased) {
        bea_refuse(d, 'I', "ib-released-while-bound", NULL);
        return 0;
    }
    if (!d->ib) {
        bea_refuse(d, 'I', "ib-unset", NULL);
        return 0;
    }
    st = bea_binding_state(d->ib, d->ibGen, &bea_wib_vtbl, &b);
    if (st == 2) {
        snprintf(det, sizeof(det), "wrap=0x%p gen=%u", (void *)d->ib, d->ibGen);
        bea_refuse(d, 'I', "ib-wrapper-stale", det);
        return 0;
    }
    if (st == 0 || !b) {
        bea_refuse(d, 'I', "ib-not-created-through-proxy", NULL);
        return 0;
    }
    if (!b->covValid) {
        bea_refuse(d, 'I', "ib-never-written", NULL);
        return 0;
    }
    esz = (b->ifmt == D3DFMT_INDEX32) ? 4 : 2;
    off = startIndex * esz;
    size = indexCount * esz;
    if (!size || off + size > b->size) {
        snprintf(det, sizeof(det), "off=%u size=%u ibsize=%u", off, size, b->size);
        bea_refuse(d, 'I', "ib-range", det);
        return 0;
    }
    if (!bea_cov_covers(b, off, off + size, 0)) {
        char have[128];
        bea_cov_describe(b, have, sizeof(have));
        snprintf(det, sizeof(det), "want=[%u,%u) have=%s", off, off + size, have);
        bea_refuse(d, 'I', "ib-outside-written-range", det);
        return 0;
    }
    if (!bea_cov_covers(b, off, off + size, 1)) {
        char have[128];
        bea_cov_describe(b, have, sizeof(have));
        snprintf(det, sizeof(det), "want=[%u,%u) have=%s", off, off + size, have);
        if (bea_cfg_strictcov) {
            bea_refuse(d, 'I', "ib-provisional-coverage", det);
            return 0;
        }
        bea_warn(d, 'I', "ib-provisional-coverage", det);
        r->prov = 1;
    }
    r->b = b;
    r->off = off;
    r->size = size;
    r->esz = esz;
    r->count = indexCount;
    return 1;
}

/* ------------------------------------------------------- geometry digest */

/* One line per draw: what buffer, which bytes, their hash, how many times that
 * buffer has been re-written, and -- for a recognised position layout -- the
 * bounding box of the positions the draw actually reads.
 *
 * This is the record that answers the CPU-skinning question without dumping a
 * single vertex. If a mesh's `h=` is identical frame after frame while the
 * object moves on screen, the movement is in the transforms (`M` rows). If `h=`
 * changes every frame and `unlocks=` advances with it, the vertices themselves
 * are being re-written on the CPU -- and only then is a full `V` dump worth its
 * volume, at which point `pos=` says where to point the gate. */
static void bea_geom_digest(BeaDev *d, const BeaRange *r, const char *kind,
                            DWORD fvf)
{
    LineBuf l;
    unsigned long long h;
    const unsigned char *base;

    if (!r->b || !r->size)
        return;
    base = r->b->shadow + r->off;
    h = bea_fnv(base, r->size);

    lb_init(&l);
    lb_addf(&l, "G %u %u %s real=0x%p gen=%u off=%u n=%u bytes=%u h=%016llX"
                " unlocks=%u lastunlock=%u",
            d->frame, d->draws, kind, r->b->real, r->b->gen, r->off, r->count,
            r->size, h, r->b->unlocks, r->b->lastUnlockFrame);
    if (r->stride)
        lb_addf(&l, " stride=%u", r->stride);
    if (r->esz)
        lb_addf(&l, " esz=%u", r->esz);
    if (r->prov)
        lb_addf(&l, " PROVISIONAL");

    /* Position bounds, in whatever space the vertices are in -- object space for
     * this title's world draws, screen pixels for its XYZRHW quads. Printed only
     * when the FVF names a float position at offset 0; never guessed. */
    if (r->stride && !r->esz) {
        const char *posname;
        int pos = fvf_pos_size(fvf, &posname);
        if (fvf && pos >= 12 && (UINT)pos <= r->stride) {
            float mn[3], mx[3];
            UINT i;
            int k;
            for (k = 0; k < 3; ++k) { mn[k] = 0.0f; mx[k] = 0.0f; }
            for (i = 0; i < r->count; ++i) {
                const float *f = (const float *)(base + (size_t)i * r->stride);
                for (k = 0; k < 3; ++k) {
                    if (!i || f[k] < mn[k]) mn[k] = f[k];
                    if (!i || f[k] > mx[k]) mx[k] = f[k];
                }
            }
            lb_addf(&l, " %s min=(%.4f,%.4f,%.4f) max=(%.4f,%.4f,%.4f)",
                    posname, mn[0], mn[1], mn[2], mx[0], mx[1], mx[2]);
        }
    }
    lb_addf(&l, "\n");
    bea_logf("%s", l.b);
}

/* ------------------------------------------------------- the full dumps */

/* Which draws get a full per-vertex dump. Everything the gate excludes is
 * refused BY THE NAME OF THE PREDICATE that excluded it, so a reader can tell a
 * gated capture from a sparse frame without knowing the command line -- and the
 * settings themselves are restated in the log header. */
static int bea_vgate(BeaDev *d, UINT nv, DWORD fvf)
{
    char det[96];
    if (d->draws < bea_cfg_vdraw_first || d->draws > bea_cfg_vdraw_last) {
        snprintf(det, sizeof(det), "draw=%u window=[%u,%u]", d->draws,
                 bea_cfg_vdraw_first, bea_cfg_vdraw_last);
        bea_refuse(d, 'V', "gated-draw-window", det);
        return 0;
    }
    if (nv < bea_cfg_vminverts) {
        snprintf(det, sizeof(det), "nv=%u min=%u", nv, bea_cfg_vminverts);
        bea_refuse(d, 'V', "gated-min-verts", det);
        return 0;
    }
    if (bea_cfg_vfvf && fvf != (DWORD)bea_cfg_vfvf) {
        snprintf(det, sizeof(det), "fvf=0x%lX want=0x%X", (unsigned long)fvf,
                 bea_cfg_vfvf);
        bea_refuse(d, 'V', "gated-fvf", det);
        return 0;
    }
    if (bea_cfg_vbudget && d->vlines >= bea_cfg_vbudget) {
        snprintf(det, sizeof(det), "used=%u budget=%u", d->vlines,
                 bea_cfg_vbudget);
        bea_refuse(d, 'V', "gated-frame-budget", det);
        return 0;
    }
    return 1;
}

static void bea_dump_range(BeaDev *d, const BeaRange *r, DWORD fvf)
{
    const unsigned char *base = r->b->shadow + r->off;
    UINT i;

    /* Identical bytes already written out in full earlier in this same log get a
     * back-reference instead of a second copy. A static mesh drawn hundreds of
     * times therefore costs one dump and hundreds of one-line references. */
    if (bea_cfg_vdedup) {
        unsigned long long h = bea_fnv(base, r->size);
        if (bea_dedup_seen(h)) {
            bea_logf("V %u %u ref=%016llX n=%u\n", d->frame, d->draws, h,
                     r->count);
            d->vlines++;
            return;
        }
    }
    for (i = 0; i < r->count; ++i)
        bea_dump_vertex(d->frame, d->draws, i, fvf,
                        base + (size_t)i * r->stride, r->stride);
    d->vlines += r->count;
}

/* Indices, in chunks. A LineBuf truncates silently at 8 KiB, which for a big
 * index run would drop values with no trace at all -- so a long run is split
 * across lines that each name the element they start at, and nothing is lost. */
#define BEA_IDX_PER_LINE 512

static void bea_dump_index_range(BeaDev *d, const BeaRange *r)
{
    UINT done = 0;
    while (done < r->count) {
        UINT n = r->count - done;
        LineBuf l;
        UINT i;
        if (n > BEA_IDX_PER_LINE)
            n = BEA_IDX_PER_LINE;
        lb_init(&l);
        lb_addf(&l, "I %u %u from=%u idx=", d->frame, d->draws, done);
        for (i = 0; i < n; ++i) {
            UINT e = done + i;
            UINT v = (r->esz == 4)
                ? *(const UINT *)(r->b->shadow + r->off + e * 4)
                : (UINT)*(const unsigned short *)(r->b->shadow + r->off + e * 2);
            lb_addf(&l, "%s%u", i ? "," : "", v);
        }
        lb_addf(&l, "\n");
        bea_logf("%s", l.b);
        done += n;
    }
}

/* --------------------------------------------------------- the draw record */

static void bea_log_draw(BeaDev *d, const char *kind, D3DPRIMITIVETYPE pt,
                         UINT primCount, UINT numVerts, UINT extra1, UINT extra2,
                         UINT extra3, const char *extraName1,
                         const char *extraName2, const char *extraName3)
{
    LineBuf l;
    char b[8][32];
    char tex0[192], tex1[192];
    char mw[16], mv[16], mp[16];
    unsigned idW, idV, idP;

    /* Transforms FIRST: bea_mtx_use writes the `M` row for any matrix whose
     * value has not been written out yet, and those rows must appear above the
     * `D` row that names them or the log does not read in order. */
    idW = bea_mtx_use(d, BEA_MTX_WORLD0);
    idV = bea_mtx_use(d, BEA_MTX_VIEW);
    idP = bea_mtx_use(d, BEA_MTX_PROJ);

    lb_init(&l);
    lb_addf(&l, "D %u %u %s prim=%s primc=%u verts=%u",
            d->frame, d->draws, kind, bea_prim_name(pt), primCount, numVerts);
    if (extraName1)
        lb_addf(&l, " %s=%u", extraName1, extra1);
    if (extraName2)
        lb_addf(&l, " %s=%u", extraName2, extra2);
    if (extraName3)
        lb_addf(&l, " %s=%u", extraName3, extra3);

    if (d->fvfSt == BEA_ST_SET)
        lb_addf(&l, " fvf=0x%lX", (unsigned long)d->fvf);
    else
        lb_addf(&l, " fvf=?");
    lb_addf(&l, " decl=0x%p vs=0x%p ps=0x%p",
            (void *)d->decl, (void *)d->vs, (void *)d->ps);
    /* Never dereference a stored wrapper to print it: resolve through the live
     * registry, and name the two failure states rather than printing a pointer
     * that no longer means anything. */
    {
        int s;
        for (s = 0; s < 2; ++s) {
            BeaBuf *sb = NULL;
            int st;
            if (s == 1 && !d->stream[1].vb && !d->stream[1].vbReleased)
                continue;
            st = bea_binding_state(d->stream[s].vb, d->stream[s].vbGen,
                                   &bea_wvb_vtbl, &sb);
            if (d->stream[s].vbReleased)
                lb_addf(&l, " s%d=(vb=released,off=%u,stride=%u)", s,
                        d->stream[s].off, d->stream[s].stride);
            else if (st == 2)
                lb_addf(&l, " s%d=(vb=stale,off=%u,stride=%u)", s,
                        d->stream[s].off, d->stream[s].stride);
            else
                lb_addf(&l, " s%d=(vb=0x%p,off=%u,stride=%u%s)", s,
                        sb ? sb->real : (void *)d->stream[s].vb,
                        d->stream[s].off, d->stream[s].stride,
                        d->stream[s].st == BEA_ST_SET ? "" : ",unset");
        }
    }

    fmt_tex(d, d->tex[0], tex0, sizeof(tex0));
    fmt_tex(d, d->tex[1], tex1, sizeof(tex1));
    lb_addf(&l, " tex0=%s tex1=%s", tex0, tex1);
    /* Stages 2..7 are shadowed too, and were simply never printed. They are
     * emitted only when something is bound, so the common two-stage draw row is
     * the same length it always was. */
    {
        int s;
        for (s = 2; s < BEA_STAGES; ++s)
            if (d->tex[s]) {
                char t[192];
                fmt_tex(d, d->tex[s], t, sizeof(t));
                lb_addf(&l, " tex%d=%s", s, t);
            }
    }

    fmt_rs(d, D3DRS_ALPHABLENDENABLE, b[0], 32);
    fmt_rs(d, D3DRS_SRCBLEND,         b[1], 32);
    fmt_rs(d, D3DRS_DESTBLEND,        b[2], 32);
    fmt_rs(d, D3DRS_BLENDOP,          b[3], 32);
    fmt_rs(d, D3DRS_ALPHATESTENABLE,  b[4], 32);
    fmt_rs(d, D3DRS_ALPHAREF,         b[5], 32);
    fmt_rs(d, D3DRS_ALPHAFUNC,        b[6], 32);
    lb_addf(&l, " ab=%s sb=%s db=%s bop=%s at=%s aref=%s afunc=%s",
            b[0], b[1], b[2], b[3], b[4], b[5], b[6]);

    fmt_rs(d, D3DRS_ZENABLE,      b[0], 32);
    fmt_rs(d, D3DRS_ZWRITEENABLE, b[1], 32);
    fmt_rs(d, D3DRS_ZFUNC,        b[2], 32);
    fmt_rs(d, D3DRS_CULLMODE,     b[3], 32);
    fmt_rs(d, D3DRS_LIGHTING,     b[4], 32);
    fmt_rs(d, D3DRS_FOGENABLE,    b[5], 32);
    lb_addf(&l, " z=%s zw=%s zf=%s cull=%s lit=%s fog=%s",
            b[0], b[1], b[2], b[3], b[4], b[5]);

    if (d->rsSt[D3DRS_TEXTUREFACTOR] != BEA_ST_UNKNOWN)
        lb_addf(&l, " tfactor=0x%08lX%s",
                (unsigned long)d->rs[D3DRS_TEXTUREFACTOR],
                d->rsSt[D3DRS_TEXTUREFACTOR] == BEA_ST_DEFAULT ? "~" : "");
    else
        lb_addf(&l, " tfactor=?");

    fmt_tss(d, 0, D3DTSS_COLOROP,   b[0], 32);
    fmt_tss(d, 0, D3DTSS_COLORARG1, b[1], 32);
    fmt_tss(d, 0, D3DTSS_COLORARG2, b[2], 32);
    fmt_tss(d, 0, D3DTSS_ALPHAOP,   b[3], 32);
    fmt_tss(d, 0, D3DTSS_ALPHAARG1, b[4], 32);
    fmt_tss(d, 0, D3DTSS_ALPHAARG2, b[5], 32);
    lb_addf(&l, " s0.cop=%s/%s,%s s0.aop=%s/%s,%s",
            b[0], b[1], b[2], b[3], b[4], b[5]);

    fmt_tss(d, 1, D3DTSS_COLOROP, b[0], 32);
    fmt_tss(d, 1, D3DTSS_ALPHAOP, b[1], 32);
    lb_addf(&l, " s1.cop=%s s1.aop=%s", b[0], b[1]);

    if (d->vpSt != BEA_ST_UNKNOWN)
        lb_addf(&l, " vp=(%u,%u,%ux%u)%s",
                (unsigned)d->vp.X, (unsigned)d->vp.Y,
                (unsigned)d->vp.Width, (unsigned)d->vp.Height,
                d->vpSt == BEA_ST_DEFAULT ? "~" : "");

    /* Sampler state for the two stages that carry this title's material, so a
     * quad's addressing and filtering are on the same row as its texture. */
    fmt_state(d->sampSt[0][D3DSAMP_ADDRESSU], d->samp[0][D3DSAMP_ADDRESSU], b[0], 32);
    fmt_state(d->sampSt[0][D3DSAMP_ADDRESSV], d->samp[0][D3DSAMP_ADDRESSV], b[1], 32);
    fmt_state(d->sampSt[0][D3DSAMP_MAGFILTER], d->samp[0][D3DSAMP_MAGFILTER], b[2], 32);
    fmt_state(d->sampSt[0][D3DSAMP_MINFILTER], d->samp[0][D3DSAMP_MINFILTER], b[3], 32);
    fmt_state(d->sampSt[0][D3DSAMP_MIPFILTER], d->samp[0][D3DSAMP_MIPFILTER], b[4], 32);
    lb_addf(&l, " s0.addr=%s/%s s0.filt=%s/%s/%s", b[0], b[1], b[2], b[3], b[4]);

    /* The transforms in force. These are the whole point of the extension: for
     * a world draw the vertices are object-space, so without w=/v=/p= the row
     * says what was drawn but nothing about where or facing which way. */
    bea_fmt_mtx_id(idW, mw, sizeof(mw));
    bea_fmt_mtx_id(idV, mv, sizeof(mv));
    bea_fmt_mtx_id(idP, mp, sizeof(mp));
    lb_addf(&l, " w=%s v=%s p=%s", mw, mv, mp);
    /* A texture matrix only participates when the stage says so, so it is named
     * only then -- an absent tm0= means the stage disabled it, not that it was
     * not observed. */
    if (d->tssSt[0][D3DTSS_TEXTURETRANSFORMFLAGS] == BEA_ST_SET &&
        d->tss[0][D3DTSS_TEXTURETRANSFORMFLAGS] != D3DTTFF_DISABLE) {
        char tm[16];
        bea_fmt_mtx_id(bea_mtx_use(d, BEA_MTX_TEX0), tm, sizeof(tm));
        lb_addf(&l, " tm0=%s tmflags=%lu", tm,
                (unsigned long)d->tss[0][D3DTSS_TEXTURETRANSFORMFLAGS]);
    }
    if (d->mtxUntracked)
        lb_addf(&l, " mtxuntracked=%u", d->mtxUntracked);
    lb_addf(&l, "\n");
    bea_logf("%s", l.b);
}

/* ============================ IDirect3DStateBlock9 ======================== */

static ULONG STDMETHODCALLTYPE WSB_AddRef(IDirect3DStateBlock9 *This)
{
    BeaSB *w = (BeaSB *)This;
    w->real->lpVtbl->AddRef(w->real);
    return (ULONG)InterlockedIncrement(&w->ref);
}

static ULONG STDMETHODCALLTYPE WSB_Release(IDirect3DStateBlock9 *This)
{
    BeaSB *w = (BeaSB *)This;
    LONG r = InterlockedDecrement(&w->ref);
    w->real->lpVtbl->Release(w->real);
    if (r <= 0) {
        bea_sb_retire(w);
        free(w);
        return 0;
    }
    return (ULONG)r;
}

static HRESULT STDMETHODCALLTYPE WSB_QueryInterface(IDirect3DStateBlock9 *This,
                                                    REFIID riid, void **ppvObject)
{
    BeaSB *w = (BeaSB *)This;
    void *p = NULL;
    HRESULT hr = w->real->lpVtbl->QueryInterface(w->real, riid, &p);
    if (FAILED(hr) || !p) {
        if (ppvObject)
            *ppvObject = NULL;
        return hr;
    }
    if (p == (void *)w->real) {
        w->real->lpVtbl->Release(w->real);
        WSB_AddRef(This);
        *ppvObject = This;
    } else {
        *ppvObject = p;
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WSB_Apply(IDirect3DStateBlock9 *This)
{
    BeaSB *w = (BeaSB *)This;
    if (w->dev)
        bea_dev_invalidate_shadow(w->dev, "stateblock-apply");
    return w->real->lpVtbl->Apply(w->real);
}

#define BEA_REAL(p) (((BeaSB *)(p))->real)
#include "idirect3dstateblock9.inc"
#undef BEA_REAL

static IDirect3DStateBlock9 *bea_wrap_sb(IDirect3DStateBlock9 *real, BeaDev *dev)
{
    BeaSB *w;
    if (!real)
        return NULL;
    w = (BeaSB *)calloc(1, sizeof(BeaSB));
    if (!w)
        return real; /* degrade to pass-through rather than fail the game */
    w->base.lpVtbl = &bea_wsb_vtbl;
    w->real = real;
    w->ref = 1;
    w->dev = dev;   /* weak; bea_dev_retire nulls it if the device dies first */
    bea_sb_enrol(w);
    return (IDirect3DStateBlock9 *)w;
}

/* ============================== IDirect3DDevice9 ========================== */

static void bea_dev_invalidate_shadow(BeaDev *d, const char *why)
{
    memset(d->rsSt, BEA_ST_UNKNOWN, sizeof(d->rsSt));
    memset(d->tssSt, BEA_ST_UNKNOWN, sizeof(d->tssSt));
    memset(d->sampSt, BEA_ST_UNKNOWN, sizeof(d->sampSt));
    memset(d->texSt, BEA_ST_UNKNOWN, sizeof(d->texSt));
    d->fvfSt = BEA_ST_UNKNOWN;
    d->vpSt = BEA_ST_UNKNOWN;
    {
        int i;
        for (i = 0; i < BEA_STREAMS; ++i)
            d->stream[i].st = BEA_ST_UNKNOWN;
        /* A state block can restore transforms as silently as it restores
         * render state, so the matrix shadow is invalidated with everything
         * else: a draw after an Apply prints w=? rather than a stale id. */
        for (i = 0; i < BEA_MTX_SLOTS; ++i) {
            d->mtx[i].st = BEA_ST_UNKNOWN;
            d->mtx[i].emitted = 0;
        }
    }
    bea_logf("! %u shadow-invalidated %s\n", d->frame, why);
}

static void bea_dev_seed_defaults(BeaDev *d, const D3DPRESENT_PARAMETERS *pp)
{
    int s;
#define SEED_RS(st, val) do { d->rs[st] = (DWORD)(val); d->rsSt[st] = BEA_ST_DEFAULT; } while (0)
    SEED_RS(D3DRS_ZENABLE, (pp && pp->EnableAutoDepthStencil) ? D3DZB_TRUE : D3DZB_FALSE);
    SEED_RS(D3DRS_ZWRITEENABLE, TRUE);
    SEED_RS(D3DRS_ZFUNC, D3DCMP_LESSEQUAL);
    SEED_RS(D3DRS_ALPHATESTENABLE, FALSE);
    SEED_RS(D3DRS_ALPHAREF, 0);
    SEED_RS(D3DRS_ALPHAFUNC, D3DCMP_ALWAYS);
    SEED_RS(D3DRS_SRCBLEND, D3DBLEND_ONE);
    SEED_RS(D3DRS_DESTBLEND, D3DBLEND_ZERO);
    SEED_RS(D3DRS_ALPHABLENDENABLE, FALSE);
    SEED_RS(D3DRS_BLENDOP, D3DBLENDOP_ADD);
    SEED_RS(D3DRS_CULLMODE, D3DCULL_CCW);
    SEED_RS(D3DRS_LIGHTING, TRUE);
    SEED_RS(D3DRS_FOGENABLE, FALSE);
    SEED_RS(D3DRS_TEXTUREFACTOR, 0xFFFFFFFF);
#undef SEED_RS
    for (s = 0; s < BEA_STAGES; ++s) {
#define SEED_TSS(t, val) do { d->tss[s][t] = (DWORD)(val); d->tssSt[s][t] = BEA_ST_DEFAULT; } while (0)
        SEED_TSS(D3DTSS_COLOROP, s == 0 ? D3DTOP_MODULATE : D3DTOP_DISABLE);
        SEED_TSS(D3DTSS_COLORARG1, D3DTA_TEXTURE);
        SEED_TSS(D3DTSS_COLORARG2, D3DTA_CURRENT);
        SEED_TSS(D3DTSS_ALPHAOP, s == 0 ? D3DTOP_SELECTARG1 : D3DTOP_DISABLE);
        SEED_TSS(D3DTSS_ALPHAARG1, D3DTA_TEXTURE);
        SEED_TSS(D3DTSS_ALPHAARG2, D3DTA_CURRENT);
        SEED_TSS(D3DTSS_TEXTURETRANSFORMFLAGS, D3DTTFF_DISABLE);
#undef SEED_TSS
#define SEED_SAMP(t, val) do { d->samp[s][t] = (DWORD)(val); d->sampSt[s][t] = BEA_ST_DEFAULT; } while (0)
        SEED_SAMP(D3DSAMP_ADDRESSU, D3DTADDRESS_WRAP);
        SEED_SAMP(D3DSAMP_ADDRESSV, D3DTADDRESS_WRAP);
        SEED_SAMP(D3DSAMP_MAGFILTER, D3DTEXF_POINT);
        SEED_SAMP(D3DSAMP_MINFILTER, D3DTEXF_POINT);
        SEED_SAMP(D3DSAMP_MIPFILTER, D3DTEXF_NONE);
#undef SEED_SAMP
    }
    /* The device starts with every transform at identity. id 0 is reserved for
     * exactly that value, and is never emitted as an `M` row: a draw carrying
     * w=0 means "identity, never set", which is a different claim from w=? --
     * "set at some point, but a state block then made it unknowable". */
    {
        int i, k;
        for (i = 0; i < BEA_MTX_SLOTS; ++i) {
            for (k = 0; k < 16; ++k)
                d->mtx[i].m[k] = (k % 5 == 0) ? 1.0f : 0.0f;
            d->mtx[i].id = 0;
            d->mtx[i].st = BEA_ST_DEFAULT;
            d->mtx[i].emitted = 1;
            d->mtx[i].viaMul = 0;
        }
    }
    if (pp) {
        d->vp.X = 0;
        d->vp.Y = 0;
        d->vp.Width = pp->BackBufferWidth;
        d->vp.Height = pp->BackBufferHeight;
        d->vp.MinZ = 0.0f;
        d->vp.MaxZ = 1.0f;
        d->vpSt = BEA_ST_DEFAULT;
        d->bbw = pp->BackBufferWidth;
        d->bbh = pp->BackBufferHeight;
    }
}

static ULONG STDMETHODCALLTYPE WD_AddRef(IDirect3DDevice9 *This)
{
    BeaDev *w = (BeaDev *)This;
    w->real->lpVtbl->AddRef(w->real);
    return (ULONG)InterlockedIncrement(&w->ref);
}

static ULONG STDMETHODCALLTYPE WD_Release(IDirect3DDevice9 *This)
{
    BeaDev *w = (BeaDev *)This;
    LONG r = InterlockedDecrement(&w->ref);
    w->real->lpVtbl->Release(w->real);
    if (r <= 0) {
        bea_logf("DEV release frame=%u\n", w->frame);
        bea_log_summary();
        bea_log_flush();
        bea_dev_retire(w);   /* retract every weak reference BEFORE the free */
        free(w);
        return 0;
    }
    return (ULONG)r;
}

static HRESULT STDMETHODCALLTYPE WD_QueryInterface(IDirect3DDevice9 *This,
                                                   REFIID riid, void **ppvObject)
{
    BeaDev *w = (BeaDev *)This;
    void *p = NULL;
    HRESULT hr = w->real->lpVtbl->QueryInterface(w->real, riid, &p);
    if (FAILED(hr) || !p) {
        if (ppvObject)
            *ppvObject = NULL;
        return hr;
    }
    if (p == (void *)w->real) {
        w->real->lpVtbl->Release(w->real);
        WD_AddRef(This);
        *ppvObject = This;
    } else {
        bea_logf("DEV qi-unwrapped 0x%p\n", p);
        *ppvObject = p;
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_BeginScene(IDirect3DDevice9 *This)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging)
        bea_logf("S %u begin\n", d->frame);
    return d->real->lpVtbl->BeginScene(d->real);
}

static HRESULT STDMETHODCALLTYPE WD_EndScene(IDirect3DDevice9 *This)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging)
        bea_logf("S %u end draws=%u\n", d->frame, d->draws);
    return d->real->lpVtbl->EndScene(d->real);
}

static HRESULT STDMETHODCALLTYPE WD_Clear(IDirect3DDevice9 *This, DWORD rect_count,
                                          const D3DRECT *rects, DWORD flags,
                                          D3DCOLOR color, float z, DWORD stencil)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging)
        bea_logf("C %u rects=%lu flags=0x%lX color=0x%08lX z=%.4f stencil=%lu\n",
                 d->frame, (unsigned long)rect_count, (unsigned long)flags,
                 (unsigned long)color, z, (unsigned long)stencil);
    return d->real->lpVtbl->Clear(d->real, rect_count, rects, flags, color, z,
                                  stencil);
}

static HRESULT STDMETHODCALLTYPE WD_Present(IDirect3DDevice9 *This,
                                            const RECT *src_rect,
                                            const RECT *dst_rect,
                                            HWND dst_window_override,
                                            const RGNDATA *dirty_region)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr;
    if (d->logging) {
        bea_logf("P %u draws=%u\n", d->frame, d->draws);
        bea_log_flush();
    }
    /* Grab BEFORE the real Present. With D3DSWAPEFFECT_DISCARD -- which is what
     * this title creates its device with -- the back buffer's contents are
     * undefined the moment Present returns, so a grab taken afterwards would be
     * reading whatever the driver left behind rather than the frame the game
     * composed. */
    if (bea_shot_enabled)
        bea_shot_present(d->real, d->frame);
    hr = d->real->lpVtbl->Present(d->real, src_rect, dst_rect,
                                  dst_window_override, dirty_region);
    d->frame++;
    d->draws = 0;
    d->vlines = 0;
    bea_cur_frame = d->frame;
    d->logging = (d->frame >= bea_cfg_firstframe &&
                  d->frame < bea_cfg_firstframe + bea_cfg_maxframes);
    bea_window_open = d->logging;
    if (!d->logging && d->frame == bea_cfg_firstframe + bea_cfg_maxframes) {
        bea_logf("# capture window closed at frame %u\n", d->frame);
        bea_log_summary();
        bea_log_flush();
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_Reset(IDirect3DDevice9 *This,
                                          D3DPRESENT_PARAMETERS *pPresentationParameters)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr;
    /* Before, not after: the grab's resolve target is D3DPOOL_DEFAULT and the
     * application must have released every such resource by now, or Reset fails
     * with D3DERR_INVALIDCALL. An instrument must never be the reason a mode
     * change breaks. */
    if (bea_shot_enabled)
        bea_shot_pre_reset();
    hr = d->real->lpVtbl->Reset(d->real, pPresentationParameters);
    if (SUCCEEDED(hr)) {
        if (bea_shot_enabled)
            bea_shot_reset();
        bea_dev_invalidate_shadow(d, "device-reset");
        bea_dev_seed_defaults(d, pPresentationParameters);
        if (pPresentationParameters)
            bea_logf("DEV reset bb=%ux%u fmt=%u windowed=%d\n",
                     (unsigned)pPresentationParameters->BackBufferWidth,
                     (unsigned)pPresentationParameters->BackBufferHeight,
                     (unsigned)pPresentationParameters->BackBufferFormat,
                     (int)pPresentationParameters->Windowed);
    }
    return hr;
}

/* -- state shadowing ------------------------------------------------------- */

static HRESULT STDMETHODCALLTYPE WD_SetRenderState(IDirect3DDevice9 *This,
                                                   D3DRENDERSTATETYPE State,
                                                   DWORD Value)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && (unsigned)State < BEA_RS_MAX) {
        d->rs[State] = Value;
        d->rsSt[State] = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetRenderState(d->real, State, Value);
}

static HRESULT STDMETHODCALLTYPE WD_SetTextureStageState(IDirect3DDevice9 *This,
                                                         DWORD Stage,
                                                         D3DTEXTURESTAGESTATETYPE Type,
                                                         DWORD Value)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && Stage < BEA_STAGES && (unsigned)Type < BEA_TSS_MAX) {
        d->tss[Stage][Type] = Value;
        d->tssSt[Stage][Type] = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetTextureStageState(d->real, Stage, Type, Value);
}

static HRESULT STDMETHODCALLTYPE WD_SetTexture(IDirect3DDevice9 *This, DWORD Stage,
                                               IDirect3DBaseTexture9 *pTexture)
{
    BeaDev *d = (BeaDev *)This;
    /* No AddRef: SetTexture makes the device hold a reference of its own, so a
     * bound texture cannot be destroyed while we hold the pointer. */
    if (!d->recording && Stage < BEA_STAGES) {
        d->tex[Stage] = pTexture;
        d->texSt[Stage] = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetTexture(d->real, Stage, pTexture);
}

static HRESULT STDMETHODCALLTYPE WD_SetSamplerState(IDirect3DDevice9 *This,
                                                    DWORD Sampler,
                                                    D3DSAMPLERSTATETYPE Type,
                                                    DWORD Value)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && Sampler < BEA_STAGES && (unsigned)Type < BEA_SAMP_MAX) {
        d->samp[Sampler][Type] = Value;
        d->sampSt[Sampler][Type] = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetSamplerState(d->real, Sampler, Type, Value);
}

/* The transform shadow.
 *
 * A world draw's vertices are object-space, so the matrices in force at the
 * draw are the only thing that says where the object is and how it is facing.
 * Nothing is read back: D3DCREATE_PUREDEVICE refuses GetTransform, so the value
 * is whatever the game last passed in, tracked here. */
static HRESULT STDMETHODCALLTYPE WD_SetTransform(IDirect3DDevice9 *This,
                                                 D3DTRANSFORMSTATETYPE state,
                                                 const D3DMATRIX *matrix)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && matrix) {
        int slot = bea_mtx_slot(state);
        if (slot < 0) {
            /* Counted and surfaced on the draw row rather than dropped: a
             * WORLDMATRIX(4..255) would mean this title does indexed vertex
             * blending after all, which would change what the vertex data
             * means. Silence there would be the dangerous outcome. */
            d->mtxUntracked++;
            if (d->logging)
                bea_logf("! %u transform-untracked state=%u\n", d->frame,
                         (unsigned)state);
        } else {
            bea_mtx_store(d, slot, (const float *)matrix, 0);
        }
    }
    return d->real->lpVtbl->SetTransform(d->real, state, matrix);
}

/* MultiplyTransform composes with a value we already hold, so the result is
 * derived rather than observed -- and D3D9's documented multiplication ORDER is
 * the one thing here that cannot be measured from the call alone. The value is
 * computed as new = current * arg, and the resulting `M` row is stamped `mul`
 * so a consumer can see exactly which values rest on that assumption instead of
 * having it silently folded into the rest. */
static HRESULT STDMETHODCALLTYPE WD_MultiplyTransform(IDirect3DDevice9 *This,
                                                      D3DTRANSFORMSTATETYPE state,
                                                      const D3DMATRIX *matrix)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && matrix) {
        int slot = bea_mtx_slot(state);
        if (slot < 0) {
            d->mtxUntracked++;
        } else if (d->mtx[slot].st == BEA_ST_UNKNOWN) {
            /* Composing onto an unknown value yields an unknown value. */
            bea_count("transform-multiply-onto-unknown", 0);
        } else {
            const float *a = d->mtx[slot].m;
            const float *b = (const float *)matrix;
            float out[16];
            int i, j, k;
            for (i = 0; i < 4; ++i)
                for (j = 0; j < 4; ++j) {
                    float s = 0.0f;
                    for (k = 0; k < 4; ++k)
                        s += a[i * 4 + k] * b[k * 4 + j];
                    out[i * 4 + j] = s;
                }
            bea_mtx_store(d, slot, out, 1);
            bea_count("transform-multiply-order-assumed", 0);
        }
    }
    return d->real->lpVtbl->MultiplyTransform(d->real, state, matrix);
}

static HRESULT STDMETHODCALLTYPE WD_SetFVF(IDirect3DDevice9 *This, DWORD FVF)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording) {
        d->fvf = FVF;
        d->fvfSt = BEA_ST_SET;
        d->decl = NULL;
    }
    return d->real->lpVtbl->SetFVF(d->real, FVF);
}

static HRESULT STDMETHODCALLTYPE WD_SetVertexDeclaration(IDirect3DDevice9 *This,
                                                         IDirect3DVertexDeclaration9 *pDecl)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording) {
        d->decl = pDecl;
        if (pDecl) {
            d->fvf = 0;
            d->fvfSt = BEA_ST_SET;
        }
    }
    return d->real->lpVtbl->SetVertexDeclaration(d->real, pDecl);
}

static HRESULT STDMETHODCALLTYPE WD_SetStreamSource(IDirect3DDevice9 *This,
                                                    UINT StreamNumber,
                                                    IDirect3DVertexBuffer9 *pStreamData,
                                                    UINT OffsetInBytes, UINT Stride)
{
    BeaDev *d = (BeaDev *)This;
    /* The device takes a reference on the REAL buffer; the wrapper is held
     * WEAKLY (see BeaDev). No AddRef here on purpose: it would keep a
     * D3DPOOL_DEFAULT resource alive across Reset and make Reset fail. The
     * wrapper's own Release retracts this binding, and `vbGen` catches the case
     * where the heap block is recycled into a different wrapper. */
    BeaBuf *b = bea_find_live(pStreamData, &bea_wvb_vtbl);
    if (!d->recording && StreamNumber < BEA_STREAMS) {
        d->stream[StreamNumber].vb = pStreamData;
        d->stream[StreamNumber].vbGen = b ? b->gen : 0;
        d->stream[StreamNumber].vbReleased = 0;
        d->stream[StreamNumber].off = OffsetInBytes;
        d->stream[StreamNumber].stride = Stride;
        d->stream[StreamNumber].st = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetStreamSource(d->real, StreamNumber,
                                            b ? (IDirect3DVertexBuffer9 *)b->real
                                              : pStreamData,
                                            OffsetInBytes, Stride);
}

static HRESULT STDMETHODCALLTYPE WD_SetIndices(IDirect3DDevice9 *This,
                                               IDirect3DIndexBuffer9 *pIndexData)
{
    BeaDev *d = (BeaDev *)This;
    BeaBuf *b = bea_find_live(pIndexData, &bea_wib_vtbl);   /* weak, as above */
    if (!d->recording) {
        d->ib = pIndexData;
        d->ibGen = b ? b->gen : 0;
        d->ibReleased = 0;
    }
    return d->real->lpVtbl->SetIndices(d->real,
                                       b ? (IDirect3DIndexBuffer9 *)b->real
                                         : pIndexData);
}

static HRESULT STDMETHODCALLTYPE WD_SetViewport(IDirect3DDevice9 *This,
                                                const D3DVIEWPORT9 *viewport)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording && viewport) {
        d->vp = *viewport;
        d->vpSt = BEA_ST_SET;
    }
    return d->real->lpVtbl->SetViewport(d->real, viewport);
}

static HRESULT STDMETHODCALLTYPE WD_SetVertexShader(IDirect3DDevice9 *This,
                                                    IDirect3DVertexShader9 *pShader)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording)
        d->vs = pShader;
    return d->real->lpVtbl->SetVertexShader(d->real, pShader);
}

static HRESULT STDMETHODCALLTYPE WD_SetPixelShader(IDirect3DDevice9 *This,
                                                   IDirect3DPixelShader9 *pShader)
{
    BeaDev *d = (BeaDev *)This;
    if (!d->recording)
        d->ps = pShader;
    return d->real->lpVtbl->SetPixelShader(d->real, pShader);
}

static HRESULT STDMETHODCALLTYPE WD_BeginStateBlock(IDirect3DDevice9 *This)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr = d->real->lpVtbl->BeginStateBlock(d->real);
    if (SUCCEEDED(hr)) {
        d->recording = 1;
        bea_logf("! %u stateblock-record-begin\n", d->frame);
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_EndStateBlock(IDirect3DDevice9 *This,
                                                  IDirect3DStateBlock9 **ppSB)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr = d->real->lpVtbl->EndStateBlock(d->real, ppSB);
    d->recording = 0;
    bea_logf("! %u stateblock-record-end hr=0x%08lX\n", d->frame,
             (unsigned long)hr);
    if (SUCCEEDED(hr) && ppSB && *ppSB)
        *ppSB = bea_wrap_sb(*ppSB, d);
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_CreateStateBlock(IDirect3DDevice9 *This,
                                                     D3DSTATEBLOCKTYPE Type,
                                                     IDirect3DStateBlock9 **ppSB)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr = d->real->lpVtbl->CreateStateBlock(d->real, Type, ppSB);
    bea_logf("! %u stateblock-create type=%u hr=0x%08lX\n", d->frame,
             (unsigned)Type, (unsigned long)hr);
    if (SUCCEEDED(hr) && ppSB && *ppSB)
        *ppSB = bea_wrap_sb(*ppSB, d);
    return hr;
}

/* -- resource creation ----------------------------------------------------- */

/* Textures are registered, not wrapped.
 *
 * The game hands the real pointer straight back at SetTexture, so a
 * creation-order registry is enough to give a bound texture a stable name --
 * and staying out of the object's lifetime means the proxy cannot be the reason
 * a texture survives a Reset or a device teardown. The cost is that the registry
 * never shrinks; a recycled address is handled by re-registering it under a new
 * serial, which is logged. */
static HRESULT STDMETHODCALLTYPE WD_CreateTexture(IDirect3DDevice9 *This,
                                                  UINT Width, UINT Height,
                                                  UINT Levels, DWORD Usage,
                                                  D3DFORMAT Format, D3DPOOL Pool,
                                                  IDirect3DTexture9 **ppTexture,
                                                  HANDLE *pSharedHandle)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr;
    bea_fault_createtexture_count += 1;
    if (bea_cfg_fault_createtexture_after > 0) {
        int fire = bea_cfg_fault_createtexture_sticky
            ? (bea_fault_createtexture_count >= bea_cfg_fault_createtexture_after)
            : (bea_fault_createtexture_count == bea_cfg_fault_createtexture_after);
        if (fire) {
            if (ppTexture)
                *ppTexture = NULL;
            bea_logf("# FAULT-INJECTION CreateTexture n=%u -> hr=0x%08lX "
                     "(%ux%u lv=%u fmt=%u)%s\n",
                     bea_fault_createtexture_count,
                     (unsigned long)bea_cfg_fault_createtexture_hr,
                     (unsigned)Width, (unsigned)Height, (unsigned)Levels,
                     (unsigned)Format,
                     bea_cfg_fault_createtexture_sticky ? " sticky" : "");
            bea_log_flush();
            return (HRESULT)bea_cfg_fault_createtexture_hr;
        }
    }
    hr = d->real->lpVtbl->CreateTexture(d->real, Width, Height, Levels,
                                                Usage, Format, Pool, ppTexture,
                                                pSharedHandle);
    if (SUCCEEDED(hr) && ppTexture && *ppTexture) {
        unsigned prev = 0;
        UINT lv = Levels;
        BeaTex *t;
        if (!lv)
            lv = (*ppTexture)->lpVtbl->GetLevelCount(*ppTexture);
        t = bea_tex_register(*ppTexture, Width, Height, lv, Usage,
                             (unsigned)Format, (unsigned)Pool, &prev);
        if (t) {
            char note[48];
            note[0] = 0;
            if (prev)
                snprintf(note, sizeof(note), " RECYCLED-PTR prev=%u", prev);
            bea_logf("T create serial=%u ptr=0x%p %ux%u lv=%u fmt=%u usage=0x%lX"
                     " pool=%u%s\n",
                     t->serial, (void *)*ppTexture, (unsigned)Width,
                     (unsigned)Height, (unsigned)lv, (unsigned)Format,
                     (unsigned long)Usage, (unsigned)Pool, note);
        }
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_CreateVertexBuffer(IDirect3DDevice9 *This,
                                                       UINT Length, DWORD Usage,
                                                       DWORD FVF, D3DPOOL Pool,
                                                       IDirect3DVertexBuffer9 **ppVertexBuffer,
                                                       HANDLE *pSharedHandle)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr = d->real->lpVtbl->CreateVertexBuffer(d->real, Length, Usage, FVF,
                                                     Pool, ppVertexBuffer,
                                                     pSharedHandle);
    if (SUCCEEDED(hr) && ppVertexBuffer && *ppVertexBuffer) {
        BeaBuf *b = bea_new_buf(*ppVertexBuffer, &bea_wvb_vtbl, 0, Length, Usage,
                                D3DFMT_UNKNOWN);
        if (b) {
            /* wrap= and gen= are what make a recycled heap block visible in the
             * log: the same wrap address with a new gen is a DIFFERENT buffer. */
            bea_logf("VB create 0x%p wrap=0x%p gen=%u len=%u usage=0x%lX"
                     " fvf=0x%lX pool=%u\n",
                     (void *)*ppVertexBuffer, (void *)b, b->gen, Length,
                     (unsigned long)Usage, (unsigned long)FVF, (unsigned)Pool);
            *ppVertexBuffer = (IDirect3DVertexBuffer9 *)b;
        }
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_CreateIndexBuffer(IDirect3DDevice9 *This,
                                                      UINT Length, DWORD Usage,
                                                      D3DFORMAT Format, D3DPOOL Pool,
                                                      IDirect3DIndexBuffer9 **ppIndexBuffer,
                                                      HANDLE *pSharedHandle)
{
    BeaDev *d = (BeaDev *)This;
    HRESULT hr = d->real->lpVtbl->CreateIndexBuffer(d->real, Length, Usage, Format,
                                                    Pool, ppIndexBuffer,
                                                    pSharedHandle);
    if (SUCCEEDED(hr) && ppIndexBuffer && *ppIndexBuffer) {
        BeaBuf *b = bea_new_buf(*ppIndexBuffer, &bea_wib_vtbl, 1, Length, Usage,
                                Format);
        if (b) {
            bea_logf("IB create 0x%p wrap=0x%p gen=%u len=%u usage=0x%lX"
                     " fmt=%u pool=%u\n",
                     (void *)*ppIndexBuffer, (void *)b, b->gen, Length,
                     (unsigned long)Usage, (unsigned)Format, (unsigned)Pool);
            *ppIndexBuffer = (IDirect3DIndexBuffer9 *)b;
        }
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE WD_ProcessVertices(IDirect3DDevice9 *This,
                                                    UINT SrcStartIndex,
                                                    UINT DestIndex,
                                                    UINT VertexCount,
                                                    IDirect3DVertexBuffer9 *pDestBuffer,
                                                    IDirect3DVertexDeclaration9 *pVertexDecl,
                                                    DWORD Flags)
{
    BeaDev *d = (BeaDev *)This;
    return d->real->lpVtbl->ProcessVertices(d->real, SrcStartIndex, DestIndex,
                                            VertexCount,
                                            bea_unwrap_vb(pDestBuffer),
                                            pVertexDecl, Flags);
}

/* -- draws ----------------------------------------------------------------- */

/* Decide whether a vertex dump will be attempted, and if not, SAY SO.
 *
 * The cap exists so an in-level log stays readable, but silently dropping the
 * vertices of a 900-vertex mesh draw would make the log's central promise --
 * every absent dump states its reason -- false for the majority of in-level
 * draws, which is exactly the case this instrument was built for. */
static int bea_verts_wanted(BeaDev *d, UINT nv)
{
    char det[64];
    if (bea_cfg_noverts) {
        bea_refuse(d, 'V', "noverts-configured", NULL);
        return 0;
    }
    if (!nv) {
        bea_refuse(d, 'V', "zero-vertex-draw", NULL);
        return 0;
    }
    if (nv > bea_cfg_maxverts) {
        snprintf(det, sizeof(det), "nv=%u cap=%u", nv, bea_cfg_maxverts);
        bea_refuse(d, 'V', "too-many-verts", det);
        return 0;
    }
    return 1;
}

static HRESULT STDMETHODCALLTYPE WD_DrawPrimitive(IDirect3DDevice9 *This,
                                                  D3DPRIMITIVETYPE PrimitiveType,
                                                  UINT StartVertex,
                                                  UINT PrimitiveCount)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging) {
        UINT nv = bea_vertex_count(PrimitiveType, PrimitiveCount);
        DWORD fvf = (d->fvfSt == BEA_ST_SET) ? d->fvf : 0;
        BeaRange r;
        bea_log_draw(d, "DP", PrimitiveType, PrimitiveCount, nv,
                     StartVertex, 0, 0, "startvtx", NULL, NULL);
        /* Resolve ONCE, then serve both records from it. The digest is cheap
         * and survives the vertex cap, so a 6,000-vertex mesh still gets an
         * identity and a bounding box even when its full dump is refused. */
        if (bea_stream0_range(d, StartVertex, nv, &r)) {
            if (bea_cfg_digest)
                bea_geom_digest(d, &r, "vb", fvf);
            if (bea_verts_wanted(d, nv) && bea_vgate(d, nv, fvf))
                bea_dump_range(d, &r, fvf);
        }
        d->draws++;
    }
    return d->real->lpVtbl->DrawPrimitive(d->real, PrimitiveType, StartVertex,
                                          PrimitiveCount);
}

static HRESULT STDMETHODCALLTYPE WD_DrawIndexedPrimitive(IDirect3DDevice9 *This,
                                                         D3DPRIMITIVETYPE PrimitiveType,
                                                         INT BaseVertexIndex,
                                                         UINT MinVertexIndex,
                                                         UINT NumVertices,
                                                         UINT startIndex,
                                                         UINT primCount)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging) {
        /* minvtx is part of the vertex run's origin and the `I` values are
         * relative to BaseVertexIndex, so without it the I and V lines are in
         * different coordinate systems and the log carries nothing to reconcile
         * them. */
        DWORD fvf = (d->fvfSt == BEA_ST_SET) ? d->fvf : 0;
        UINT ni = bea_vertex_count(PrimitiveType, primCount);
        BeaRange rv, ri;
        bea_log_draw(d, "DIP", PrimitiveType, primCount, NumVertices,
                     (UINT)BaseVertexIndex, startIndex, MinVertexIndex,
                     "basevtx", "startidx", "minvtx");
        if (BaseVertexIndex < 0) {
            bea_refuse(d, 'V', "negative-basevtx", NULL);
            bea_refuse(d, 'I', "negative-basevtx", NULL);
        } else {
            int haveV = bea_stream0_range(d, (UINT)BaseVertexIndex +
                                          MinVertexIndex, NumVertices, &rv);
            int haveI = bea_index_range(d, startIndex, ni, &ri);
            int wantV;
            if (haveV && bea_cfg_digest)
                bea_geom_digest(d, &rv, "vb", fvf);
            if (haveI && bea_cfg_digest)
                bea_geom_digest(d, &ri, "ib", 0);
            /* Evaluated ONCE. Calling the gate again for the index run would
             * emit a second refusal for the same decision and double it in the
             * tally, which is what makes the tally worth reading. */
            wantV = bea_verts_wanted(d, NumVertices) &&
                    bea_vgate(d, NumVertices, fvf);
            if (haveV && wantV)
                bea_dump_range(d, &rv, fvf);
            if (haveI) {
                if (!wantV) {
                    bea_refuse(d, 'I', "vertex-dump-refused", NULL);
                } else if (ni > bea_cfg_maxverts) {
                    char det[64];
                    snprintf(det, sizeof(det), "ni=%u cap=%u", ni,
                             bea_cfg_maxverts);
                    bea_refuse(d, 'I', "too-many-indices", det);
                } else {
                    bea_dump_index_range(d, &ri);
                }
            }
        }
        d->draws++;
    }
    return d->real->lpVtbl->DrawIndexedPrimitive(d->real, PrimitiveType,
                                                 BaseVertexIndex, MinVertexIndex,
                                                 NumVertices, startIndex,
                                                 primCount);
}

static HRESULT STDMETHODCALLTYPE WD_DrawPrimitiveUP(IDirect3DDevice9 *This,
                                                    D3DPRIMITIVETYPE primitive_type,
                                                    UINT primitive_count,
                                                    const void *data, UINT stride)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging) {
        UINT nv = bea_vertex_count(primitive_type, primitive_count);
        DWORD fvf = d->fvfSt == BEA_ST_SET ? d->fvf : 0;
        bea_log_draw(d, "DPUP", primitive_type, primitive_count, nv,
                     stride, 0, 0, "upstride", NULL, NULL);
        if (bea_verts_wanted(d, nv) && bea_vgate(d, nv, fvf))
            bea_dump_run(d, fvf, (const unsigned char *)data, stride, nv);
        d->draws++;
    }
    return d->real->lpVtbl->DrawPrimitiveUP(d->real, primitive_type,
                                            primitive_count, data, stride);
}

static HRESULT STDMETHODCALLTYPE WD_DrawIndexedPrimitiveUP(IDirect3DDevice9 *This,
                                                           D3DPRIMITIVETYPE primitive_type,
                                                           UINT min_vertex_idx,
                                                           UINT vertex_count,
                                                           UINT primitive_count,
                                                           const void *index_data,
                                                           D3DFORMAT index_format,
                                                           const void *data,
                                                           UINT stride)
{
    BeaDev *d = (BeaDev *)This;
    if (d->logging) {
        DWORD fvf = d->fvfSt == BEA_ST_SET ? d->fvf : 0;
        bea_log_draw(d, "DIPUP", primitive_type, primitive_count, vertex_count,
                     stride, min_vertex_idx, 0, "upstride", "minvtx", NULL);
        if (bea_verts_wanted(d, vertex_count) &&
            bea_vgate(d, vertex_count, fvf))
            bea_dump_run(d, fvf,
                         (const unsigned char *)data +
                             (size_t)min_vertex_idx * stride,
                         stride, vertex_count);
        d->draws++;
    }
    return d->real->lpVtbl->DrawIndexedPrimitiveUP(d->real, primitive_type,
                                                   min_vertex_idx, vertex_count,
                                                   primitive_count, index_data,
                                                   index_format, data, stride);
}

#define BEA_REAL(p) (((BeaDev *)(p))->real)
#include "idirect3ddevice9.inc"
#undef BEA_REAL

static IDirect3DDevice9 *bea_wrap_device(IDirect3DDevice9 *real,
                                         const D3DPRESENT_PARAMETERS *pp,
                                         DWORD behavior)
{
    BeaDev *d;
    if (!real)
        return NULL;
    d = (BeaDev *)calloc(1, sizeof(BeaDev));
    if (!d)
        return real;
    d->base.lpVtbl = &bea_wd_vtbl;
    d->real = real;
    d->ref = 1;
    d->behavior = behavior;
    bea_dev_seed_defaults(d, pp);
    d->logging = (bea_cfg_firstframe == 0 && bea_cfg_maxframes > 0);
    bea_window_open = d->logging;
    bea_dev_enrol(d);
    return (IDirect3DDevice9 *)d;
}

/* ================================ IDirect3D9 ============================== */

static ULONG STDMETHODCALLTYPE W9_AddRef(IDirect3D9 *This)
{
    BeaD3D9 *w = (BeaD3D9 *)This;
    w->real->lpVtbl->AddRef(w->real);
    return (ULONG)InterlockedIncrement(&w->ref);
}

static ULONG STDMETHODCALLTYPE W9_Release(IDirect3D9 *This)
{
    BeaD3D9 *w = (BeaD3D9 *)This;
    LONG r = InterlockedDecrement(&w->ref);
    w->real->lpVtbl->Release(w->real);
    if (r <= 0) {
        free(w);
        return 0;
    }
    return (ULONG)r;
}

static HRESULT STDMETHODCALLTYPE W9_QueryInterface(IDirect3D9 *This, REFIID riid,
                                                   void **ppvObject)
{
    BeaD3D9 *w = (BeaD3D9 *)This;
    void *p = NULL;
    HRESULT hr = w->real->lpVtbl->QueryInterface(w->real, riid, &p);
    if (FAILED(hr) || !p) {
        if (ppvObject)
            *ppvObject = NULL;
        return hr;
    }
    if (p == (void *)w->real) {
        w->real->lpVtbl->Release(w->real);
        W9_AddRef(This);
        *ppvObject = This;
    } else {
        bea_logf("D3D9 qi-unwrapped 0x%p\n", p);
        *ppvObject = p;
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE W9_CreateDevice(IDirect3D9 *This, UINT Adapter,
                                                 D3DDEVTYPE DeviceType,
                                                 HWND hFocusWindow,
                                                 DWORD BehaviorFlags,
                                                 D3DPRESENT_PARAMETERS *pPresentationParameters,
                                                 struct IDirect3DDevice9 **ppReturnedDeviceInterface)
{
    BeaD3D9 *w = (BeaD3D9 *)This;
    HRESULT hr = w->real->lpVtbl->CreateDevice(w->real, Adapter, DeviceType,
                                               hFocusWindow, BehaviorFlags,
                                               pPresentationParameters,
                                               ppReturnedDeviceInterface);
    if (FAILED(hr) || !ppReturnedDeviceInterface || !*ppReturnedDeviceInterface) {
        bea_logf("DEV create FAILED hr=0x%08lX\n", (unsigned long)hr);
        return hr;
    }
    if (pPresentationParameters) {
        const D3DPRESENT_PARAMETERS *p = pPresentationParameters;
        bea_logf("DEV create adapter=%u devtype=%u behavior=0x%08lX hwnd=0x%p"
                 " bb=%ux%u fmt=%u count=%u windowed=%d depth=%d depthfmt=%u"
                 " presentflags=0x%lX interval=0x%lX pure=%d\n",
                 Adapter, (unsigned)DeviceType, (unsigned long)BehaviorFlags,
                 (void *)hFocusWindow,
                 (unsigned)p->BackBufferWidth, (unsigned)p->BackBufferHeight,
                 (unsigned)p->BackBufferFormat, (unsigned)p->BackBufferCount,
                 (int)p->Windowed, (int)p->EnableAutoDepthStencil,
                 (unsigned)p->AutoDepthStencilFormat,
                 (unsigned long)p->Flags,
                 (unsigned long)p->PresentationInterval,
                 (BehaviorFlags & D3DCREATE_PUREDEVICE) ? 1 : 0);
    }
    *ppReturnedDeviceInterface =
        bea_wrap_device(*ppReturnedDeviceInterface, pPresentationParameters,
                        BehaviorFlags);
    bea_log_flush();
    return hr;
}

#define BEA_REAL(p) (((BeaD3D9 *)(p))->real)
#include "idirect3d9.inc"
#undef BEA_REAL

IDirect3D9 *bea_wrap_d3d9(IDirect3D9 *real)
{
    BeaD3D9 *w;
    if (!real)
        return NULL;
    w = (BeaD3D9 *)calloc(1, sizeof(BeaD3D9));
    if (!w)
        return real;
    w->base.lpVtbl = &bea_w9_vtbl;
    w->real = real;
    w->ref = 1;
    return (IDirect3D9 *)w;
}

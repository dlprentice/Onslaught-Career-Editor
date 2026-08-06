/* bea-d3d9-proxy -- exports, real-DLL resolution, logging.
 *
 * Every export of the real system d3d9.dll is re-exported here at its original
 * ordinal. All but Direct3DCreate9 / Direct3DCreate9Ex are naked tail-jump
 * thunks that resolve lazily and jump straight to the real implementation, so
 * arguments and calling convention are untouched and nothing has to be loaded
 * from DllMain (the loader lock forbids LoadLibrary there).
 */

#include "proxy.h"
#include <stdarg.h>
#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>
#include <string.h>

/* 2: adds the transform shadow (`M` rows, w=/v=/p= on every draw), the
 *    per-draw geometry digest (`G` rows), texture creation identity (`T` rows)
 *    and the vertex-dump gating predicates. Version 1 readers see only new
 *    record letters and new trailing fields; no existing field changed. */
#define BEA_PROXY_VERSION "2"

HMODULE bea_real_dll = NULL;
int bea_enabled = 0;
unsigned bea_cfg_maxframes = 300;
unsigned bea_cfg_firstframe = 0;
unsigned bea_cfg_maxverts = 64;
int bea_cfg_noverts = 0;
int bea_cfg_strictcov = 0;
int bea_cfg_fault_noclearbind = 0;
unsigned bea_cfg_fault_createtexture_after = 0;
unsigned bea_cfg_fault_createtexture_hr = 0x80004005u; /* E_FAIL */
int bea_cfg_fault_createtexture_sticky = 0;
unsigned bea_fault_createtexture_count = 0;
unsigned bea_cfg_vdraw_first = 0;
unsigned bea_cfg_vdraw_last = 0xFFFFFFFFu;
unsigned bea_cfg_vminverts = 0;
unsigned bea_cfg_vfvf = 0;
unsigned bea_cfg_vbudget = 0;
/* OFF by default: with it on, the SECOND draw of identical bytes is a one-line
 * back-reference rather than a dump, which is a different log grammar from
 * version 1. It is a volume tool for a deliberate mass dump, not a default. */
int bea_cfg_vdedup = 0;
int bea_cfg_digest = 1;
int bea_cfg_texhash = 0;

/* ------------------------------------------------------------------ exports */

/* Ordinals and names as exported by C:\Windows\SysWOW64\d3d9.dll.
 * build.ps1 verifies this table against the live system DLL before compiling. */
#define BEA_EXPORT_LIST(X)                                                     \
    X(16, NULL)                                                                \
    X(17, NULL)                                                                \
    X(18, NULL)                                                                \
    X(19, NULL)                                                                \
    X(20, "Direct3DCreate9On12")                                               \
    X(21, "Direct3DCreate9On12Ex")                                             \
    X(22, NULL)                                                                \
    X(23, NULL)                                                                \
    X(24, "Direct3DShaderValidatorCreate9")                                    \
    X(25, "PSGPError")                                                         \
    X(26, "PSGPSampleTexture")                                                 \
    X(27, "D3DPERF_BeginEvent")                                                \
    X(28, "D3DPERF_EndEvent")                                                  \
    X(29, "D3DPERF_GetStatus")                                                 \
    X(30, "D3DPERF_QueryRepeatFrame")                                          \
    X(31, "D3DPERF_SetMarker")                                                 \
    X(32, "D3DPERF_SetOptions")                                                \
    X(33, "D3DPERF_SetRegion")                                                 \
    X(34, "DebugSetLevel")                                                     \
    X(35, "DebugSetMute")                                                      \
    X(36, "Direct3D9EnableMaximizedWindowedModeShim")                          \
    X(37, "Direct3DCreate9")                                                   \
    X(38, "Direct3DCreate9Ex")

#define BEA_ORD_MIN 16
#define BEA_ORD_MAX 38
#define BEA_ORD_COUNT (BEA_ORD_MAX - BEA_ORD_MIN + 1)

static const char *const bea_export_name[BEA_ORD_COUNT] = {
#define X(ord, name) name,
    BEA_EXPORT_LIST(X)
#undef X
};

static FARPROC bea_export_addr[BEA_ORD_COUNT];

/* Thunks for every export we do not implement ourselves (16..36).
 *
 *   push  <ordinal>
 *   call  bea_resolve      ; __cdecl, returns the real address in eax
 *   add   esp, 4           ; esp back to entry value, return address at [esp]
 *   jmp   eax              ; tail jump: the callee's arguments are untouched
 *
 * eax/ecx/edx are caller-saved on both cdecl and stdcall, so clobbering eax is
 * safe, and no argument ever lives in a register for these conventions. */
#define BEA_THUNK_LIST(X)                                                      \
    X(16) X(17) X(18) X(19) X(20) X(21) X(22) X(23) X(24) X(25) X(26)          \
    X(27) X(28) X(29) X(30) X(31) X(32) X(33) X(34) X(35) X(36)

#define BEA_EMIT_THUNK(ord)                                                    \
    __asm__(".text\n"                                                          \
            ".globl _bea_thunk_" #ord "\n"                                     \
            "_bea_thunk_" #ord ":\n"                                           \
            "  pushl $" #ord "\n"                                              \
            "  call _bea_resolve\n"                                            \
            "  addl $4, %esp\n"                                                \
            "  jmp *%eax\n");

BEA_THUNK_LIST(BEA_EMIT_THUNK)

/* Reached only if the OS d3d9.dll is missing an export it used to have -- a
 * state in which the game could not have started without this proxy either.
 * Returns zero; it does not pop stdcall arguments, and cannot: the thunk has no
 * idea how many there are. Documented rather than hidden. */
__asm__(".text\n"
        ".globl _bea_null_stub\n"
        "_bea_null_stub:\n"
        "  xorl %eax, %eax\n"
        "  ret\n");
void bea_null_stub(void);

void *__cdecl bea_resolve(unsigned ordinal);

void *__cdecl bea_resolve(unsigned ordinal)
{
    unsigned idx;
    bea_init();
    if (ordinal < BEA_ORD_MIN || ordinal > BEA_ORD_MAX)
        return (void *)bea_null_stub;
    idx = ordinal - BEA_ORD_MIN;
    if (!bea_export_addr[idx] && bea_real_dll) {
        const char *nm = bea_export_name[idx];
        bea_export_addr[idx] = nm
            ? GetProcAddress(bea_real_dll, nm)
            : GetProcAddress(bea_real_dll, MAKEINTRESOURCEA(ordinal));
    }
    if (!bea_export_addr[idx])
        return (void *)bea_null_stub;
    return (void *)bea_export_addr[idx];
}

/* ------------------------------------------------------------------ logging */

static CRITICAL_SECTION bea_cs;
static int bea_cs_ready = 0;
static FILE *bea_fp = NULL;

int bea_log_open(void) { return bea_fp != NULL; }

void bea_logf(const char *fmt, ...)
{
    char buf[8192];
    int n;
    va_list ap;
    if (!bea_fp)
        return;
    va_start(ap, fmt);
    n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n < 0 || n > (int)sizeof(buf) - 1)
        n = (int)sizeof(buf) - 1;
    buf[n] = 0;
    if (bea_cs_ready)
        EnterCriticalSection(&bea_cs);
    fwrite(buf, 1, (size_t)n, bea_fp);
    if (bea_cs_ready)
        LeaveCriticalSection(&bea_cs);
}

void bea_log_flush(void)
{
    if (!bea_fp)
        return;
    if (bea_cs_ready)
        EnterCriticalSection(&bea_cs);
    fflush(bea_fp);
    if (bea_cs_ready)
        LeaveCriticalSection(&bea_cs);
}

/* The same critical section guards the live-wrapper registries in wrap.c. A
 * CRITICAL_SECTION is reentrant for the owning thread, so holding it across a
 * bea_logf call is safe. */
void bea_lock(void)
{
    if (bea_cs_ready)
        EnterCriticalSection(&bea_cs);
}

void bea_unlock(void)
{
    if (bea_cs_ready)
        LeaveCriticalSection(&bea_cs);
}

/* --------------------------------------------------------------------- init */

static int bea_env(const wchar_t *name, wchar_t *out, DWORD cch)
{
    DWORD n = GetEnvironmentVariableW(name, out, cch);
    return (n > 0 && n < cch);
}

static unsigned bea_env_uint(const wchar_t *name, unsigned dflt)
{
    wchar_t buf[64];
    if (!bea_env(name, buf, 64))
        return dflt;
    if (!buf[0])
        return dflt;
    return (unsigned)wcstoul(buf, NULL, 0);
}

static void bea_make_parent_dirs(const wchar_t *path)
{
    wchar_t dir[MAX_PATH * 2];
    size_t i, last = 0;
    wcsncpy(dir, path, MAX_PATH * 2 - 1);
    dir[MAX_PATH * 2 - 1] = 0;
    for (i = 0; dir[i]; ++i)
        if (dir[i] == L'\\' || dir[i] == L'/')
            last = i;
    if (!last)
        return;
    dir[last] = 0;
    CreateDirectoryW(dir, NULL);
}

static void bea_open_log(void)
{
    wchar_t path[MAX_PATH * 2];
    wchar_t exe[MAX_PATH * 2];
    wchar_t real[MAX_PATH];
    SYSTEMTIME st;

    if (bea_env(L"BEA_D3D9_LOG", path, MAX_PATH * 2)) {
        /* explicit path wins */
    } else {
        wchar_t on[64];
        if (!bea_env(L"BEA_D3D9_CAPTURE", on, 64) || !on[0] || on[0] == L'0')
            return; /* inert: neither variable set */
        GetLocalTime(&st);
        _snwprintf(path, MAX_PATH * 2 - 1,
                   L"G:\\bea-d3d9-capture\\d3d9-%04u%02u%02u-%02u%02u%02u-%lu.log",
                   st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond,
                   (unsigned long)GetCurrentProcessId());
        path[MAX_PATH * 2 - 1] = 0;
    }

    bea_make_parent_dirs(path);
    bea_fp = _wfopen(path, L"wb");
    if (!bea_fp)
        return; /* silent: a capture that cannot write is simply not a capture */
    setvbuf(bea_fp, NULL, _IOFBF, 1 << 20);

    exe[0] = 0;
    GetModuleFileNameW(NULL, exe, MAX_PATH * 2);
    real[0] = 0;
    if (bea_real_dll)
        GetModuleFileNameW(bea_real_dll, real, MAX_PATH);

    GetLocalTime(&st);
    bea_logf("# bea-d3d9-proxy v%s\n", BEA_PROXY_VERSION);
    bea_logf("# time=%04u-%02u-%02uT%02u:%02u:%02u pid=%lu\n",
             st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond,
             (unsigned long)GetCurrentProcessId());
    bea_logf("# exe=%S\n", exe);
    bea_logf("# real=%S\n", real);
    bea_logf("# cfg firstframe=%u maxframes=%u maxverts=%u noverts=%d strictcov=%d\n",
             bea_cfg_firstframe, bea_cfg_maxframes, bea_cfg_maxverts,
             bea_cfg_noverts, bea_cfg_strictcov);
    /* GATING IS NOT ABSENCE. Every predicate that can suppress a record is
     * restated here, in the file itself, so a reader who never saw the command
     * line cannot mistake a narrow capture for a sparse frame. */
    bea_logf("# gating vdrawfirst=%u vdrawlast=%u vminverts=%u vfvf=0x%X"
             " vbudget=%u vdedup=%d digest=%d texhash=%d\n",
             bea_cfg_vdraw_first, bea_cfg_vdraw_last, bea_cfg_vminverts,
             bea_cfg_vfvf, bea_cfg_vbudget, bea_cfg_vdedup, bea_cfg_digest,
             bea_cfg_texhash);
    bea_logf("# 'M <id> <slot> m=<16 floats>' = a transform, row-major as D3D"
             " stores it, emitted once per distinct value at its first use."
             " id=0 is the identity the device starts with. Every 'D' row"
             " carries w=/v=/p= naming the ids in force for that draw; 'mul'"
             " on an M row means the value came from MultiplyTransform and"
             " ASSUMES the order new=current*arg.\n");
    bea_logf("# 'G <f> <d> vb|ib ...' = geometry digest: identity, FNV-1a-64"
             " hash and position bounds of the exact bytes that draw reads,"
             " with unlocks= (how many times the buffer has been rewritten)"
             " and lastunlock= (the frame of the most recent rewrite). A mesh"
             " whose h= changes every frame is being re-written on the CPU.\n");
    bea_logf("# 'T create serial=<n> ...' = a texture, at creation, in load"
             " order. Draw rows name a bound texture by that serial.\n");
    bea_logf("# render-state and stage-state values are shadowed from Set* calls:"
             " '~' = D3D default never set by the game, '?' = unknown\n");
    bea_logf("# 'V f d - none <reason>' = no vertices recorded, and why;"
             " '- warn <reason>' = recorded but qualified. Both are tallied at"
             " '# refusals'.\n");
    if (bea_cfg_fault_noclearbind)
        bea_logf("# FAULT-INJECTION noclearbind=1 -- THIS LOG IS A TEST"
                 " ARTEFACT, NOT EVIDENCE ABOUT THE GAME\n");
    bea_log_flush();
    bea_enabled = 1;
}

static BOOL CALLBACK bea_init_once(PINIT_ONCE once, PVOID param, PVOID *ctx)
{
    wchar_t sys[MAX_PATH];
    UINT n;
    (void)once;
    (void)param;
    (void)ctx;

    InitializeCriticalSection(&bea_cs);
    bea_cs_ready = 1;

    /* Absolute path only. Loading "d3d9.dll" by bare name would find this DLL
     * again (application directory first) and recurse into itself. For a 32-bit
     * process GetSystemDirectoryW is redirected to SysWOW64, which is correct. */
    n = GetSystemDirectoryW(sys, MAX_PATH);
    if (n > 0 && n < MAX_PATH - 12) {
        wcscat(sys, L"\\d3d9.dll");
        bea_real_dll = LoadLibraryW(sys);
    }

    bea_cfg_maxframes = bea_env_uint(L"BEA_D3D9_MAXFRAMES", 300);
    bea_cfg_firstframe = bea_env_uint(L"BEA_D3D9_FIRSTFRAME", 0);
    bea_cfg_maxverts = bea_env_uint(L"BEA_D3D9_MAXVERTS", 64);
    bea_cfg_noverts = (int)bea_env_uint(L"BEA_D3D9_NOVERTS", 0);
    bea_cfg_strictcov = (int)bea_env_uint(L"BEA_D3D9_STRICTCOV", 0);
    bea_cfg_fault_noclearbind =
        (int)bea_env_uint(L"BEA_D3D9_FAULT_NOCLEARBIND", 0);
    bea_cfg_fault_createtexture_after =
        bea_env_uint(L"BEA_D3D9_FAULT_CREATETEXTURE_AFTER", 0);
    bea_cfg_fault_createtexture_hr =
        bea_env_uint(L"BEA_D3D9_FAULT_CREATETEXTURE_HR", 0x80004005u);
    bea_cfg_fault_createtexture_sticky =
        (int)bea_env_uint(L"BEA_D3D9_FAULT_CREATETEXTURE_STICKY", 0);
    bea_cfg_vdraw_first = bea_env_uint(L"BEA_D3D9_VDRAWFIRST", 0);
    bea_cfg_vdraw_last = bea_env_uint(L"BEA_D3D9_VDRAWLAST", 0xFFFFFFFFu);
    bea_cfg_vminverts = bea_env_uint(L"BEA_D3D9_VMINVERTS", 0);
    bea_cfg_vfvf = bea_env_uint(L"BEA_D3D9_VFVF", 0);
    bea_cfg_vbudget = bea_env_uint(L"BEA_D3D9_VBUDGET", 0);
    bea_cfg_vdedup = (int)bea_env_uint(L"BEA_D3D9_VDEDUP", 0);
    bea_cfg_digest = (int)bea_env_uint(L"BEA_D3D9_DIGEST", 1);
    bea_cfg_texhash = (int)bea_env_uint(L"BEA_D3D9_TEXHASH", 0);

    bea_open_log();

    /* A back-buffer grab needs the device wrapped but needs no draw log, so it
     * enables the proxy on its own. bea_logf is a no-op with no log file open,
     * which is exactly what a shots-only run wants. */
    bea_shot_init();
    if (bea_shot_enabled) {
        bea_enabled = 1;
        bea_logf("# back-buffer grab armed\n");
        bea_log_flush();
    }
    /* Fault-injection of CreateTexture needs the device wrapped even when no
     * capture log is open (probe runs use CDB/TTD, not the draw recorder). */
    if (bea_cfg_fault_createtexture_after > 0) {
        bea_enabled = 1;
        /* Open a small fault log if none exists so FAULT lines are visible. */
        if (!bea_fp) {
            wchar_t path[MAX_PATH * 2];
            SYSTEMTIME st;
            GetLocalTime(&st);
            _snwprintf(path, MAX_PATH * 2 - 1,
                       L"G:\\bea-d3d9-capture\\d3d9-fault-%04u%02u%02u-%02u%02u%02u-%lu.log",
                       st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute,
                       st.wSecond, (unsigned long)GetCurrentProcessId());
            path[MAX_PATH * 2 - 1] = 0;
            bea_make_parent_dirs(path);
            bea_fp = _wfopen(path, L"wb");
            if (bea_fp) {
                setvbuf(bea_fp, NULL, _IOFBF, 1 << 16);
                bea_logf("# bea-d3d9-proxy FAULT-INJECTION CreateTexture after=%u "
                         "hr=0x%08lX sticky=%d\n",
                         bea_cfg_fault_createtexture_after,
                         (unsigned long)bea_cfg_fault_createtexture_hr,
                         bea_cfg_fault_createtexture_sticky);
                bea_log_flush();
            }
        } else {
            bea_logf("# FAULT-INJECTION CreateTexture after=%u hr=0x%08lX sticky=%d\n",
                     bea_cfg_fault_createtexture_after,
                     (unsigned long)bea_cfg_fault_createtexture_hr,
                     bea_cfg_fault_createtexture_sticky);
            bea_log_flush();
        }
    }
    return TRUE;
}

void bea_init(void)
{
    static INIT_ONCE once = INIT_ONCE_STATIC_INIT;
    InitOnceExecuteOnce(&once, bea_init_once, NULL, NULL);
}

/* ------------------------------------------------------- implemented exports */

typedef IDirect3D9 *(WINAPI *PFN_Direct3DCreate9)(UINT);
typedef HRESULT (WINAPI *PFN_Direct3DCreate9Ex)(UINT, IDirect3D9Ex **);

IDirect3D9 *WINAPI bea_Direct3DCreate9(UINT SDKVersion);
HRESULT WINAPI bea_Direct3DCreate9Ex(UINT SDKVersion, IDirect3D9Ex **ppD3D);

IDirect3D9 *WINAPI bea_Direct3DCreate9(UINT SDKVersion)
{
    PFN_Direct3DCreate9 fn;
    IDirect3D9 *real;

    fn = (PFN_Direct3DCreate9)bea_resolve(37);
    if ((void *)fn == (void *)bea_null_stub)
        return NULL;
    real = fn(SDKVersion);
    if (!real || !bea_enabled)
        return real;
    bea_logf("D3D9 create sdk=0x%X real=0x%p\n", SDKVersion, (void *)real);
    return bea_wrap_d3d9(real);
}

HRESULT WINAPI bea_Direct3DCreate9Ex(UINT SDKVersion, IDirect3D9Ex **ppD3D)
{
    PFN_Direct3DCreate9Ex fn;
    HRESULT hr;

    fn = (PFN_Direct3DCreate9Ex)bea_resolve(38);
    if ((void *)fn == (void *)bea_null_stub)
        return E_NOTIMPL;
    hr = fn(SDKVersion, ppD3D);
    /* Not wrapped: an Ex device is a different interface and this title does not
     * use one. Recorded so a capture can never silently be empty for this
     * reason. */
    if (bea_enabled)
        bea_logf("D3D9EX create sdk=0x%X hr=0x%08lX -- NOT WRAPPED\n",
                 SDKVersion, (unsigned long)hr);
    return hr;
}

/* ------------------------------------------------------------------ DllMain */

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    switch (reason) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(inst);
        /* Deliberately nothing else here: no LoadLibrary, no file I/O, no
         * window or thread creation under the loader lock. */
        break;
    case DLL_PROCESS_DETACH:
        if (bea_shot_enabled)
            bea_shot_close();
        if (bea_fp) {
            bea_log_summary();
            bea_logf("# detach\n");
            fflush(bea_fp);
        }
        break;
    default:
        break;
    }
    return TRUE;
}

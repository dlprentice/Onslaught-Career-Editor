/* bea-d3d9-proxy -- passive Direct3D 9 draw-call recorder.
 *
 * See tools/d3d9-proxy/README.md. Hard rules this file exists to enforce:
 *   - no windows, no dialogs, no console, no input, no network;
 *   - if anything fails, fall back to pure pass-through so the game still runs;
 *   - completely inert unless an environment variable enables it.
 */
#ifndef BEA_D3D9_PROXY_H
#define BEA_D3D9_PROXY_H

#define WIN32_LEAN_AND_MEAN
#define CINTERFACE
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>

/* ---- real system d3d9.dll ------------------------------------------------ */

extern HMODULE bea_real_dll;

/* Idempotent, thread-safe, never called from DllMain (loader lock). */
void bea_init(void);

/* ---- capture configuration (all resolved once, in bea_init) -------------- */

extern int bea_enabled;          /* 0 => wrap nothing at all, pure pass-through */
extern unsigned bea_cfg_maxframes;
extern unsigned bea_cfg_firstframe;
extern unsigned bea_cfg_maxverts;
extern int bea_cfg_noverts;
extern int bea_cfg_strictcov;    /* 1 => refuse provisional coverage instead of flagging it */

/* ---- volume gating for the per-draw vertex dump --------------------------
 *
 * The full `V` dump is the expensive record: an in-level frame issues ~1,200
 * draws and the largest carry ~6,000 vertices, so an ungated dump is hundreds
 * of megabytes per frame. These predicates narrow WHICH draws get one. Every
 * draw the gate excludes still emits a refusal naming the gate, and every
 * setting is restated in the log header, so a gated absence can never be read
 * as "the game drew nothing there". */
extern unsigned bea_cfg_vdraw_first;   /* lowest draw index eligible for a V dump */
extern unsigned bea_cfg_vdraw_last;    /* highest draw index eligible */
extern unsigned bea_cfg_vminverts;     /* skip draws with fewer vertices than this */
extern unsigned bea_cfg_vfvf;          /* if nonzero, dump only this exact FVF */
extern unsigned bea_cfg_vbudget;       /* max V lines per frame, 0 = unlimited */
extern int bea_cfg_vdedup;             /* 1 => a repeated byte-range is a `ref=` line */

/* ---- geometry digest ------------------------------------------------------
 *
 * One line per draw carrying the identity, hash and position bounding box of
 * the exact bytes the draw reads, plus how many times that buffer has been
 * rewritten. Cheap enough to leave on for a whole level, and it is what
 * answers "is this mesh re-written per frame (CPU skinning) or static". */
extern int bea_cfg_digest;

/* ---- texture content hashing ---------------------------------------------
 *
 * OFF by default, because it is the one thing in this proxy that reads back a
 * Direct3D resource rather than only observing calls. When on, a texture is
 * locked READONLY exactly once, at its first use in a logged draw, and only if
 * its own descriptor says the read is legal and side-effect free. */
extern int bea_cfg_texhash;

/* FAULT INJECTION, for the self-test only. 1 => a dying buffer wrapper does NOT
 * retract itself from the devices that have it bound, leaving exactly the
 * dangling binding this proxy exists to avoid. It is here so the SECOND line of
 * defence -- the generation check -- can be proven to refuse rather than merely
 * asserted to. Any log produced with it set is stamped as a test artefact. */
extern int bea_cfg_fault_noclearbind;

/* FAULT INJECTION for HResultToString / CreateTexture error-path probes.
 * When bea_cfg_fault_createtexture_after > 0, the Nth CreateTexture call
 * (1-based) returns bea_cfg_fault_createtexture_hr instead of calling through.
 * When bea_cfg_fault_createtexture_sticky != 0, every call with count >= N fails
 * (not only the single Nth call). Enables device wrapping even without a
 * capture log. Logs stamped FAULT-INJECTION. Not production evidence. */
extern unsigned bea_cfg_fault_createtexture_after;
extern unsigned bea_cfg_fault_createtexture_hr;
extern int bea_cfg_fault_createtexture_sticky;
extern unsigned bea_fault_createtexture_count;

/* ---- logging ------------------------------------------------------------- */

void bea_logf(const char *fmt, ...);
void bea_log_flush(void);
int bea_log_open(void);          /* nonzero once the log file is writable */

/* Tally of every refusal and warning the run emitted, by reason. Written at the
 * end of the capture window and again at DLL_PROCESS_DETACH so a reader can see
 * what was NOT recorded without counting lines. */
void bea_log_summary(void);

/* ---- serialisation ------------------------------------------------------- */

/* Guards the live-wrapper registries in wrap.c. Reentrant (a CRITICAL_SECTION),
 * so it is safe to call bea_logf while holding it. */
void bea_lock(void);
void bea_unlock(void);

/* ---- back-buffer grab (shot.c) ------------------------------------------- */

/* Nonzero only when BEA_D3D9_SHOT selected at least one frame AND the output
 * directory and manifest were both opened. Enables device wrapping on its own,
 * so a capture run needs no draw log. */
extern int bea_shot_enabled;

void bea_shot_init(void);                       /* from bea_init, once */
void bea_shot_present(IDirect3DDevice9 *real, unsigned frame);
void bea_shot_pre_reset(void);                  /* BEFORE Reset: drop DEFAULT pool */
void bea_shot_reset(void);                      /* AFTER Reset: back buffer may differ */
void bea_shot_close(void);

/* ---- wrappers ------------------------------------------------------------ */

IDirect3D9 *bea_wrap_d3d9(IDirect3D9 *real);

#endif /* BEA_D3D9_PROXY_H */

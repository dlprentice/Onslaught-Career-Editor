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

/* FAULT INJECTION, for the self-test only. 1 => a dying buffer wrapper does NOT
 * retract itself from the devices that have it bound, leaving exactly the
 * dangling binding this proxy exists to avoid. It is here so the SECOND line of
 * defence -- the generation check -- can be proven to refuse rather than merely
 * asserted to. Any log produced with it set is stamped as a test artefact. */
extern int bea_cfg_fault_noclearbind;

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

/* ---- wrappers ------------------------------------------------------------ */

IDirect3D9 *bea_wrap_d3d9(IDirect3D9 *real);

#endif /* BEA_D3D9_PROXY_H */

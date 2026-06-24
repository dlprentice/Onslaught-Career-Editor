/* address: 0x0055d6a0 */
/* name: CRT__SehPopExceptionFrameAndJump */
/* signature: void __stdcall CRT__SehPopExceptionFrameAndJump(void * param_1) */


void CRT__SehPopExceptionFrameAndJump(void *param_1)

{
  ExceptionList = *(void **)ExceptionList;
                    /* WARNING: Could not recover jumptable at 0x0055d6cb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*param_1)();
  return;
}

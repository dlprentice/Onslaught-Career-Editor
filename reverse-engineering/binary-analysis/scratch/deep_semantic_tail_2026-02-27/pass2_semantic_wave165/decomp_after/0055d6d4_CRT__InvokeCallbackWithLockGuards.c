/* address: 0x0055d6d4 */
/* name: CRT__InvokeCallbackWithLockGuards */
/* signature: void __stdcall CRT__InvokeCallbackWithLockGuards(int param_1, void * param_2) */


void CRT__InvokeCallbackWithLockGuards(int param_1,void *param_2)

{
  LOCK();
  UNLOCK();
                    /* WARNING: Could not recover jumptable at 0x0055d6d9. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*param_2)();
  return;
}

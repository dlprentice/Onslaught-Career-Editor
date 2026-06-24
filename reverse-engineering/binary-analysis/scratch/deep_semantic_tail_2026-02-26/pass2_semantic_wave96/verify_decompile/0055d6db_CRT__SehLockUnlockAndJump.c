/* address: 0x0055d6db */
/* name: CRT__SehLockUnlockAndJump */
/* signature: void __stdcall CRT__SehLockUnlockAndJump(int param_1, void * param_2) */


void CRT__SehLockUnlockAndJump(int param_1,void *param_2)

{
  LOCK();
  UNLOCK();
                    /* WARNING: Could not recover jumptable at 0x0055d6e0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*param_2)();
  return;
}

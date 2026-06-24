/* address: 0x00561179 */
/* name: CRT__LockByIndex */
/* signature: void __cdecl CRT__LockByIndex(int param_1) */


void __cdecl CRT__LockByIndex(int param_1)

{
  int *piVar1;
  LPCRITICAL_SECTION lpCriticalSection;

  piVar1 = (int *)(&DAT_00653670 + param_1 * 4);
  if (*(int *)(&DAT_00653670 + param_1 * 4) == 0) {
    lpCriticalSection = _malloc(0x18);
    if (lpCriticalSection == (LPCRITICAL_SECTION)0x0) {
      __amsg_exit(0x11);
    }
    CRT__LockByIndex(0x11);
    if (*piVar1 == 0) {
      InitializeCriticalSection(lpCriticalSection);
      *piVar1 = (int)lpCriticalSection;
    }
    else {
      CRT__FreeBase((int)lpCriticalSection);
    }
    CTexture__Helper_005611da(0x11);
  }
  EnterCriticalSection((LPCRITICAL_SECTION)*piVar1);
  return;
}

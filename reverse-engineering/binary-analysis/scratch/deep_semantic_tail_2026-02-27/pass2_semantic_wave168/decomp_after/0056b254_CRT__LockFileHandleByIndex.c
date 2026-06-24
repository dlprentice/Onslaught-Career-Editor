/* address: 0x0056b254 */
/* name: CRT__LockFileHandleByIndex */
/* signature: void __cdecl CRT__LockFileHandleByIndex(uint param_1) */


void __cdecl CRT__LockFileHandleByIndex(uint param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = (param_1 & 0x1f) * 0x24;
  iVar1 = (&DAT_009d32a0)[(int)param_1 >> 5] + iVar2;
  if (*(int *)(iVar1 + 8) == 0) {
    CRT__LockByIndex(0x11);
    if (*(int *)(iVar1 + 8) == 0) {
      InitializeCriticalSection((LPCRITICAL_SECTION)(iVar1 + 0xc));
      *(int *)(iVar1 + 8) = *(int *)(iVar1 + 8) + 1;
    }
    CTexture__Helper_005611da(0x11);
  }
  EnterCriticalSection((LPCRITICAL_SECTION)((&DAT_009d32a0)[(int)param_1 >> 5] + 0xc + iVar2));
  return;
}

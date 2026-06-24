/* address: 0x005611da */
/* name: CRT__UnlockByIndex */
/* signature: void __cdecl CRT__UnlockByIndex(int param_1) */


void __cdecl CRT__UnlockByIndex(int param_1)

{
  LeaveCriticalSection(*(LPCRITICAL_SECTION *)(&DAT_00653670 + param_1 * 4));
  return;
}

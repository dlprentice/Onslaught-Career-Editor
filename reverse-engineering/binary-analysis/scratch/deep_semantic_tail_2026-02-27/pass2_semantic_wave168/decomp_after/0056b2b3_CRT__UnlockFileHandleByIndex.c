/* address: 0x0056b2b3 */
/* name: CRT__UnlockFileHandleByIndex */
/* signature: void __cdecl CRT__UnlockFileHandleByIndex(uint param_1) */


void __cdecl CRT__UnlockFileHandleByIndex(uint param_1)

{
  LeaveCriticalSection
            ((LPCRITICAL_SECTION)
             ((&DAT_009d32a0)[(int)param_1 >> 5] + 0xc + (param_1 & 0x1f) * 0x24));
  return;
}

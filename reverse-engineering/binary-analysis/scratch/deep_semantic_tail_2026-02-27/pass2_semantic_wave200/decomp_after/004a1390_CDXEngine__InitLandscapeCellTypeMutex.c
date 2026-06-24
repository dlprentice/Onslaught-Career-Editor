/* address: 0x004a1390 */
/* name: CDXEngine__InitLandscapeCellTypeMutex */
/* signature: int __fastcall CDXEngine__InitLandscapeCellTypeMutex(int param_1) */


int __fastcall CDXEngine__InitLandscapeCellTypeMutex(int param_1)

{
  HANDLE pvVar1;

  pvVar1 = CreateMutexA((LPSECURITY_ATTRIBUTES)0x0,0,(LPCSTR)0x0);
  *(HANDLE *)(param_1 + 0x8bc) = pvVar1;
  return param_1;
}

/* address: 0x00589116 */
/* name: CDXTexture__Unk_00589116 */
/* signature: int CDXTexture__Unk_00589116(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_00589116(void)

{
  LSTATUS LVar1;
  int iVar2;
  int extraout_ECX;
  int extraout_EDX;
  _union_530 local_38 [8];
  ushort local_18;
  int local_14;
  DWORD local_10 [2];
  HKEY local_8;

  LVar1 = RegOpenKeyA((HKEY)&DAT_80000002,"Software\\Microsoft\\Direct3D",&local_8);
  if (LVar1 == 0) {
    local_10[1] = 4;
    LVar1 = RegQueryValueExA(local_8,"DisableMMX",(LPDWORD)0x0,local_10,(LPBYTE)&local_14,
                             local_10 + 1);
    if (((LVar1 == 0) && (local_10[0] == 4)) && (local_14 != 0)) {
      RegCloseKey(local_8);
      DAT_00657a80 = 0;
      return 0;
    }
    RegCloseKey(local_8);
  }
  if (DAT_00657a80 < 0) {
    DAT_00657a80 = 0;
    GetSystemInfo((LPSYSTEM_INFO)&local_38[0].s);
    if (((local_38[0].s.wProcessorArchitecture == 0) && (4 < local_18)) &&
       (iVar2 = CDXTexture__Unk_005890f1(extraout_ECX,extraout_EDX), iVar2 != 0)) {
      DAT_00657a80 = 1;
    }
  }
  return DAT_00657a80;
}

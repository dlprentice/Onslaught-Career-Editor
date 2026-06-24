/* address: 0x00527d20 */
/* name: CDXLandscape__Helper_00527d20 */
/* signature: int __fastcall CDXLandscape__Helper_00527d20(int param_1) */


int __fastcall CDXLandscape__Helper_00527d20(int param_1)

{
  int extraout_EAX;
  int extraout_EAX_00;
  int iVar1;
  int extraout_EAX_01;
  uint uVar2;

  iVar1 = *(int *)(param_1 + 0x10);
  if (iVar1 == 0) {
    if (*(int *)(param_1 + 0xc) == 0) {
      CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0);
      iVar1 = extraout_EAX;
      if (extraout_EAX < 0) {
        HResultToString();
        CConsole__Printf(&DAT_0066eb90,s_RM__Failed_ValidSoFar_on___s__d__0064bca4);
        iVar1 = extraout_EAX_00;
      }
    }
    else {
      CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0);
      iVar1 = extraout_EAX_01;
      if (extraout_EAX_01 < 0) {
        HResultToString();
        CConsole__Printf(&DAT_0066eb90,s_RM__Failed_ValidSoFar_on___s__d__0064bc78);
        uVar2 = *(int *)(param_1 + 0xc) - 1;
        *(uint *)(param_1 + 0xc) = uVar2;
        return uVar2 & 0xffffff00;
      }
    }
  }
  return CONCAT31((int3)((uint)iVar1 >> 8),1);
}

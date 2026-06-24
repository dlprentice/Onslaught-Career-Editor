/* address: 0x004419e0 */
/* name: FrontendUpdate_CheatChecks__Helper_004419e0 */
/* signature: void __fastcall FrontendUpdate_CheatChecks__Helper_004419e0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FrontendUpdate_CheatChecks__Helper_004419e0(int param_1)

{
  float fVar1;
  short *psVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  float fVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  float local_8;

  if (*(float *)(param_1 + 0x9e8) < DAT_00672fd0 - _DAT_005d8bc0) {
    *(undefined4 *)(param_1 + 0x9e8) = 0xc2c80000;
    return;
  }
  local_8 = 100.0;
  iVar5 = 0;
  do {
    iVar3 = *(int *)(param_1 + 0x9e4) - iVar5;
    iVar4 = iVar3;
    if (iVar3 < 0) {
      iVar4 = iVar3 + ((0x1dU - iVar3) / 0x1e) * 0x1e;
    }
    fVar1 = (DAT_00672fd0 - *(float *)(param_1 + 0x96c + iVar4 * 4)) * _DAT_005db024;
    if (fVar1 < _DAT_005db020 - local_8) {
      fVar1 = _DAT_005db020 - local_8;
    }
    fVar1 = _DAT_005db020 - fVar1;
    if (iVar3 < 0) {
      iVar3 = iVar3 + ((0x1dU - iVar3) / 0x1e) * 0x1e;
    }
    uVar11 = 0x3f800000;
    uVar10 = 0;
    uVar9 = 0;
    psVar2 = Text__AsciiToWideScratch((char *)(iVar3 * 0x50 + 9 + param_1));
    uVar8 = 0xff3eff84;
    uVar6 = 0x40000000;
    fVar7 = fVar1;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar6,fVar7,uVar8,psVar2,uVar9,uVar10,uVar11);
    local_8 = fVar1 - _DAT_005d85d4;
    iVar5 = iVar5 + 1;
  } while (iVar5 < 6);
  return;
}

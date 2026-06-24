/* address: 0x0040ef20 */
/* name: CMonitor__Helper_0040ef20 */
/* signature: void __fastcall CMonitor__Helper_0040ef20(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Helper_0040ef20(int param_1)

{
  float fVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  double dVar8;
  undefined4 uVar9;
  undefined1 local_24 [4];
  undefined4 *local_20;
  float local_14;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  fVar7 = DAT_006fbdfc;
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d12a8;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  dVar8 = CHeightField__Unk_0047eb80(0x6fadc8,(undefined4 *)(param_1 + 0x1c));
  fVar6 = (float)dVar8;
  fVar1 = fVar6;
  if (fVar7 < fVar6) {
    fVar1 = fVar7;
  }
  fVar1 = fVar1 - *(float *)(param_1 + 0x24);
  if (fVar1 < _DAT_005d85cc) {
    local_20 = (undefined4 *)0x0;
    CParticleManager__Unk_004cb040(local_24);
    uVar2 = *(undefined4 *)(param_1 + 0x1c);
    uVar3 = *(undefined4 *)(param_1 + 0x20);
    local_14 = fVar1 * _DAT_005d8bd8 + *(float *)(param_1 + 0x24);
    uVar4 = *(undefined4 *)(param_1 + 0x28);
    local_4 = 0;
    uVar9 = DAT_006601b0;
    if (fVar7 < fVar6) {
      uVar9 = DAT_006601b4;
    }
    CParticleManager__CreateEffect
              (uVar9,local_24,DAT_006601e8,DAT_006601ec,DAT_006601f0,DAT_006601f4,0,0);
    if (local_20 != (undefined4 *)0x0) {
      if (local_20[0x12] == 0x461c4000) {
        local_20[0x20] = uVar2;
        local_20[0x21] = uVar3;
        local_20[0x22] = local_14;
        local_20[0x23] = uVar4;
        local_20[0x10] = local_20[0x20];
        local_20[0x11] = local_20[0x21];
        local_20[0x12] = local_20[0x22];
        local_20[0x13] = local_20[0x23];
        *local_20 = uVar2;
        local_20[1] = uVar3;
        local_20[2] = local_14;
        iVar5 = local_20[0x2b];
        local_20[3] = uVar4;
      }
      else {
        local_20[0x10] = *local_20;
        local_20[0x11] = local_20[1];
        local_20[0x12] = local_20[2];
        local_20[0x13] = local_20[3];
        *local_20 = uVar2;
        local_20[1] = uVar3;
        local_20[2] = local_14;
        iVar5 = local_20[0x2b];
        local_20[3] = uVar4;
      }
      if (iVar5 != -0x40800000) {
        local_20[0x2b] = DAT_00672fd0;
      }
    }
    local_4 = 0xffffffff;
    CParticleManager__RemoveFromGlobalList();
  }
  ExceptionList = local_c;
  return;
}

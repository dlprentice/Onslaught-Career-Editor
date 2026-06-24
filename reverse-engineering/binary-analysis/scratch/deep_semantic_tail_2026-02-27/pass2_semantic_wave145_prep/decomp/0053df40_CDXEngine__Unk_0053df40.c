/* address: 0x0053df40 */
/* name: CDXEngine__Unk_0053df40 */
/* signature: int CDXEngine__Unk_0053df40(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXEngine__Unk_0053df40(void)

{
  float fVar1;
  float *pfVar2;
  undefined4 uVar3;
  int iVar4;
  int extraout_EAX;
  int iVar5;
  float *pfVar6;
  undefined4 *puVar7;
  uint uVar8;
  undefined4 *puVar9;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000014;
  float in_stack_00000018;
  float in_stack_0000001c;
  float in_stack_ffffff2c;
  float in_stack_ffffff30;
  float in_stack_ffffff34;
  float in_stack_ffffff38;
  float in_stack_ffffff3c;
  float in_stack_ffffff40;
  float in_stack_ffffff44;
  float in_stack_ffffff48;
  float in_stack_ffffff4c;
  float in_stack_ffffff50;
  float in_stack_ffffff54;
  float in_stack_ffffff58;
  float local_94;
  float local_90;
  float local_8c;
  float local_88;
  undefined4 local_84;
  undefined2 local_80;
  undefined2 local_7e;
  undefined2 local_7c;
  undefined2 local_7a;
  undefined2 local_76;
  float local_74;
  float local_70;
  float local_6c;
  float local_64;
  float local_60;
  float local_5c;
  undefined4 local_54;
  undefined2 local_50;
  undefined2 local_4c;
  undefined2 local_48;
  float local_44;
  float local_40;
  float local_3c;
  float local_30;
  float local_2c;
  float local_24;
  float local_20;
  float local_1c;
  undefined4 local_8;
  undefined4 local_4;

  puVar7 = &DAT_0089d640;
  puVar9 = (undefined4 *)&stack0xffffff2c;
  for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar9 = puVar9 + 1;
  }
  local_94 = 0.0;
  local_90 = 0.0;
  local_8c = 0.0;
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,0.0,0.0,0.0,local_88,in_stack_ffffff2c,in_stack_ffffff30,
             in_stack_ffffff34,in_stack_ffffff38,in_stack_ffffff3c,in_stack_ffffff40,
             in_stack_ffffff44,in_stack_ffffff48,in_stack_ffffff4c,in_stack_ffffff50,
             in_stack_ffffff54,in_stack_ffffff58);
  local_64 = in_stack_00000014 - in_stack_00000004;
  local_84 = 0;
  local_8c = 0.0;
  local_60 = in_stack_00000018 - in_stack_00000008;
  local_5c = in_stack_0000001c - in_stack_0000000c;
  local_94 = local_60 * _DAT_005d8be0 - 0.0;
  local_90 = 0.0 - local_64 * _DAT_005d8be0;
  fVar1 = SQRT(local_90 * local_90 + local_94 * local_94 + 0.0);
  if (fVar1 != _DAT_005d856c) {
    fVar1 = _DAT_005d8568 / fVar1;
    local_94 = local_94 * fVar1;
    local_90 = local_90 * fVar1;
    local_8c = fVar1 * 0.0;
  }
  local_94 = local_94 * _DAT_005d85ec;
  local_90 = local_90 * _DAT_005d85ec;
  local_8c = local_8c * _DAT_005d85ec;
  iVar5 = CVBufTexture__GetOrCreate();
  CVBufTexture__SetVBFormat();
  CVBufTexture__SetIBFormat();
  local_74 = in_stack_00000004;
  local_70 = in_stack_00000008;
  uVar8 = 0;
  puVar7 = &local_54;
  local_6c = in_stack_0000000c - _DAT_005d85ec;
  do {
    if ((uVar8 & 2) == 0) {
      local_44 = -local_94;
      local_40 = -local_90;
      local_3c = -local_8c;
      pfVar6 = &local_44;
    }
    else {
      pfVar6 = &local_94;
    }
    pfVar2 = (float *)&DAT_0089d670;
    if ((uVar8 & 1) == 0) {
      pfVar2 = &local_64;
    }
    local_8 = 0x3f800000;
    local_30 = pfVar6[1] + pfVar2[1];
    local_2c = pfVar6[2] + pfVar2[2];
    local_24 = *pfVar6 + *pfVar2 + local_74;
    local_20 = pfVar6[1] + pfVar2[1] + local_70;
    local_1c = local_2c + local_6c;
    if ((uVar8 & 2) == 0) {
      local_8 = 0;
    }
    local_4 = 0;
    if ((uVar8 & 1) == 0) {
      local_4 = 0x3f800000;
    }
    uVar3 = CVBufTexture__AddVertices();
    *puVar7 = uVar3;
    uVar8 = uVar8 + 1;
    puVar7 = puVar7 + 1;
  } while ((int)uVar8 < 4);
  local_7c = local_4c;
  local_80 = (undefined2)local_54;
  local_7e = local_50;
  local_76 = local_48;
  local_7a = local_80;
  CVBufTexture__AddIndices();
  iVar4 = CVBufTexture__Render();
  if (iVar5 != 0) {
    CDXEngine__Helper_00501310(iVar5);
    iVar4 = extraout_EAX;
  }
  return iVar4;
}

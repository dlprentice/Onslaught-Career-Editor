/* address: 0x00424ca0 */
/* name: CUnitAI__Unk_00424ca0 */
/* signature: void __fastcall CUnitAI__Unk_00424ca0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00424ca0(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 *extraout_EAX;
  int iVar6;
  void *unaff_EDI;
  undefined4 *puVar7;
  undefined4 *this;
  float10 fVar8;
  float10 fVar9;
  float local_a0;
  float fStack_9c;
  float fStack_98;
  undefined4 uStack_94;
  float local_90;
  float local_8c;
  float local_88;
  float local_84;
  undefined4 uStack_80;
  float fStack_7c;
  float fStack_78;
  float fStack_74;
  float local_6c;
  void *local_68;
  float local_64;
  undefined1 auStack_60 [16];
  undefined4 local_50;
  float local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  float local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 auStack_30 [48];

  iVar4 = *(int *)(param_1 + 0x110);
  if ((iVar4 != 0) && ((*(byte *)(iVar4 + 0x2c) & 4) == 0)) {
    fVar8 = (float10)fcos((float10)*(float *)(param_1 + 0xa0));
    this = (undefined4 *)(param_1 + 0x2c);
    puVar5 = (undefined4 *)(param_1 + 0xb0);
    puVar7 = this;
    for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
      *puVar7 = *puVar5;
      puVar5 = puVar5 + 1;
      puVar7 = puVar7 + 1;
    }
    local_64 = (float)(fVar8 * (float10)*(float *)(param_1 + 0x9c) -
                      (float10)*(float *)(iVar4 + 0x278));
    local_68 = (void *)-*(float *)(iVar4 + 0x278);
    local_90 = *(float *)(iVar4 + 0x280) * _DAT_005d95c0;
    iVar4 = CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120(iVar4);
    if (iVar4 != 0) {
      fVar8 = (float10)*(float *)(*(int *)(*(int *)(param_1 + 0x110) + 0x578) + 0x24);
      fVar9 = (float10)fcos(fVar8);
      local_64 = (float)(fVar9 * (float10)_DAT_005d8cb8 + (float10)local_64);
      fVar8 = (float10)fcos(fVar8 + fVar8);
      fVar8 = fVar8 * (float10)_DAT_005d8cb8;
      if (fVar8 < (float10)_DAT_005d87b0) {
        fVar8 = (float10)_DAT_005d856c;
      }
      local_90 = (float)(fVar8 + (float10)local_90);
      local_68 = (void *)((float)fVar9 * _DAT_005d87c0 + (float)local_68);
    }
    fVar8 = (float10)*(float *)(*(int *)(param_1 + 0x110) + 0x114);
    fVar9 = (float10)fcos(fVar8);
    local_6c = (float)fVar9;
    local_8c = (float)fVar9;
    fVar8 = (float10)fsin(fVar8);
    local_88 = (float)-fVar8;
    puVar5 = (undefined4 *)Vec3__SetXYZ();
    local_50 = *puVar5;
    local_4c = (float)puVar5[1];
    local_48 = puVar5[2];
    local_44 = puVar5[3];
    puVar5 = (undefined4 *)Vec3__SetXYZ();
    local_40 = *puVar5;
    local_84 = (float)puVar5[1];
    local_8c = local_88;
    local_38 = puVar5[2];
    local_34 = puVar5[3];
    local_88 = local_4c;
    local_3c = local_84;
    iVar4 = (**(code **)(**(int **)(param_1 + 0x110) + 0x10c))();
    if ((iVar4 == 0) || (iVar4 = HeightDelta__Below015_D4(*(int *)(param_1 + 0x110)), iVar4 != 0)) {
      fStack_7c = 0.0;
      fStack_78 = 0.0;
      fStack_74 = -1.0;
    }
    else {
      CMonitor__Helper_0047ec60(0x6fadc8,&local_a0,(void *)(*(int *)(param_1 + 0x110) + 0x1c));
      fStack_7c = local_a0;
      fStack_78 = fStack_9c;
      fStack_74 = fStack_98;
    }
    local_a0 = fStack_74 * local_88 - fStack_78 * local_84;
    fStack_9c = local_84 * fStack_7c - fStack_74 * local_8c;
    fStack_98 = fStack_78 * local_8c - local_88 * fStack_7c;
    fVar1 = fStack_9c * fStack_74 - fStack_98 * fStack_78;
    fVar2 = fStack_98 * fStack_7c - fStack_74 * local_a0;
    fVar3 = fStack_78 * local_a0 - fStack_9c * fStack_7c;
    fVar1 = SQRT(fVar2 * fVar2 + fVar3 * fVar3 + fVar1 * fVar1);
    if (fVar1 != _DAT_005d856c) {
      fVar3 = (_DAT_005d8568 / fVar1) * fVar3;
    }
    fVar3 = fVar3 * _DAT_005d95bc;
    uStack_80 = uStack_94;
    fVar1 = SQRT(local_a0 * local_a0 + fStack_9c * fStack_9c + fStack_98 * fStack_98);
    fVar2 = fStack_98;
    if (fVar1 != _DAT_005d856c) {
      fVar2 = (_DAT_005d8568 / fVar1) * fStack_98;
    }
    fVar2 = fVar2 * _DAT_005d8bc4;
    if (fVar3 - _DAT_005d8574 <= *(float *)(param_1 + 0xa4)) {
      if (*(float *)(param_1 + 0xa4) <= fVar3 + _DAT_005d8574) {
        *(float *)(param_1 + 0xa4) = fVar3;
      }
      else {
        *(float *)(param_1 + 0xa4) = *(float *)(param_1 + 0xa4) - _DAT_005d8574;
      }
    }
    else {
      *(float *)(param_1 + 0xa4) = *(float *)(param_1 + 0xa4) + _DAT_005d8574;
    }
    if (fVar2 - _DAT_005d8574 <= *(float *)(param_1 + 0xa8)) {
      if (fVar2 + _DAT_005d8574 < *(float *)(param_1 + 0xa8)) {
        fVar2 = *(float *)(param_1 + 0xa8) - _DAT_005d8574;
      }
    }
    else {
      fVar2 = *(float *)(param_1 + 0xa8) + _DAT_005d8574;
    }
    *(float *)(param_1 + 0xa8) = fVar2;
    local_6c = local_64 + *(float *)(param_1 + 0xa8);
    local_90 = local_90 + *(float *)(param_1 + 0xa4);
    local_8c = local_a0;
    local_88 = fStack_9c;
    local_84 = fStack_98;
    vector_constructor_iterator_nothrow(auStack_60,0x10,3,&LAB_00402d20);
    CSquadNormal__Helper_004062d0(auStack_60,local_68,local_90,local_6c,(float)unaff_EDI);
    CMCBuggy__Helper_0040d320(this,auStack_30,auStack_60,unaff_EDI);
    puVar5 = extraout_EAX;
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *this = *puVar5;
      puVar5 = puVar5 + 1;
      this = this + 1;
    }
  }
  return;
}

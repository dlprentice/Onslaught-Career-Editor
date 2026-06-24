/* address: 0x00413760 */
/* name: CMonitor__Unk_00413760 */
/* signature: void __fastcall CMonitor__Unk_00413760(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Unk_00413760(void *param_1)

{
  int *piVar1;
  byte *pbVar2;
  float fVar3;
  undefined4 *puVar4;
  float fVar5;
  int iVar6;
  void *this;
  float *pfVar7;
  int unaff_ESI;
  double dVar8;
  float *in_stack_ffffffbc;
  float fStack_38;
  float fStack_34;
  undefined4 local_30;
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined1 auStack_18 [24];

  *(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0x630) = 2;
  iVar6 = CGeneralVolume__Unk_00414030(param_1);
  if (iVar6 == 0) {
    *(undefined4 *)((int)param_1 + 0x10) = 0;
  }
  iVar6 = *(int *)(*(int *)((int)param_1 + 0x20) + 0x574);
  if (iVar6 != 0) {
    piVar1 = (int *)(iVar6 + 0x44);
    *piVar1 = *piVar1 + 1;
  }
  puVar4 = *(undefined4 **)param_1;
  *(undefined4 **)((int)param_1 + 8) = puVar4;
  if (puVar4 == (undefined4 *)0x0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)*puVar4;
  }
  while (this != (void *)0x0) {
    in_stack_ffffffbc = (float *)0x4137ab;
    CMonitor__Unk_005078f0(this,0,unaff_ESI);
    puVar4 = *(undefined4 **)(*(int *)((int)param_1 + 8) + 4);
    *(undefined4 **)((int)param_1 + 8) = puVar4;
    if (puVar4 == (undefined4 *)0x0) {
      this = (void *)0x0;
    }
    else {
      this = (void *)*puVar4;
    }
  }
  iVar6 = *(int *)((int)param_1 + 0x20);
  if (((DAT_00672fd0 - *(float *)(iVar6 + 0xcc) < _DAT_005d8cb4) && (*(int *)(iVar6 + 0x160) == 0))
     && (*(int *)(iVar6 + 0x4ac) == 0)) {
    fVar3 = *(float *)(*(int *)(iVar6 + 0x4b0) + 0x28);
    if (*(int *)((int)param_1 + 0x14) == 0) {
      fVar3 = fVar3 * _DAT_005d85ec;
    }
    *(float *)(iVar6 + 0xfc) = fVar3 + *(float *)(iVar6 + 0xfc);
    iVar6 = *(int *)((int)param_1 + 0x20);
    if (*(float *)(*(int *)(iVar6 + 0x4b0) + 0x20) < *(float *)(iVar6 + 0xfc)) {
      *(undefined4 *)(iVar6 + 0xfc) = *(undefined4 *)(*(int *)(iVar6 + 0x4b0) + 0x20);
    }
  }
  *(undefined4 *)((int)param_1 + 0x14) = 1;
  *(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0x100) =
       *(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0xfc);
  iVar6 = CMonitor__Unk_00413a70((int)param_1);
  if (iVar6 == 0) {
    iVar6 = (**(code **)(**(int **)((int)param_1 + 0x20) + 0x10c))();
    if (((iVar6 != 0) || ((*(byte *)(*(int *)((int)param_1 + 0x20) + 0x2c) & 0x80) != 0)) &&
       (iVar6 = HeightDelta__Below015_D4(*(int *)((int)param_1 + 0x20)), iVar6 == 0)) {
      Vec3__SetXYZ();
      CHeightField__Unk_0047ec60(0x6fadc8,&fStack_38,&fStack_28);
      dVar8 = CGeneralVolume__Unk_0040d1a0(&fStack_38);
      if ((double)_DAT_005d8cdc < dVar8 + (double)_DAT_005d85e4) {
        pbVar2 = (byte *)(*(int *)((int)param_1 + 0x20) + 0x2c);
        *pbVar2 = *pbVar2 | 0x80;
        CCylinder__Unk_00413b90((int)param_1);
        goto LAB_00413924;
      }
    }
    pbVar2 = (byte *)(*(int *)((int)param_1 + 0x20) + 0x2c);
    *pbVar2 = *pbVar2 & 0x7f;
  }
  else {
    iVar6 = (**(code **)(**(int **)((int)param_1 + 0x20) + 0x6c))();
    uStack_1c = *(undefined4 *)(iVar6 + 8);
    fStack_24 = 0.0;
    uStack_20 = 0;
    in_stack_ffffffbc = &fStack_24;
    (**(code **)(**(int **)((int)param_1 + 0x20) + 0x70))(in_stack_ffffffbc);
  }
LAB_00413924:
  iVar6 = CMonitor__Unk_00413a70((int)param_1);
  if ((iVar6 == 0) &&
     ((iVar6 = (**(code **)(**(int **)((int)param_1 + 0x20) + 0x10c))(), iVar6 != 0 ||
      (*(int *)((int)param_1 + 0x44) != 0)))) {
    pfVar7 = (float *)(**(code **)(**(int **)((int)param_1 + 0x20) + 0x6c))(auStack_18);
    fStack_24 = (float)in_stack_ffffffbc * pfVar7[2];
    fStack_28 = (float)in_stack_ffffffbc * pfVar7[1];
    fStack_2c = (float)in_stack_ffffffbc * *pfVar7;
    (**(code **)(**(int **)((int)param_1 + 0x20) + 0x70))(&fStack_2c);
    (**(code **)(**(int **)((int)param_1 + 0x20) + 0x6c))(&stack0xffffffc0);
    local_30 = 0;
    fVar5 = SQRT(fStack_38 * fStack_38 + fStack_34 * fStack_34);
    fVar3 = *(float *)((*(int **)((int)param_1 + 0x20))[300] + 0x34);
    if ((fVar3 < fVar5) && (*(int *)((int)param_1 + 0x44) < DAT_006236bc)) {
      fVar3 = fVar3 / fVar5;
      local_30 = 0;
      uStack_20 = 0;
      fStack_38 = fVar3 * fStack_38;
      fStack_34 = fVar3 * fStack_34;
      fStack_28 = fStack_38;
      fStack_24 = fStack_34;
      iVar6 = (**(code **)(**(int **)((int)param_1 + 0x20) + 0x6c))(auStack_18);
      fStack_24 = *(float *)(iVar6 + 8);
      (**(code **)(**(int **)((int)param_1 + 0x20) + 0x70))(&fStack_2c);
    }
  }
  if (0 < *(int *)((int)param_1 + 0x44)) {
    *(int *)((int)param_1 + 0x44) = *(int *)((int)param_1 + 0x44) + -1;
  }
  iVar6 = CUnitAI__Unk_00408120(*(int *)((int)param_1 + 0x20));
  if (iVar6 != 0) {
    ABS__Wrapper_00412ad0((int)param_1);
  }
  return;
}

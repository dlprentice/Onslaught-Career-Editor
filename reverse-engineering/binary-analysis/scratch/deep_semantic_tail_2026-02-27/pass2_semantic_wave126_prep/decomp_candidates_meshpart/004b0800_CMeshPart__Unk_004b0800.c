/* address: 0x004b0800 */
/* name: CMeshPart__Unk_004b0800 */
/* signature: void __thiscall CMeshPart__Unk_004b0800(void * this, void * param_1, float param_2, float param_3, float param_4) */


void __thiscall
CMeshPart__Unk_004b0800(void *this,void *param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  float fVar2;
  void *this_00;
  void *extraout_EAX;
  void *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  undefined4 *puVar3;
  float *pfVar4;
  void *extraout_EAX_02;
  void *extraout_EAX_03;
  void *extraout_EAX_04;
  undefined4 *extraout_EAX_05;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  void *unaff_EDI;
  undefined4 *puVar9;
  int in_stack_00000044;
  undefined4 auStack_14c [9];
  undefined4 uStack_128;
  int local_108;
  float local_104;
  float local_100;
  float local_fc;
  float local_f8;
  int local_f4;
  float local_f0;
  float local_ec;
  float local_e8;
  float local_e0;
  float local_dc;
  float local_d8;
  float local_d0;
  float local_cc;
  float local_c8;
  undefined1 local_c0 [16];
  undefined1 local_b0 [16];
  undefined1 local_a0 [16];
  undefined1 local_90 [16];
  undefined1 local_80 [16];
  undefined1 local_70 [48];
  undefined1 local_40 [16];
  undefined1 local_30 [48];

  iVar6 = 0;
  if (0 < *(int *)((int)this + 0x90)) {
    do {
      this_00 = *(void **)(*(int *)((int)this + 0x94) + iVar6 * 4);
      if (this_00 != (void *)0x0) {
        puVar8 = this;
        puVar9 = auStack_14c;
        for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
          *puVar9 = *puVar8;
          puVar8 = puVar8 + 1;
          puVar9 = puVar9 + 1;
        }
        CMeshPart__Unk_004b0800
                  (this_00,*(void **)((int)this + 0x60),*(float *)((int)this + 100),
                   *(float *)((int)this + 0x68),*(float *)((int)this + 0x6c));
      }
      iVar6 = iVar6 + 1;
    } while (iVar6 < *(int *)((int)this + 0x90));
  }
  *(float *)((int)this + 0x60) = *(float *)((int)this + 0x60) - (float)param_1;
  *(float *)((int)this + 100) = *(float *)((int)this + 100) - param_2;
  *(float *)((int)this + 0x68) = *(float *)((int)this + 0x68) - param_3;
  uStack_128 = 0x4b08ac;
  Vec3__SetXYZ();
  CMeshPart__Unk_004b0c00(&stack0x00000014,(int)local_c0,&local_104);
  uStack_128 = 0x4b08d4;
  CMeshPart__Helper_004aa3f0(&stack0x00000014,local_b0,extraout_EAX);
  uStack_128 = 0x4b08de;
  Mat34__SetRows();
  local_104 = local_f0 * *(float *)((int)this + 0x60) +
              local_e8 * *(float *)((int)this + 0x68) + local_ec * *(float *)((int)this + 100);
  local_100 = local_e0 * *(float *)((int)this + 0x60) +
              local_d8 * *(float *)((int)this + 0x68) + local_dc * *(float *)((int)this + 100);
  fVar1 = *(float *)((int)this + 100);
  fVar2 = *(float *)((int)this + 0x60);
  *(float *)((int)this + 0x60) = local_104;
  *(float *)((int)this + 100) = local_100;
  local_fc = local_d0 * fVar2 + local_c8 * *(float *)((int)this + 0x68) + local_cc * fVar1;
  *(float *)((int)this + 0x68) = local_fc;
  *(float *)((int)this + 0x6c) = local_f8;
  uStack_128 = 0x4b0972;
  Vec3__SetXYZ();
  CMeshPart__Unk_004b0c00(&stack0x00000014,(int)local_b0,&local_104);
  uStack_128 = 0x4b099a;
  CMeshPart__Helper_004aa3f0(&stack0x00000014,local_c0,extraout_EAX_00);
  uStack_128 = 0x4b09a4;
  Mat34__SetRows();
  CMCBuggy__Helper_0040d320(this,local_70,&local_f0,unaff_EDI);
  iVar6 = *(int *)((int)this + 0xbc);
  iVar7 = 0;
  puVar8 = extraout_EAX_01;
  puVar9 = this;
  for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar8;
    puVar8 = puVar8 + 1;
    puVar9 = puVar9 + 1;
  }
  local_f4 = 0;
  if (0 < iVar6) {
    local_108 = 0;
    do {
      if ((in_stack_00000044 != 0) && (*(int *)(in_stack_00000044 + 0xbc) == local_f4)) {
        puVar3 = (undefined4 *)(*(int *)(in_stack_00000044 + 200) + iVar7);
        puVar8 = (undefined4 *)(*(int *)(in_stack_00000044 + 0x10c) + local_108);
        puVar9 = (undefined4 *)&stack0x00000014;
        for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
          *puVar9 = *puVar8;
          puVar8 = puVar8 + 1;
          puVar9 = puVar9 + 1;
        }
        param_1 = (void *)*puVar3;
        param_2 = (float)puVar3[1];
        param_3 = (float)puVar3[2];
      }
      pfVar4 = (float *)(iVar7 + *(int *)((int)this + 200));
      *pfVar4 = *pfVar4 - (float)param_1;
      pfVar4[1] = pfVar4[1] - param_2;
      pfVar4[2] = pfVar4[2] - param_3;
      uStack_128 = 0x4b0a8d;
      Vec3__SetXYZ();
      CMeshPart__Unk_004b0c00(&stack0x00000014,(int)local_b0,local_c0);
      uStack_128 = 0x4b0ab5;
      CMeshPart__Helper_004aa3f0(&stack0x00000014,local_a0,extraout_EAX_02);
      uStack_128 = 0x4b0abf;
      Mat34__SetRows();
      uStack_128 = 0x4b0b28;
      Vec3__SetXYZ();
      pfVar4 = (float *)(iVar7 + *(int *)((int)this + 200));
      *pfVar4 = local_104;
      pfVar4[1] = local_100;
      pfVar4[2] = local_fc;
      pfVar4[3] = local_f8;
      CMeshPart__Unk_004b0c20(&stack0x00000014,(int)local_90,unaff_EDI);
      CMeshPart__Unk_004b0c00(&stack0x00000014,(int)local_80,extraout_EAX_03);
      uStack_128 = 0x4b0b8b;
      CMeshPart__Helper_004aa3f0(&stack0x00000014,local_40,extraout_EAX_04);
      uStack_128 = 0x4b0b98;
      Mat34__SetRows();
      CMCBuggy__Helper_0040d320
                (local_70,local_30,(void *)(*(int *)((int)this + 0x10c) + local_108),unaff_EDI);
      puVar8 = extraout_EAX_05;
      puVar9 = (undefined4 *)(*(int *)((int)this + 0x10c) + local_108);
      for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
        *puVar9 = *puVar8;
        puVar8 = puVar8 + 1;
        puVar9 = puVar9 + 1;
      }
      local_f4 = local_f4 + 1;
      iVar7 = iVar7 + 0x10;
      local_108 = local_108 + 0x30;
    } while (local_f4 < *(int *)((int)this + 0xbc));
  }
  return;
}

/* address: 0x0049dcd0 */
/* name: CMCTentacle__UpdateSpline */
/* signature: undefined CMCTentacle__UpdateSpline(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMCTentacle__UpdateSpline(int param_1,undefined4 param_2)

{
  void *pvVar1;
  void *pvVar2;
  undefined4 *extraout_EAX;
  void *extraout_EAX_00;
  void *extraout_EAX_01;
  void *extraout_EAX_02;
  void *extraout_EAX_03;
  float *pfVar3;
  undefined4 *puVar4;
  undefined4 *extraout_EAX_04;
  undefined4 *extraout_EAX_05;
  int iVar5;
  int iVar6;
  void *pvVar7;
  uint uVar8;
  void *unaff_EDI;
  undefined4 *puVar9;
  int iVar10;
  float10 fVar11;
  double dVar12;
  void *pvVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  void *local_1a0;
  void *local_19c;
  void *local_198;
  void *local_194;
  float local_190;
  float local_18c;
  float local_188;
  float local_184;
  void *local_180;
  void *local_17c;
  void *local_178;
  void *local_174;
  float local_170;
  void **local_16c;
  void *local_168;
  int local_164;
  int local_160;
  int local_15c;
  int local_158;
  undefined4 local_154 [12];
  undefined4 local_124 [12];
  void *local_f4;
  undefined4 local_f0 [12];
  undefined1 local_c0 [16];
  undefined1 local_b0 [16];
  undefined1 local_a0 [16];
  undefined4 local_90 [12];
  undefined1 local_60 [16];
  undefined1 local_50 [16];
  undefined1 local_40 [16];
  undefined4 local_30 [12];

  if (*(int *)(param_1 + 0x2c) == 0) {
    CMCTentacle__Init(param_2);
  }
  vector_constructor_iterator_nothrow(local_154,0x10,3,&LAB_00402d20);
  CMCMech__Helper_004b0fb0();
  local_17c = local_19c;
  iVar6 = *(int *)(param_1 + 8);
  local_180 = local_1a0;
  local_178 = local_198;
  local_174 = local_194;
  puVar4 = local_154;
  puVar9 = local_90;
  for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar9 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar9 = puVar9 + 1;
  }
  if (iVar6 == 0) {
    pvVar7 = (void *)0x0;
  }
  else {
    pvVar7 = (void *)(iVar6 + -8);
  }
  CMCTentacle__Helper_004f0ba0(pvVar7,param_1 + 0x40,unaff_EDI);
  CMCTentacle__Helper_004f0c50(pvVar7,param_1 + 0x50,unaff_EDI);
  CMCMech__Helper_004b0fb0();
  local_190 = (float)local_1a0 - (float)local_180;
  local_18c = (float)local_19c - (float)local_17c;
  local_188 = (float)local_198 - (float)local_178;
  CUnitAI__Unk_0049bc80(local_90,local_124,unaff_EDI);
  CUnitAI__Unk_0049bc10((int)local_124);
  dVar12 = CUnitAI__Unk_0049bc40(local_90);
  CUnitAI__Unk_0049bbb0(local_124,(void *)(float)dVar12,(float)unaff_EDI);
  Vec3__SetXYZ();
  CUnitAI__Unk_0049bc80(local_90,local_124,unaff_EDI);
  CUnitAI__Unk_0049bc10((int)local_124);
  dVar12 = CUnitAI__Unk_0049bc40(local_90);
  CUnitAI__Unk_0049bbb0(local_124,(void *)(float)dVar12,(float)unaff_EDI);
  puVar4 = local_124;
  puVar9 = local_f0;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar9 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar9 = puVar9 + 1;
  }
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Mat34__SetRows();
  puVar4 = local_30;
  puVar9 = local_154;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar9 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar9 = puVar9 + 1;
  }
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  pvVar2 = local_174;
  pvVar1 = local_178;
  pvVar13 = local_17c;
  pvVar7 = local_180;
  CMCBuggy__Helper_0040d320(local_154,local_30,(void *)(param_1 + 0x50),unaff_EDI);
  puVar4 = extraout_EAX;
  puVar9 = local_154;
  for (iVar6 = 0xc; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar9 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar9 = puVar9 + 1;
  }
  *(void **)(param_1 + 0x90) = pvVar7;
  *(void **)(param_1 + 0x94) = pvVar13;
  *(void **)(param_1 + 0x98) = pvVar1;
  *(void **)(param_1 + 0x9c) = pvVar2;
  iVar6 = *(int *)(param_1 + 0xe8);
  local_164 = 0;
  if (0 < iVar6) {
    local_160 = 0;
    local_158 = 0;
    do {
      local_16c = &local_180;
      local_180 = (void *)((float)local_164 / (float)(iVar6 + -1));
      local_190 = 0.0;
      local_18c = 0.0;
      local_188 = 0.0;
      local_17c = (void *)0x0;
      local_178 = (void *)0x0;
      local_15c = 0;
      uVar8 = 3;
      local_174 = (void *)(_DAT_005d8568 - (float)local_180);
      local_168 = local_180;
      local_f4 = local_174;
      do {
        iVar5 = 1;
        iVar6 = 2;
        do {
          iVar5 = iVar5 * iVar6;
          iVar6 = iVar6 + 1;
        } while (iVar6 < 4);
        iVar10 = 1;
        iVar6 = 2;
        if ((int)uVar8 < 2) {
          do {
            iVar10 = iVar10 * iVar6;
            iVar6 = iVar6 + 1;
          } while (iVar6 <= local_15c);
        }
        iVar6 = CMCTentacle__Factorial(uVar8);
        local_170 = (float)(iVar5 / (iVar6 * iVar10));
        fVar11 = (float10)CMCTentacle__Power(local_f4,uVar8);
        iVar6 = local_15c;
        local_170 = (float)(fVar11 * (float10)local_170);
        fVar11 = (float10)CMCTentacle__Power(local_168,local_15c);
        local_15c = iVar6 + 1;
        uVar8 = uVar8 - 1;
        *local_16c = (void *)(float)(fVar11 * (float10)local_170);
        local_16c = local_16c + 1;
      } while (uVar8 < 0x80000000);
      CExplosionInitThing__Helper_0040d150
                ((void *)(param_1 + 0x40),local_c0,local_174,(float)unaff_EDI);
      CMCTentacle__Helper_0041ad10(&local_190,extraout_EAX_00,unaff_EDI);
      CExplosionInitThing__Helper_0040d150
                ((void *)(param_1 + 0x90),local_60,local_178,(float)unaff_EDI);
      CMCTentacle__Helper_0041ad10(&local_190,extraout_EAX_01,unaff_EDI);
      CExplosionInitThing__Helper_0040d150
                ((void *)(param_1 + 0x80),local_40,local_17c,(float)unaff_EDI);
      CMCTentacle__Helper_0041ad10(&local_190,extraout_EAX_02,unaff_EDI);
      CExplosionInitThing__Helper_0040d150
                ((void *)(param_1 + 0x30),local_50,local_180,(float)unaff_EDI);
      CMCTentacle__Helper_0041ad10(&local_190,extraout_EAX_03,unaff_EDI);
      iVar5 = local_158;
      pfVar3 = (float *)(local_158 + *(int *)(param_1 + 0xdc));
      *pfVar3 = local_190;
      pfVar3[1] = local_18c;
      pfVar3[2] = local_188;
      pfVar3[3] = local_184;
      if (local_158 != 0) {
        pvVar7 = (void *)(local_158 + *(int *)(param_1 + 0xdc));
        puVar4 = (undefined4 *)Vec3__SetXYZ();
        pvVar13 = (void *)*puVar4;
        uVar14 = puVar4[1];
        uVar15 = puVar4[2];
        uVar16 = puVar4[3];
        CMeshCollisionVolume__Helper_0040d120((void *)((int)pvVar7 + -0x10),local_a0,pvVar7,pvVar13)
        ;
        CMCTentacle__BuildOrientationMatrix
                  (*extraout_EAX_04,extraout_EAX_04[1],extraout_EAX_04[2],extraout_EAX_04[3],pvVar13
                   ,uVar14,uVar15,uVar16);
      }
      iVar6 = *(int *)(param_1 + 0xe8);
      local_158 = iVar5 + 0x10;
      local_164 = local_164 + 1;
      local_160 = local_160 + 0x30;
    } while (local_164 < iVar6);
  }
  puVar4 = (undefined4 *)Vec3__SetXYZ();
  pvVar7 = (void *)*puVar4;
  uVar14 = puVar4[1];
  uVar15 = puVar4[2];
  uVar16 = puVar4[3];
  CMeshCollisionVolume__Helper_0040d120
            ((void *)(param_1 + 0x90),local_b0,(void *)(param_1 + 0x40),pvVar7);
  CMCTentacle__BuildOrientationMatrix
            (*extraout_EAX_05,extraout_EAX_05[1],extraout_EAX_05[2],extraout_EAX_05[3],pvVar7,uVar14
             ,uVar15,uVar16);
  return;
}

/* address: 0x004bcd60 */
/* name: CWorld__Helper_004bcd60 */
/* signature: void CWorld__Helper_004bcd60(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorld__Helper_004bcd60(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int *piVar4;
  float fVar5;
  uint uVar6;
  float fVar7;
  void *pvVar8;
  undefined1 *puVar9;
  int *this;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  void *unaff_EDI;
  uint uVar14;
  float10 fVar15;
  float10 extraout_ST0;
  float10 extraout_ST1;
  double dVar16;
  uint uStack_250;
  ulonglong uStack_248;
  uint uStack_240;
  int iStack_220;
  float fStack_208;
  float fStack_204;
  undefined4 uStack_1f8;
  undefined4 uStack_1f4;
  undefined4 uStack_1f0;
  undefined4 uStack_1ec;
  undefined4 uStack_1e8;
  undefined4 uStack_1e4;
  undefined4 uStack_1e0;
  undefined4 uStack_1dc;
  undefined4 uStack_1d8;
  undefined4 uStack_1d4;
  undefined4 uStack_1d0;
  undefined4 uStack_1cc;
  undefined4 uStack_1c8;
  undefined4 uStack_1c4;
  undefined4 uStack_1c0;
  undefined4 uStack_1bc;
  undefined4 uStack_1b8;
  undefined4 uStack_1b4;
  undefined4 uStack_1b0;
  undefined4 uStack_1ac;
  int iStack_1a8;
  int iStack_1a4;
  int iStack_1a0;
  int iStack_19c;
  undefined4 uStack_198;
  undefined4 uStack_194;
  undefined4 uStack_190;
  undefined4 uStack_18c;
  undefined4 uStack_188;
  float fStack_184;
  float fStack_180;
  float fStack_17c;
  undefined4 uStack_174;
  undefined4 uStack_170;
  undefined4 uStack_16c;
  undefined4 uStack_168;
  undefined4 uStack_164;
  float fStack_160;
  float fStack_15c;
  float fStack_158;
  undefined4 uStack_150;
  undefined **appuStack_14c [5];
  undefined4 uStack_138;
  undefined4 uStack_134;
  undefined4 uStack_130;
  undefined4 uStack_12c;
  undefined4 uStack_128;
  undefined4 uStack_124;
  undefined4 uStack_120;
  undefined **appuStack_118 [5];
  undefined4 uStack_104;
  undefined4 uStack_100;
  undefined4 uStack_fc;
  undefined1 auStack_f4 [120];
  undefined4 uStack_7c;
  undefined4 uStack_54;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  void *local_14;
  undefined1 *puStack_10;
  undefined4 uStack_c;

  uStack_c = 0xffffffff;
  puStack_10 = &LAB_005d3c86;
  local_14 = ExceptionList;
  iVar12 = 0;
  ExceptionList = &local_14;
  do {
    puVar9 = &DAT_00807580 + iVar12;
    iVar11 = 0x20;
    do {
      *puVar9 = 0xff;
      puVar9 = puVar9 + 0x100;
      iVar11 = iVar11 + -1;
    } while (iVar11 != 0);
    iVar12 = iVar12 + 1;
  } while (iVar12 < 0x100);
  this = CSPtrSet__First(&DAT_00809588);
  while (this != (int *)0x0) {
    fVar15 = (float10)(**(code **)(*this + 0x44))();
    fVar1 = (float)fVar15;
    CUnitAI__GetWorldPositionForTargeting(this,(int)&fStack_208,unaff_EDI);
    dVar16 = CRT__RoundDoubleWithFpuChecks((double)(fStack_204 - fVar1));
    uStack_240 = (uint)(longlong)ROUND(dVar16);
    uVar13 = uStack_240;
    dVar16 = CRT__RoundToIntegerRespectingControlWord((double)(fStack_204 + fVar1));
    uStack_240 = (uint)(longlong)ROUND(dVar16);
    if ((int)uVar13 < (int)uStack_240) {
      do {
        dVar16 = CRT__RoundDoubleWithFpuChecks((double)(fStack_208 - fVar1));
        uStack_240 = (uint)(longlong)ROUND(dVar16);
        uVar14 = uStack_240;
        uStack_248 = (longlong)ROUND(dVar16) & 0xffffffff;
        dVar16 = CRT__RoundToIntegerRespectingControlWord((double)(fStack_208 + fVar1));
        uStack_240 = (uint)(longlong)ROUND(dVar16);
        if ((int)uVar14 < (int)uStack_240) {
          fVar5 = (float)(int)uVar13 + _DAT_005d85ec;
          uStack_1c8 = 0;
          uStack_1c4 = 0;
          uStack_1c0 = 0xc2c80000;
          uStack_1f8 = 0;
          uStack_1f4 = 0;
          uStack_1f0 = 0;
          uStack_1d8 = 0;
          uStack_1d4 = 0;
          uStack_1d0 = 0;
          uStack_1e8 = 0;
          uStack_1e4 = 0;
          uStack_1e0 = 0;
          fVar2 = (float)extraout_ST1;
          uVar6 = uVar14;
          do {
            uStack_250 = uVar6 + 1;
            CGeneralVolume__ctor_like_0040b100(appuStack_14c);
            uStack_138 = uStack_1c8;
            uStack_134 = uStack_1c4;
            uStack_130 = uStack_1c0;
            uStack_12c = uStack_1bc;
            uStack_128 = 0;
            uStack_124 = 0;
            uStack_120 = 0;
            appuStack_14c[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
            uStack_c = 0;
            CGeneralVolume__ctor_like_0040b100(appuStack_118);
            fVar7 = DAT_006fbdf4;
            uStack_104 = 0x3f800000;
            uStack_100 = 0x3f800000;
            appuStack_118[0] = &PTR_VFuncSlot_00_00426340_005d95e8;
            uStack_c = CONCAT31(uStack_c._1_3_,1);
            uStack_198 = 0;
            uStack_174 = 0;
            uStack_150 = 0;
            uStack_248._0_4_ = (uint)(longlong)ROUND((float)(int)(uint)uStack_248 + _DAT_005d85ec);
            fVar3 = (float)extraout_ST0;
            uVar10 = CWorld__Helper_0047ea20(0x6fadc8,(uint)uStack_248,(uint)(longlong)ROUND(fVar5))
            ;
            fStack_17c = (float)(int)(short)uVar10 * fVar7;
            uStack_170 = uStack_1f8;
            uStack_16c = uStack_1f4;
            uStack_168 = uStack_1f0;
            uStack_164 = uStack_1ec;
            uStack_18c = uStack_1d0;
            uStack_194 = uStack_1d8;
            uStack_190 = uStack_1d4;
            uStack_188 = uStack_1cc;
            iStack_1a8 = this[7];
            iStack_1a4 = this[8];
            iStack_1a0 = this[9];
            iStack_19c = this[10];
            uStack_1b8 = uStack_1e8;
            uStack_1b0 = uStack_1e0;
            uStack_1b4 = uStack_1e4;
            uStack_1ac = uStack_1dc;
            piVar4 = *(int **)(this[0xe] + 0x18);
            fStack_184 = fVar3;
            fStack_180 = fVar2;
            fStack_160 = fVar3;
            fStack_15c = fVar2;
            fStack_158 = fStack_17c;
            if (piVar4 == (int *)0x0) {
              CWorld__Helper_004bdf70(&DAT_00807580,uVar6 - 1,uVar13,0,(int)unaff_EDI);
              CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13 + -1,0,(int)unaff_EDI);
              CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13,0,(int)unaff_EDI);
              CWorld__Helper_004bdf70(&DAT_00807580,uStack_250,uVar13,0,(int)unaff_EDI);
              CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13 + 1,0,(int)unaff_EDI);
              CWorld__Helper_004bd440(DAT_00855290,uVar14,uVar13,(int)unaff_EDI);
              CWorld__Helper_004bd440(DAT_00855294,uVar14,uVar13,(int)unaff_EDI);
              CWorld__Helper_004bd440(DAT_00855298,uVar14,uVar13,(int)unaff_EDI);
            }
            else {
              uStack_fc = 0;
              vector_constructor_iterator_nothrow(auStack_f4,0x10,6,&LAB_00402d20);
              uStack_7c = 0;
              uStack_54 = 0;
              uStack_34 = 0;
              uStack_30 = 0;
              uStack_2c = 1;
              iVar12 = (**(code **)(*piVar4 + 0x10))(&uStack_1b8,&uStack_170,appuStack_14c);
              if ((iVar12 != 0) ||
                 (iVar12 = (**(code **)(*piVar4 + 0xc))(&uStack_1b8,&uStack_194,appuStack_118),
                 iVar12 != 0)) {
                CWorld__Helper_004bdf70(&DAT_00807580,uVar6 - 1,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13 + -1,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(&DAT_00807580,uStack_250,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(&DAT_00807580,uVar14,uVar13 + 1,0,(int)unaff_EDI);
                pvVar8 = DAT_00855290;
                CWorld__Helper_004bdf70(DAT_00855290,uVar6 - 1,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + -1,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uStack_250,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + 1,0,(int)unaff_EDI);
                pvVar8 = DAT_00855294;
                CWorld__Helper_004bdf70(DAT_00855294,uVar6 - 1,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + -1,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uStack_250,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + 1,0,(int)unaff_EDI);
                pvVar8 = DAT_00855298;
                CWorld__Helper_004bdf70(DAT_00855298,uVar6 - 1,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + -1,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uStack_250,uVar13,0,(int)unaff_EDI);
                CWorld__Helper_004bdf70(pvVar8,uVar14,uVar13 + 1,0,(int)unaff_EDI);
              }
            }
            uVar14 = uVar14 + 1;
            appuStack_118[0] = &PTR_LAB_005d892c;
            uStack_c = 0xffffffff;
            appuStack_14c[0] = &PTR_LAB_005d892c;
            uStack_248 = (ulonglong)uVar14;
            dVar16 = CRT__RoundToIntegerRespectingControlWord((double)(fStack_208 + fVar1));
            iStack_220 = (int)(longlong)ROUND(dVar16);
            uVar6 = uStack_250;
          } while ((int)uVar14 < iStack_220);
        }
        uVar13 = uVar13 + 1;
        dVar16 = CRT__RoundToIntegerRespectingControlWord((double)(fStack_204 + fVar1));
        iStack_220 = (int)(longlong)ROUND(dVar16);
      } while ((int)uVar13 < iStack_220);
    }
    this = CSPtrSet__Next(&DAT_00809588);
  }
  DAT_00809598 = 1;
  ExceptionList = local_14;
  return;
}

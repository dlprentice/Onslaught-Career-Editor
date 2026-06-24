/* address: 0x005a2b2d */
/* name: CTexture__Helper_005a2b2d */
/* signature: float * __stdcall CTexture__Helper_005a2b2d(void * param_1, void * param_2, void * param_3) */


float * CTexture__Helper_005a2b2d(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  undefined1 auVar14 [16];
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  float fVar39;
  float fVar40;
  float fVar41;
  float fVar42;
  float fVar43;
  float fVar44;
  float fVar45;
  float fVar46;
  float fVar47;
  float fVar48;
  float fVar49;
  float fVar50;
  float fVar51;

  fVar10 = (float)*(undefined8 *)param_3;
  fVar15 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
  fVar18 = (float)*(undefined8 *)((int)param_3 + 0x10);
  fVar20 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x10) >> 0x20);
  fVar6 = (float)*(undefined8 *)((int)param_3 + 0x20);
  fVar7 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x20) >> 0x20);
  fVar8 = (float)*(undefined8 *)((int)param_3 + 0x30);
  fVar9 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x30) >> 0x20);
  fVar11 = (float)*(undefined8 *)((int)param_3 + 8);
  fVar16 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  fVar28 = (float)*(undefined8 *)((int)param_3 + 0x18);
  fVar32 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x18) >> 0x20);
  fVar12 = (float)*(undefined8 *)((int)param_3 + 0x28);
  fVar17 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x28) >> 0x20);
  fVar19 = (float)*(undefined8 *)((int)param_3 + 0x38);
  fVar21 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x38) >> 0x20);
  fVar22 = fVar11 * fVar17;
  fVar25 = fVar28 * fVar21;
  fVar29 = fVar12 * fVar16;
  fVar33 = fVar19 * fVar32;
  fVar36 = fVar7 * fVar11;
  fVar40 = fVar9 * fVar28;
  fVar44 = fVar15 * fVar12;
  fVar48 = fVar20 * fVar19;
  fVar37 = fVar15 * fVar17;
  fVar41 = fVar20 * fVar21;
  fVar45 = fVar7 * fVar16;
  fVar49 = fVar9 * fVar32;
  fVar23 = (fVar12 * fVar41 +
           ((fVar17 * fVar40 + (fVar7 * fVar33 - fVar7 * fVar25)) - fVar17 * fVar48)) -
           fVar12 * fVar49;
  fVar26 = (fVar19 * fVar37 +
           ((fVar21 * fVar36 + (fVar9 * fVar29 - fVar9 * fVar22)) - fVar21 * fVar44)) -
           fVar19 * fVar45;
  fVar30 = (fVar11 * fVar49 +
           ((fVar16 * fVar48 + (fVar15 * fVar25 - fVar15 * fVar33)) - fVar16 * fVar40)) -
           fVar11 * fVar41;
  fVar34 = (fVar28 * fVar45 +
           ((fVar32 * fVar44 + (fVar20 * fVar22 - fVar20 * fVar29)) - fVar32 * fVar36)) -
           fVar28 * fVar37;
  fVar38 = fVar10 * fVar7;
  fVar42 = fVar18 * fVar9;
  fVar46 = fVar6 * fVar15;
  fVar50 = fVar8 * fVar20;
  fVar39 = fVar10 * fVar17;
  fVar43 = fVar18 * fVar21;
  fVar47 = fVar6 * fVar16;
  fVar51 = fVar8 * fVar32;
  fVar1 = fVar10 * fVar23;
  fVar3 = fVar18 * fVar26;
  fVar4 = fVar6 * fVar30;
  fVar5 = fVar8 * fVar34;
  fVar24 = fVar10 * fVar12;
  fVar27 = fVar18 * fVar19;
  fVar31 = fVar6 * fVar11;
  fVar35 = fVar8 * fVar28;
  fVar13 = fVar4 + fVar1;
  fVar2 = fVar5 + fVar3 + fVar13;
  if (fVar2 == 0.0) {
    param_1 = (float *)0x0;
  }
  else {
    if (param_2 != (void *)0x0) {
      *(float *)param_2 = fVar2;
    }
    auVar14._4_4_ = fVar13;
    auVar14._0_4_ = fVar2;
    auVar14._8_4_ = fVar3 + fVar5;
    auVar14._12_4_ = fVar1 + fVar4;
    auVar14 = rcpss(ZEXT816(0),auVar14);
    fVar1 = auVar14._0_4_;
    fVar1 = (fVar1 + fVar1) - fVar2 * fVar1 * fVar1;
    *(float *)param_1 = fVar1 * fVar23;
    *(float *)((int)param_1 + 4) = fVar1 * fVar26;
    *(float *)((int)param_1 + 8) = fVar1 * fVar30;
    *(float *)((int)param_1 + 0xc) = fVar1 * fVar34;
    *(float *)((int)param_1 + 0x10) =
         fVar1 * ((fVar17 * fVar27 +
                  fVar12 * fVar51 + ((fVar6 * fVar25 - fVar6 * fVar33) - fVar12 * fVar43)) -
                 fVar17 * fVar35);
    *(float *)((int)param_1 + 0x14) =
         fVar1 * ((fVar21 * fVar24 +
                  fVar19 * fVar47 + ((fVar8 * fVar22 - fVar8 * fVar29) - fVar19 * fVar39)) -
                 fVar21 * fVar31);
    *(float *)((int)param_1 + 0x18) =
         fVar1 * ((fVar16 * fVar35 +
                  fVar11 * fVar43 + ((fVar10 * fVar33 - fVar10 * fVar25) - fVar11 * fVar51)) -
                 fVar16 * fVar27);
    *(float *)((int)param_1 + 0x1c) =
         fVar1 * ((fVar32 * fVar31 +
                  fVar28 * fVar39 + ((fVar18 * fVar29 - fVar18 * fVar22) - fVar28 * fVar47)) -
                 fVar32 * fVar24);
    *(float *)((int)param_1 + 0x20) =
         fVar1 * ((fVar7 * fVar43 +
                  (fVar17 * fVar50 - (fVar17 * fVar42 + (fVar6 * fVar41 - fVar6 * fVar49)))) -
                 fVar7 * fVar51);
    *(float *)((int)param_1 + 0x24) =
         fVar1 * ((fVar9 * fVar39 +
                  (fVar21 * fVar46 - (fVar21 * fVar38 + (fVar8 * fVar37 - fVar8 * fVar45)))) -
                 fVar9 * fVar47);
    *(float *)((int)param_1 + 0x28) =
         fVar1 * ((fVar15 * fVar51 +
                  (fVar16 * fVar42 - (fVar16 * fVar50 + (fVar10 * fVar49 - fVar10 * fVar41)))) -
                 fVar15 * fVar43);
    *(float *)((int)param_1 + 0x2c) =
         fVar1 * ((fVar20 * fVar47 +
                  (fVar32 * fVar38 - (fVar32 * fVar46 + (fVar18 * fVar45 - fVar18 * fVar37)))) -
                 fVar20 * fVar39);
    *(ulonglong *)((int)param_1 + 0x30) =
         CONCAT44(fVar1 * (fVar9 * fVar31 +
                          (((fVar19 * fVar38 - (fVar8 * fVar36 - fVar8 * fVar44)) - fVar19 * fVar46)
                          - fVar9 * fVar24)),
                  fVar1 * (fVar7 * fVar35 +
                          (((fVar12 * fVar42 - (fVar6 * fVar40 - fVar6 * fVar48)) - fVar12 * fVar50)
                          - fVar7 * fVar27)));
    *(ulonglong *)((int)param_1 + 0x38) =
         CONCAT44(fVar1 * (fVar20 * fVar24 +
                          (((fVar28 * fVar46 - (fVar18 * fVar44 - fVar18 * fVar36)) -
                           fVar28 * fVar38) - fVar20 * fVar31)),
                  fVar1 * (fVar15 * fVar27 +
                          (((fVar11 * fVar50 - (fVar10 * fVar48 - fVar10 * fVar40)) -
                           fVar11 * fVar42) - fVar15 * fVar35)));
  }
  return param_1;
}

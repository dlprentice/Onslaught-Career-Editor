/* address: 0x005a1786 */
/* name: CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786 */
/* signature: void __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786(void * param_1, void * param_2, void * param_3) */


void CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786
               (void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  undefined1 auVar7 [16];
  undefined1 auVar8 [16];
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;

  fVar1 = (float)*(undefined8 *)param_2;
  fVar3 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar9 = *(float *)((int)param_2 + 8);
  if (((uint)param_3 & 0xf) == 0) {
    fVar13 = *(float *)((int)param_3 + 0x20) * fVar9 + *(float *)((int)param_3 + 0x30);
    fVar14 = *(float *)((int)param_3 + 0x24) * fVar9 + *(float *)((int)param_3 + 0x34);
    fVar15 = *(float *)((int)param_3 + 0x28) * fVar9 + *(float *)((int)param_3 + 0x38);
    fVar16 = *(float *)((int)param_3 + 0x2c) * fVar9 + *(float *)((int)param_3 + 0x3c);
    fVar10 = *(float *)((int)param_3 + 0x10);
    fVar11 = *(float *)((int)param_3 + 0x14);
    fVar9 = *(float *)((int)param_3 + 0x18);
    fVar12 = *(float *)((int)param_3 + 0x1c);
    fVar2 = *(float *)param_3;
    fVar4 = *(float *)((int)param_3 + 4);
    fVar5 = *(float *)((int)param_3 + 8);
    fVar6 = *(float *)((int)param_3 + 0xc);
  }
  else {
    fVar13 = (float)*(undefined8 *)((int)param_3 + 0x20) * fVar9 +
             (float)*(undefined8 *)((int)param_3 + 0x30);
    fVar14 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x20) >> 0x20) * fVar9 +
             (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x30) >> 0x20);
    fVar15 = (float)*(undefined8 *)((int)param_3 + 0x28) * fVar9 +
             (float)*(undefined8 *)((int)param_3 + 0x38);
    fVar16 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x28) >> 0x20) * fVar9 +
             (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x38) >> 0x20);
    fVar10 = (float)*(undefined8 *)((int)param_3 + 0x10);
    fVar11 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x10) >> 0x20);
    fVar9 = (float)*(undefined8 *)((int)param_3 + 0x18);
    fVar12 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x18) >> 0x20);
    fVar2 = (float)*(undefined8 *)param_3;
    fVar4 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
    fVar5 = (float)*(undefined8 *)((int)param_3 + 8);
    fVar6 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  }
  auVar7._4_4_ = fVar1;
  auVar7._0_4_ = fVar1;
  auVar7._8_4_ = fVar1;
  auVar7._12_4_ = fVar1;
  fVar13 = fVar2 * fVar1 + fVar10 * fVar3 + fVar13;
  fVar14 = fVar4 * fVar1 + fVar11 * fVar3 + fVar14;
  fVar15 = fVar5 * fVar1 + fVar9 * fVar3 + fVar15;
  fVar16 = fVar6 * fVar1 + fVar12 * fVar3 + fVar16;
  auVar8._4_4_ = fVar14;
  auVar8._0_4_ = fVar13;
  auVar8._8_4_ = fVar15;
  auVar8._12_4_ = fVar16;
  auVar8 = rcpps(auVar7,auVar8);
  fVar9 = auVar8._12_4_;
  fVar9 = (fVar9 + fVar9) - fVar9 * fVar16 * fVar9;
  *(ulonglong *)param_1 = CONCAT44(fVar14 * fVar9,fVar13 * fVar9);
  *(float *)((int)param_1 + 8) = fVar15 * fVar9;
  return;
}

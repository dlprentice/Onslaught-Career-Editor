/* address: 0x005a2ee9 */
/* name: CFastVB__DispatchOp_Determinant4x4_005a2ee9 */
/* signature: double __stdcall CFastVB__DispatchOp_Determinant4x4_005a2ee9(void * param_1) */


double CFastVB__DispatchOp_Determinant4x4_005a2ee9(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined8 uVar6;
  float fVar7;
  float fVar8;
  undefined8 uVar9;
  float fVar10;
  float fVar11;
  undefined8 uVar12;
  float fVar13;
  float fVar14;
  undefined8 uVar15;
  float fVar16;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;

  if (((uint)param_1 & 0xf) == 0) {
    local_30 = *(float *)param_1;
    uStack_2c = *(float *)((int)param_1 + 4);
    uStack_28 = *(float *)((int)param_1 + 8);
    uStack_24 = *(float *)((int)param_1 + 0xc);
    uVar12 = *(undefined8 *)((int)param_1 + 0x10);
    uVar15 = *(undefined8 *)((int)param_1 + 0x18);
    uVar6 = *(undefined8 *)((int)param_1 + 0x30);
    uVar9 = *(undefined8 *)((int)param_1 + 0x38);
    fVar1 = *(float *)((int)param_1 + 0x20);
    fVar2 = *(float *)((int)param_1 + 0x24);
    fVar3 = *(float *)((int)param_1 + 0x28);
    fVar4 = *(float *)((int)param_1 + 0x2c);
  }
  else {
    local_30 = *(float *)param_1;
    uStack_2c = *(float *)((int)param_1 + 4);
    uStack_28 = *(float *)((int)param_1 + 8);
    uStack_24 = (float)((ulonglong)*(undefined8 *)((int)param_1 + 8) >> 0x20);
    uVar12 = *(undefined8 *)((int)param_1 + 0x10);
    uVar15 = *(undefined8 *)((int)param_1 + 0x18);
    fVar1 = (float)*(undefined8 *)((int)param_1 + 0x20);
    fVar2 = (float)((ulonglong)*(undefined8 *)((int)param_1 + 0x20) >> 0x20);
    fVar3 = (float)*(undefined8 *)((int)param_1 + 0x28);
    fVar4 = (float)((ulonglong)*(undefined8 *)((int)param_1 + 0x28) >> 0x20);
    uVar6 = *(undefined8 *)((int)param_1 + 0x30);
    uVar9 = *(undefined8 *)((int)param_1 + 0x38);
  }
  fVar5 = (float)uVar6;
  fVar7 = (float)((ulonglong)uVar6 >> 0x20);
  fVar8 = (float)uVar9;
  fVar10 = (float)((ulonglong)uVar9 >> 0x20);
  fVar11 = (float)uVar12;
  fVar13 = (float)((ulonglong)uVar12 >> 0x20);
  fVar14 = (float)uVar15;
  fVar16 = (float)((ulonglong)uVar15 >> 0x20);
  return (double)(((fVar13 * (fVar3 * fVar10 - fVar4 * fVar8) +
                    fVar14 * (fVar4 * fVar7 - fVar2 * fVar10) +
                   fVar16 * (fVar2 * fVar8 - fVar3 * fVar7)) * local_30 +
                  (fVar16 * (fVar1 * fVar7 - fVar2 * fVar5) +
                   fVar11 * (fVar2 * fVar10 - fVar4 * fVar7) +
                  fVar13 * (fVar4 * fVar5 - fVar1 * fVar10)) * uStack_28) -
                 ((fVar14 * (fVar4 * fVar5 - fVar1 * fVar10) +
                   fVar16 * (fVar1 * fVar8 - fVar3 * fVar5) +
                  fVar11 * (fVar3 * fVar10 - fVar4 * fVar8)) * uStack_2c +
                 (fVar11 * (fVar2 * fVar8 - fVar3 * fVar7) +
                  fVar13 * (fVar3 * fVar5 - fVar1 * fVar8) +
                 fVar14 * (fVar1 * fVar7 - fVar2 * fVar5)) * uStack_24));
}

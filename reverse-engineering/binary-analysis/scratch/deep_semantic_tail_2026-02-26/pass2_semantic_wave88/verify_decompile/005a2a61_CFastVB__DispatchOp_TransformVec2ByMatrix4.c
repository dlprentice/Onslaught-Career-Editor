/* address: 0x005a2a61 */
/* name: CFastVB__DispatchOp_TransformVec2ByMatrix4 */
/* signature: void __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4(void * param_1, void * param_2, void * param_3) */


void CFastVB__DispatchOp_TransformVec2ByMatrix4(void *param_1,void *param_2,void *param_3)

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
  float fVar14;

  fVar1 = *(float *)param_2;
  fVar2 = *(float *)((int)param_2 + 4);
  fVar7 = *(float *)((int)param_2 + 8);
  fVar8 = *(float *)((int)param_2 + 0xc);
  if (((uint)param_3 & 0xf) == 0) {
    fVar11 = *(float *)((int)param_3 + 0x20) * fVar7 + *(float *)((int)param_3 + 0x30) * fVar8;
    fVar12 = *(float *)((int)param_3 + 0x24) * fVar7 + *(float *)((int)param_3 + 0x34) * fVar8;
    fVar13 = *(float *)((int)param_3 + 0x28) * fVar7 + *(float *)((int)param_3 + 0x38) * fVar8;
    fVar14 = *(float *)((int)param_3 + 0x2c) * fVar7 + *(float *)((int)param_3 + 0x3c) * fVar8;
    fVar7 = *(float *)((int)param_3 + 0x10);
    fVar8 = *(float *)((int)param_3 + 0x14);
    fVar9 = *(float *)((int)param_3 + 0x18);
    fVar10 = *(float *)((int)param_3 + 0x1c);
    fVar3 = *(float *)param_3;
    fVar4 = *(float *)((int)param_3 + 4);
    fVar5 = *(float *)((int)param_3 + 8);
    fVar6 = *(float *)((int)param_3 + 0xc);
  }
  else {
    fVar11 = (float)*(undefined8 *)((int)param_3 + 0x20) * fVar7 +
             (float)*(undefined8 *)((int)param_3 + 0x30) * fVar8;
    fVar12 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x20) >> 0x20) * fVar7 +
             (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x30) >> 0x20) * fVar8;
    fVar13 = (float)*(undefined8 *)((int)param_3 + 0x28) * fVar7 +
             (float)*(undefined8 *)((int)param_3 + 0x38) * fVar8;
    fVar14 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x28) >> 0x20) * fVar7 +
             (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x38) >> 0x20) * fVar8;
    fVar7 = (float)*(undefined8 *)((int)param_3 + 0x10);
    fVar8 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x10) >> 0x20);
    fVar9 = (float)*(undefined8 *)((int)param_3 + 0x18);
    fVar10 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x18) >> 0x20);
    fVar3 = (float)*(undefined8 *)param_3;
    fVar4 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
    fVar5 = (float)*(undefined8 *)((int)param_3 + 8);
    fVar6 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  }
  *(float *)param_1 = fVar3 * fVar1 + fVar7 * fVar2 + fVar11;
  *(float *)((int)param_1 + 4) = fVar4 * fVar1 + fVar8 * fVar2 + fVar12;
  *(float *)((int)param_1 + 8) = fVar5 * fVar1 + fVar9 * fVar2 + fVar13;
  *(float *)((int)param_1 + 0xc) = fVar6 * fVar1 + fVar10 * fVar2 + fVar14;
  return;
}

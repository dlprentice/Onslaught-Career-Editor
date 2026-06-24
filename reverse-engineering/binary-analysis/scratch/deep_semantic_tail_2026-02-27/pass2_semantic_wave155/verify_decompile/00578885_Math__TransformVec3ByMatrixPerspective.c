/* address: 0x00578885 */
/* name: Math__TransformVec3ByMatrixPerspective */
/* signature: void __stdcall Math__TransformVec3ByMatrixPerspective(void * param_1, void * param_2, void * param_3) */


void Math__TransformVec3ByMatrixPerspective(void *param_1,void *param_2,void *param_3)

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
  float fVar15;
  int iVar16;

  fVar1 = *(float *)param_2;
  fVar2 = *(float *)((int)param_3 + 8);
  fVar3 = *(float *)param_2;
  fVar4 = *(float *)((int)param_3 + 4);
  fVar5 = *(float *)((int)param_2 + 4);
  fVar6 = *(float *)((int)param_3 + 0x18);
  fVar7 = *(float *)((int)param_2 + 4);
  fVar8 = *(float *)((int)param_3 + 0x14);
  fVar9 = *(float *)((int)param_2 + 8);
  fVar10 = *(float *)((int)param_3 + 0x28);
  fVar11 = *(float *)((int)param_2 + 8);
  fVar12 = *(float *)((int)param_3 + 0x24);
  fVar13 = *(float *)((int)param_3 + 0x34);
  fVar14 = *(float *)((int)param_3 + 0x38);
  fVar15 = *(float *)((int)param_3 + 0x3c) +
           *(float *)((int)param_2 + 8) * *(float *)((int)param_3 + 0x2c) +
           *(float *)((int)param_2 + 4) * *(float *)((int)param_3 + 0x1c) +
           *(float *)param_2 * *(float *)((int)param_3 + 0xc);
  *(float *)param_1 =
       *(float *)((int)param_3 + 0x30) +
       *(float *)((int)param_2 + 8) * *(float *)((int)param_3 + 0x20) +
       *(float *)((int)param_2 + 4) * *(float *)((int)param_3 + 0x10) +
       *(float *)param_2 * *(float *)param_3;
  *(float *)((int)param_1 + 4) = fVar13 + fVar11 * fVar12 + fVar7 * fVar8 + fVar3 * fVar4;
  *(float *)((int)param_1 + 8) = fVar14 + fVar9 * fVar10 + fVar5 * fVar6 + fVar1 * fVar2;
  iVar16 = Math__IsFloatDiffOutsideTolerance(fVar15,1.0);
  if (iVar16 == 0) {
    fVar15 = 1.0 / fVar15;
    *(float *)param_1 = fVar15 * *(float *)param_1;
    *(float *)((int)param_1 + 4) = fVar15 * *(float *)((int)param_1 + 4);
    *(float *)((int)param_1 + 8) = fVar15 * *(float *)((int)param_1 + 8);
  }
  return;
}

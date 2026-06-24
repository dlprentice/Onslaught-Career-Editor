/* address: 0x00578643 */
/* name: Math__TransformVec2ByMatrixPerspective */
/* signature: void __stdcall Math__TransformVec2ByMatrixPerspective(void * param_1, void * param_2, void * param_3) */


void Math__TransformVec2ByMatrixPerspective(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;

  fVar1 = *(float *)param_2;
  fVar2 = *(float *)((int)param_3 + 4);
  fVar3 = *(float *)((int)param_2 + 4);
  fVar4 = *(float *)((int)param_3 + 0x14);
  fVar5 = *(float *)((int)param_3 + 0x34);
  fVar6 = *(float *)((int)param_3 + 0x3c) +
          *(float *)((int)param_2 + 4) * *(float *)((int)param_3 + 0x1c) +
          *(float *)param_2 * *(float *)((int)param_3 + 0xc);
  *(float *)param_1 =
       *(float *)((int)param_3 + 0x30) +
       *(float *)((int)param_2 + 4) * *(float *)((int)param_3 + 0x10) +
       *(float *)param_2 * *(float *)param_3;
  *(float *)((int)param_1 + 4) = fVar5 + fVar3 * fVar4 + fVar1 * fVar2;
  iVar7 = Math__IsFloatDiffOutsideTolerance(fVar6,1.0);
  if (iVar7 == 0) {
    fVar6 = 1.0 / fVar6;
    *(float *)param_1 = fVar6 * *(float *)param_1;
    *(float *)((int)param_1 + 4) = fVar6 * *(float *)((int)param_1 + 4);
  }
  return;
}

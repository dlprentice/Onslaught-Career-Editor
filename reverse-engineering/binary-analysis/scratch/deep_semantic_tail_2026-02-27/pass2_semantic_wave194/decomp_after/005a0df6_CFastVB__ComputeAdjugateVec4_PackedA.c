/* address: 0x005a0df6 */
/* name: CFastVB__ComputeAdjugateVec4_PackedA */
/* signature: void __stdcall CFastVB__ComputeAdjugateVec4_PackedA(void * param_1, void * param_2, void * param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__ComputeAdjugateVec4_PackedA(void *param_1,void *param_2,void *param_3,void *param_4)

{
  float fVar1;
  float fVar2;
  uint uVar3;
  float fVar4;
  uint uVar5;
  float fVar6;
  uint uVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;

  fVar1 = (float)*(undefined8 *)param_3;
  fVar2 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
  fVar4 = (float)*(undefined8 *)((int)param_3 + 8);
  fVar6 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  fVar8 = (float)*(undefined8 *)param_4;
  fVar9 = (float)((ulonglong)*(undefined8 *)param_4 >> 0x20);
  fVar10 = (float)*(undefined8 *)((int)param_4 + 8);
  fVar11 = (float)((ulonglong)*(undefined8 *)((int)param_4 + 8) >> 0x20);
  fVar12 = (float)*(undefined8 *)param_2;
  fVar13 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar14 = (float)*(undefined8 *)((int)param_2 + 8);
  fVar15 = (float)((ulonglong)*(undefined8 *)((int)param_2 + 8) >> 0x20);
  uVar3 = (uint)(fVar14 * (fVar6 * fVar8 - fVar1 * fVar11) +
                 fVar15 * (fVar1 * fVar10 - fVar4 * fVar8) +
                fVar12 * (fVar4 * fVar11 - fVar6 * fVar10)) ^ uRam0065e604;
  uVar5 = (uint)(fVar15 * (fVar1 * fVar9 - fVar2 * fVar8) +
                 fVar12 * (fVar2 * fVar11 - fVar6 * fVar9) +
                fVar13 * (fVar6 * fVar8 - fVar1 * fVar11)) ^ uRam0065e608;
  uVar7 = (uint)(fVar12 * (fVar2 * fVar10 - fVar4 * fVar9) +
                 fVar13 * (fVar4 * fVar8 - fVar1 * fVar10) +
                fVar14 * (fVar1 * fVar9 - fVar2 * fVar8)) ^ uRam0065e60c;
  *(uint *)param_1 =
       (uint)(fVar13 * (fVar4 * fVar11 - fVar6 * fVar10) + fVar14 * (fVar6 * fVar9 - fVar2 * fVar11)
             + fVar15 * (fVar2 * fVar10 - fVar4 * fVar9)) ^ _DAT_0065e600;
  *(uint *)((int)param_1 + 4) = uVar3;
  *(uint *)((int)param_1 + 8) = uVar5;
  *(uint *)((int)param_1 + 0xc) = uVar7;
  return;
}

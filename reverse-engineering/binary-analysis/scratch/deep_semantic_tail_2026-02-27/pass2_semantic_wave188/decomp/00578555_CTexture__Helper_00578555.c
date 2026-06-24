/* address: 0x00578555 */
/* name: CTexture__Helper_00578555 */
/* signature: void __stdcall CTexture__Helper_00578555(void * param_1, void * param_2, void * param_3) */


void CTexture__Helper_00578555(void *param_1,void *param_2,void *param_3)

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

  fVar1 = *(float *)((int)param_3 + 4);
  fVar2 = *(float *)param_2;
  fVar3 = *(float *)((int)param_3 + 0x14);
  fVar4 = *(float *)((int)param_2 + 4);
  fVar5 = *(float *)((int)param_3 + 0x34);
  fVar6 = *(float *)((int)param_3 + 8);
  fVar7 = *(float *)param_2;
  fVar8 = *(float *)((int)param_3 + 0x18);
  fVar9 = *(float *)((int)param_2 + 4);
  fVar10 = *(float *)((int)param_3 + 0x38);
  fVar11 = *(float *)((int)param_3 + 0xc);
  fVar12 = *(float *)param_2;
  fVar13 = *(float *)((int)param_3 + 0x1c);
  fVar14 = *(float *)((int)param_2 + 4);
  fVar15 = *(float *)((int)param_3 + 0x3c);
  *(float *)param_1 =
       *(float *)param_2 * *(float *)param_3 +
       *(float *)((int)param_3 + 0x10) * *(float *)((int)param_2 + 4) +
       *(float *)((int)param_3 + 0x30);
  *(float *)((int)param_1 + 4) = fVar3 * fVar4 + fVar1 * fVar2 + fVar5;
  *(float *)((int)param_1 + 8) = fVar8 * fVar9 + fVar6 * fVar7 + fVar10;
  *(float *)((int)param_1 + 0xc) = fVar13 * fVar14 + fVar11 * fVar12 + fVar15;
  return;
}

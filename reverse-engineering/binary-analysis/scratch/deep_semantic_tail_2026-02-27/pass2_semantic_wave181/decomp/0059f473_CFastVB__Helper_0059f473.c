/* address: 0x0059f473 */
/* name: CFastVB__Helper_0059f473 */
/* signature: void __stdcall CFastVB__Helper_0059f473(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Helper_0059f473(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  undefined1 auVar9 [16];
  undefined1 auVar10 [16];

  fVar5 = (float)*(undefined8 *)param_2;
  fVar6 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar7 = (float)*(undefined8 *)((int)param_2 + 8);
  fVar8 = (float)((ulonglong)*(undefined8 *)((int)param_2 + 8) >> 0x20);
  fVar3 = fVar7 * fVar7;
  fVar4 = fVar8 * fVar8;
  fVar2 = fVar6 * fVar6 + fVar4;
  auVar9._4_4_ = fVar2;
  auVar9._0_4_ = fVar2;
  auVar9._8_4_ = fVar2;
  auVar9._12_4_ = fVar2;
  fVar1 = fVar5 * fVar5 + fVar3 + fVar2;
  auVar10._4_4_ = fVar2;
  auVar10._0_4_ = fVar1;
  auVar10._8_4_ = fVar3 + fVar3;
  auVar10._12_4_ = fVar4 + fVar4;
  auVar10 = rcpss(auVar9,auVar10);
  fVar2 = auVar10._0_4_;
  fVar1 = (fVar2 + fVar2) - fVar2 * fVar1 * fVar2;
  fVar6 = fVar6 * fRam0065e504;
  fVar7 = fVar7 * fRam0065e508;
  fVar8 = fVar8 * fRam0065e50c;
  *(float *)param_1 = fVar5 * _DAT_0065e500 * fVar1;
  *(float *)((int)param_1 + 4) = fVar6 * fVar1;
  *(float *)((int)param_1 + 8) = fVar7 * fVar1;
  *(float *)((int)param_1 + 0xc) = fVar8 * fVar1;
  return;
}

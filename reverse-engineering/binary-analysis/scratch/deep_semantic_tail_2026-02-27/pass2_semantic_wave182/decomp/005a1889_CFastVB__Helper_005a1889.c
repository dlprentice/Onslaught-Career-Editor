/* address: 0x005a1889 */
/* name: CFastVB__Helper_005a1889 */
/* signature: void __stdcall CFastVB__Helper_005a1889(void * param_1, void * param_2) */


void CFastVB__Helper_005a1889(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined1 auVar6 [16];

  fVar1 = *(float *)param_2;
  fVar2 = *(float *)((int)param_2 + 4);
  fVar3 = *(float *)((int)param_2 + 8);
  fVar4 = fVar1 * fVar1 + fVar2 * fVar2 + fVar3 * fVar3;
  if (fVar4 < 1.4210855e-14) {
    fVar4 = 0.0;
    *(undefined4 *)param_1 = 0;
    *(undefined4 *)((int)param_1 + 4) = 0;
  }
  else {
    auVar6 = rsqrtss(ZEXT416(0x28800000),ZEXT416((uint)fVar4));
    fVar5 = auVar6._0_4_;
    fVar4 = fVar5 * 0.5 * (3.0 - fVar4 * fVar5 * fVar5);
    *(float *)param_1 = fVar4 * fVar1;
    *(float *)((int)param_1 + 4) = fVar4 * fVar2;
    fVar4 = fVar4 * fVar3;
  }
  *(float *)((int)param_1 + 8) = fVar4;
  return;
}

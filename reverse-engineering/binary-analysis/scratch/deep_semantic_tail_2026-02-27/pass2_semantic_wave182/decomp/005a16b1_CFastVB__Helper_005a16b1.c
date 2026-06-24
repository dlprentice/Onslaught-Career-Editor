/* address: 0x005a16b1 */
/* name: CFastVB__Helper_005a16b1 */
/* signature: void __stdcall CFastVB__Helper_005a16b1(void * param_1, void * param_2, void * param_3) */


void CFastVB__Helper_005a16b1(void *param_1,void *param_2,void *param_3)

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

  if (((uint)param_3 & 0xf) == 0) {
    fVar3 = *(float *)((int)param_2 + 8);
    fVar1 = fVar3 * *(float *)((int)param_3 + 0x20);
    fVar2 = fVar3 * *(float *)((int)param_3 + 0x24);
    fVar3 = fVar3 * *(float *)((int)param_3 + 0x28);
    fVar6 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
    fVar4 = fVar6 * *(float *)((int)param_3 + 0x10);
    fVar5 = fVar6 * *(float *)((int)param_3 + 0x14);
    fVar6 = fVar6 * *(float *)((int)param_3 + 0x18);
    fVar9 = (float)*(undefined8 *)param_2;
    fVar7 = fVar9 * *(float *)param_3;
    fVar8 = fVar9 * *(float *)((int)param_3 + 4);
    fVar9 = fVar9 * *(float *)((int)param_3 + 8);
  }
  else {
    fVar3 = *(float *)((int)param_2 + 8);
    fVar1 = (float)*(undefined8 *)((int)param_3 + 0x20) * fVar3;
    fVar2 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x20) >> 0x20) * fVar3;
    fVar3 = (float)*(undefined8 *)((int)param_3 + 0x28) * fVar3;
    fVar6 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
    fVar4 = (float)*(undefined8 *)((int)param_3 + 0x10) * fVar6;
    fVar5 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x10) >> 0x20) * fVar6;
    fVar6 = (float)*(undefined8 *)((int)param_3 + 0x18) * fVar6;
    fVar9 = (float)*(undefined8 *)param_2;
    fVar7 = (float)*(undefined8 *)param_3 * fVar9;
    fVar8 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20) * fVar9;
    fVar9 = (float)*(undefined8 *)((int)param_3 + 8) * fVar9;
  }
  *(ulonglong *)param_1 = CONCAT44(fVar8 + fVar5 + fVar2,fVar7 + fVar4 + fVar1);
  *(float *)((int)param_1 + 8) = fVar9 + fVar6 + fVar3;
  return;
}

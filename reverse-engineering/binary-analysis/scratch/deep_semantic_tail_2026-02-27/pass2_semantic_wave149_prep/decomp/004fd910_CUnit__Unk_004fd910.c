/* address: 0x004fd910 */
/* name: CUnit__Unk_004fd910 */
/* signature: void __thiscall CUnit__Unk_004fd910(void * this, int param_1, void * param_2) */


void __thiscall CUnit__Unk_004fd910(void *this,int param_1,void *param_2)

{
  int iVar1;
  undefined4 *puVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;
  int *piVar8;
  float local_20;
  float local_1c;
  int local_18;
  int local_14;

  local_20 = 0.0;
  local_1c = 0.0;
  local_18 = 0;
  puVar2 = DAT_00855160;
  if (DAT_00855160 == (undefined4 *)0x0) {
    piVar8 = (int *)0x0;
  }
  else {
    piVar8 = (int *)*DAT_00855160;
  }
  while (piVar8 != (int *)0x0) {
    iVar1 = *(int *)((int)this + 0x138);
    iVar7 = (**(code **)(*piVar8 + 0x108))();
    if ((iVar7 == iVar1) &&
       (fVar3 = *(float *)((int)this + 0x1c) - local_20,
       fVar4 = *(float *)((int)this + 0x20) - local_1c,
       fVar5 = *(float *)((int)this + 0x1c) - (float)piVar8[7],
       fVar6 = *(float *)((int)this + 0x20) - (float)piVar8[8],
       SQRT(fVar5 * fVar5 + fVar6 * fVar6) < SQRT(fVar3 * fVar3 + fVar4 * fVar4))) {
      local_20 = (float)piVar8[7];
      local_1c = (float)piVar8[8];
      local_18 = piVar8[9];
      local_14 = piVar8[10];
    }
    puVar2 = (undefined4 *)puVar2[1];
    if (puVar2 == (undefined4 *)0x0) {
      piVar8 = (int *)0x0;
    }
    else {
      piVar8 = (int *)*puVar2;
    }
  }
  *(float *)param_1 = local_20;
  *(float *)(param_1 + 4) = local_1c;
  *(int *)(param_1 + 8) = local_18;
  *(int *)(param_1 + 0xc) = local_14;
  return;
}

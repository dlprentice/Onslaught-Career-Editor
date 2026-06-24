/* address: 0x004fdad0 */
/* name: CUnit__Unk_004fdad0 */
/* signature: void __thiscall CUnit__Unk_004fdad0(void * this, void * param_1, int param_2) */


void __thiscall CUnit__Unk_004fdad0(void *this,void *param_1,int param_2)

{
  undefined4 *puVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  bool bVar5;
  int iVar6;
  void *this_00;
  int unaff_EBP;

  if ((param_1 != (void *)0x0) && (iVar6 = (**(code **)(*(int *)this + 0x18c))(), iVar6 != 0)) {
    puVar1 = *(undefined4 **)((int)this + 0x18c);
    if (puVar1 == (undefined4 *)0x0) {
      this_00 = (void *)0x0;
    }
    else {
      this_00 = (void *)*puVar1;
    }
    while (this_00 != (void *)0x0) {
      iVar6 = CUnit__Helper_004e43d0((int)this_00);
      if (iVar6 != 0) {
        bVar5 = false;
        iVar6 = (**(code **)(*(int *)this + 0x10c))();
        if ((((iVar6 != 0) && ((*(byte *)(*(int *)((int)this_00 + 0x3d0) + 0x14) & 2) != 0)) ||
            ((iVar6 = HeightDelta__Below025_D0((int)this), iVar6 != 0 &&
             ((*(byte *)(*(int *)((int)this_00 + 0x3d0) + 0x14) & 1) != 0)))) ||
           (((iVar6 = (**(code **)(*(int *)this + 0x10c))(), iVar6 == 0 &&
             (iVar6 = HeightDelta__Below025_D0((int)this), iVar6 == 0)) &&
            ((*(byte *)(*(int *)((int)this_00 + 0x3d0) + 0x14) & 4) != 0)))) {
          bVar5 = true;
        }
        fVar2 = *(float *)((int)param_1 + 0x1c) - *(float *)((int)this + 0x1c);
        fVar4 = *(float *)((int)param_1 + 0x20) - *(float *)((int)this + 0x20);
        fVar3 = *(float *)((int)param_1 + 0x24) - *(float *)((int)this + 0x24);
        fVar2 = SQRT(fVar2 * fVar2 + fVar4 * fVar4 + fVar3 * fVar3);
        iVar6 = CSquadNormal__Helper_004e4480(this_00,(int)param_1,unaff_EBP);
        if (((iVar6 != 0) && (bVar5)) &&
           ((*(float *)(*(int *)((int)this_00 + 0x3d0) + 0x2c) <= fVar2 &&
            (fVar2 <= *(float *)(*(int *)((int)this_00 + 0x3d0) + 0x30))))) {
          CSpawnerThng__DoSpawn();
        }
      }
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        this_00 = (void *)0x0;
      }
      else {
        this_00 = (void *)*puVar1;
      }
    }
  }
  return;
}

/* address: 0x004fb3d0 */
/* name: CSquadNormal__Helper_004fb3d0 */
/* signature: int __thiscall CSquadNormal__Helper_004fb3d0(void * this, int param_1, void * param_2) */


int __thiscall CSquadNormal__Helper_004fb3d0(void *this,int param_1,void *param_2)

{
  undefined4 *puVar1;
  float fVar2;
  int iVar3;
  uint uVar4;
  void *pvVar5;
  int unaff_EDI;
  int *piVar6;
  uint uStack_8;

  if ((param_1 != 0) && (iVar3 = (**(code **)(*(int *)param_1 + 0x1b0))(), iVar3 != 0)) {
    puVar1 = *(undefined4 **)((int)this + 0x18c);
    if (puVar1 == (undefined4 *)0x0) {
      pvVar5 = (void *)0x0;
    }
    else {
      pvVar5 = (void *)*puVar1;
    }
    while (pvVar5 != (void *)0x0) {
      iVar3 = CSquadNormal__Helper_004e4480(pvVar5,param_1,unaff_EDI);
      if (iVar3 != 0) {
        return 1;
      }
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        pvVar5 = (void *)0x0;
      }
      else {
        pvVar5 = (void *)*puVar1;
      }
    }
    piVar6 = *(int **)((int)this + 0x17c);
    if (piVar6 == (int *)0x0) {
      pvVar5 = (void *)0x0;
    }
    else {
      pvVar5 = (void *)*piVar6;
    }
    if (pvVar5 != (void *)0x0) {
      while (uVar4 = CSquadNormal__Helper_0050a0b0(pvVar5,param_1,unaff_EDI), fVar2 = DAT_006fbdf4,
            uVar4 == 0) {
        piVar6 = (int *)piVar6[1];
        if (piVar6 == (int *)0x0) {
          pvVar5 = (void *)0x0;
        }
        else {
          pvVar5 = (void *)*piVar6;
        }
        if (pvVar5 == (void *)0x0) {
          return 0;
        }
      }
      uStack_8 = (uint)(longlong)ROUND(*(float *)(param_1 + 0x20));
      uVar4 = uStack_8;
      uStack_8 = (uint)(longlong)ROUND(*(float *)(param_1 + 0x1c));
      uVar4 = CWorld__Helper_0047ea20(0x6fadc8,uStack_8,uVar4);
      fVar2 = (float)(int)(short)uVar4 * fVar2;
      if (DAT_006fbdfc < fVar2) {
        fVar2 = DAT_006fbdfc;
      }
      fVar2 = fVar2 - *(float *)(param_1 + 0x24);
      if ((*(float *)(*(int *)((int)pvVar5 + 0xa0) + 0x6c) <= fVar2) &&
         (fVar2 <= *(float *)(*(int *)((int)pvVar5 + 0xa0) + 0x70))) {
        return 1;
      }
    }
  }
  return 0;
}

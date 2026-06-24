/* address: 0x004140d0 */
/* name: CMonitor__Unk_004140d0 */
/* signature: int __thiscall CMonitor__Unk_004140d0(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CMonitor__Unk_004140d0(void *this,void *param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  void *pvVar4;
  int iVar5;
  float *pfVar6;

  piVar1 = *(int **)this;
  *(int **)((int)this + 8) = piVar1;
  if (piVar1 == (int *)0x0) {
    pvVar4 = (void *)0x0;
  }
  else {
    pvVar4 = (void *)*piVar1;
  }
  while (pvVar4 != (void *)0x0) {
    if (pvVar4 == param_1) {
      iVar2 = *(int *)((int)this + 0x20);
      iVar5 = *(int *)(*(int *)((int)pvVar4 + 0xa4) + 0x24);
      if (*(int *)(iVar2 + 0x55c + iVar5 * 4) == 0) {
        if (_DAT_005d856c < *(float *)(iVar2 + 0x52c + iVar5 * 4)) {
          pfVar6 = (float *)(*(int *)((int)this + 0x20) + 0x52c + iVar5 * 4);
          *pfVar6 = *pfVar6 - *(float *)(*(int *)((int)pvVar4 + 0xa4) + 0x20);
          goto LAB_004143b2;
        }
        if (*(float *)(iVar2 + 0x608) < DAT_00672fd0 - _DAT_005d8c44) {
          *(float *)(iVar2 + 0x608) = DAT_00672fd0;
        }
      }
      else {
        if (0 < *(int *)((int)pvVar4 + 0x68)) {
          return 1;
        }
        if ((*(float *)(iVar2 + 0x52c + iVar5 * 4) <
             *(float *)(*(int *)(iVar2 + 0x4b0) + 0x88 + iVar5 * 4)) &&
           (*(int *)(iVar2 + 0x544 + iVar5 * 4) == 0)) {
          pfVar6 = (float *)(*(int *)((int)this + 0x20) + 0x52c + iVar5 * 4);
          *pfVar6 = *(float *)(*(int *)((int)pvVar4 + 0xa4) + 0x20) + *pfVar6;
          *(undefined4 *)((int)this + 0x14) = 0;
          return 1;
        }
        *(undefined4 *)(iVar2 + 0x544 + iVar5 * 4) = 1;
        CMonitor__Unk_0040f110(*(int *)((int)this + 0x20));
      }
    }
    piVar1 = *(int **)(*(int *)((int)this + 8) + 4);
    *(int **)((int)this + 8) = piVar1;
    if (piVar1 == (int *)0x0) {
      pvVar4 = (void *)0x0;
    }
    else {
      pvVar4 = (void *)*piVar1;
    }
  }
  pvVar4 = *(void **)((int)this + 0x18);
  if ((pvVar4 != (void *)0x0) && (param_1 == pvVar4)) {
    iVar2 = *(int *)((int)pvVar4 + 0xa4);
    iVar5 = *(int *)((int)this + 0x20);
    iVar3 = *(int *)(iVar2 + 0x24);
    if (*(int *)(iVar5 + 0x55c + iVar3 * 4) == 0) {
      if (_DAT_005d856c < *(float *)(iVar5 + 0x52c + iVar3 * 4)) {
        *(float *)(iVar5 + 0x52c + iVar3 * 4) =
             *(float *)(iVar5 + 0x52c + iVar3 * 4) - *(float *)(iVar2 + 0x20);
        pfVar6 = (float *)(*(int *)((int)this + 0x20) + 0x52c + iVar3 * 4);
        goto LAB_004143bc;
      }
      if (*(float *)(iVar5 + 0x608) < DAT_00672fd0 - _DAT_005d8c44) {
        *(float *)(iVar5 + 0x608) = DAT_00672fd0;
      }
    }
    else {
      if (0 < *(int *)((int)pvVar4 + 0x68)) {
        return 1;
      }
      if ((*(float *)(iVar5 + 0x52c + iVar3 * 4) <
           *(float *)(*(int *)(iVar5 + 0x4b0) + 0x88 + iVar3 * 4)) &&
         (*(int *)(iVar5 + 0x544 + iVar3 * 4) == 0)) {
        *(float *)(iVar5 + 0x52c + iVar3 * 4) =
             *(float *)(iVar2 + 0x20) + *(float *)(iVar5 + 0x52c + iVar3 * 4);
        *(undefined4 *)((int)this + 0x14) = 0;
        return 1;
      }
      *(undefined4 *)(iVar5 + 0x544 + iVar3 * 4) = 1;
      CMonitor__Unk_0040f110(*(int *)((int)this + 0x20));
    }
  }
  pvVar4 = *(void **)((int)this + 0x1c);
  if ((pvVar4 == (void *)0x0) || (param_1 != pvVar4)) {
    return 0;
  }
  iVar2 = *(int *)((int)pvVar4 + 0xa4);
  iVar3 = *(int *)((int)this + 0x20);
  iVar5 = *(int *)(iVar2 + 0x24);
  if (*(int *)(iVar3 + 0x55c + iVar5 * 4) != 0) {
    if (0 < *(int *)((int)pvVar4 + 0x68)) {
      *(undefined4 *)(iVar3 + 0x2f8) = 0;
      return 1;
    }
    if ((*(float *)(iVar3 + 0x52c + iVar5 * 4) <
         *(float *)(*(int *)(iVar3 + 0x4b0) + 0x88 + iVar5 * 4)) &&
       (*(int *)(iVar3 + 0x544 + iVar5 * 4) == 0)) {
      *(float *)(iVar3 + 0x52c + iVar5 * 4) =
           *(float *)(iVar2 + 0x20) + *(float *)(iVar3 + 0x52c + iVar5 * 4);
      *(undefined4 *)((int)this + 0x14) = 0;
      *(undefined4 *)(*(int *)((int)this + 0x20) + 0x2f8) = 0;
      return 1;
    }
    *(undefined4 *)(iVar3 + 0x544 + iVar5 * 4) = 1;
    CMonitor__Unk_0040f110(*(int *)((int)this + 0x20));
    return 0;
  }
  if (*(float *)(iVar3 + 0x52c + iVar5 * 4) <= _DAT_005d856c) {
    if (DAT_00672fd0 - _DAT_005d8c44 <= *(float *)(iVar3 + 0x608)) {
      return 0;
    }
    *(float *)(iVar3 + 0x608) = DAT_00672fd0;
    return 0;
  }
  *(float *)(iVar3 + 0x52c + iVar5 * 4) =
       *(float *)(iVar3 + 0x52c + iVar5 * 4) - *(float *)(iVar2 + 0x20);
  *(undefined4 *)(*(int *)((int)this + 0x20) + 0x2f8) = 0;
LAB_004143b2:
  pfVar6 = (float *)(*(int *)((int)this + 0x20) + 0x52c + iVar5 * 4);
LAB_004143bc:
  if (*pfVar6 < _DAT_005d856c) {
    *pfVar6 = 0.0;
  }
  return 1;
}

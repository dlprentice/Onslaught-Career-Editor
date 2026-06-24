/* address: 0x00412050 */
/* name: CMonitor__Unk_00412050 */
/* signature: int __thiscall CMonitor__Unk_00412050(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CMonitor__Unk_00412050(void *this,void *param_1,int param_2)

{
  float *pfVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  void *pvVar5;

  piVar2 = *(int **)this;
  *(int **)((int)this + 8) = piVar2;
  if (piVar2 == (int *)0x0) {
    pvVar5 = (void *)0x0;
  }
  else {
    pvVar5 = (void *)*piVar2;
  }
  do {
    if (pvVar5 == (void *)0x0) {
      return 0;
    }
    if (pvVar5 == param_1) {
      iVar3 = *(int *)((int)this + 0x18);
      iVar4 = *(int *)(*(int *)((int)pvVar5 + 0xa4) + 0x24);
      if (*(int *)(iVar3 + 0x55c + iVar4 * 4) == 0) {
        if (_DAT_005d856c < *(float *)(iVar3 + 0x52c + iVar4 * 4)) {
          pfVar1 = (float *)(*(int *)((int)this + 0x18) + 0x52c + iVar4 * 4);
          *pfVar1 = *pfVar1 - *(float *)(*(int *)((int)pvVar5 + 0xa4) + 0x20);
          if (_DAT_005d856c <= *(float *)(*(int *)((int)this + 0x18) + 0x52c + iVar4 * 4)) {
            return 1;
          }
          *(undefined4 *)(*(int *)((int)this + 0x18) + 0x52c + iVar4 * 4) = 0;
          return 1;
        }
        if (*(float *)(iVar3 + 0x608) < DAT_00672fd0 - _DAT_005d8c44) {
          *(float *)(iVar3 + 0x608) = DAT_00672fd0;
        }
      }
      else {
        if (0 < *(int *)((int)pvVar5 + 0x68)) {
          return 1;
        }
        if ((*(float *)(iVar3 + 0x52c + iVar4 * 4) <
             *(float *)(*(int *)(iVar3 + 0x4b0) + 0x88 + iVar4 * 4)) &&
           (*(int *)(iVar3 + 0x544 + iVar4 * 4) == 0)) {
          pfVar1 = (float *)(*(int *)((int)this + 0x18) + 0x52c + iVar4 * 4);
          *pfVar1 = (*(float *)(*(int *)((int)pvVar5 + 0xa4) + 0x20) - (float)_DAT_006236a4) +
                    *pfVar1;
          return 1;
        }
        *(undefined4 *)(iVar3 + 0x544 + iVar4 * 4) = 1;
        CMonitor__Unk_0040f110(*(int *)((int)this + 0x18));
      }
    }
    piVar2 = *(int **)(*(int *)((int)this + 8) + 4);
    *(int **)((int)this + 8) = piVar2;
    if (piVar2 == (int *)0x0) {
      pvVar5 = (void *)0x0;
    }
    else {
      pvVar5 = (void *)*piVar2;
    }
  } while( true );
}

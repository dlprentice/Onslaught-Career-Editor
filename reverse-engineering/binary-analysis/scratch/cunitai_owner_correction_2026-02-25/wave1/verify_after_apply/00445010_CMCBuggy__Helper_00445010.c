/* address: 0x00445010 */
/* name: CMCBuggy__Helper_00445010 */
/* signature: double __thiscall CMCBuggy__Helper_00445010(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CMCBuggy__Helper_00445010(void *this,int param_1,int param_2)

{
  int *piVar1;
  int iVar2;

  if (0 < *(int *)((int)this + 0x20)) {
    piVar1 = *(int **)(*(int *)((int)this + 4) + param_1 * 4);
    if (piVar1 == (int *)0x0) {
      if ((param_1 != 0) &&
         (piVar1 = *(int **)(*(int *)((int)this + 0x10) + 0x30), piVar1 != (int *)0x0)) {
        (**(code **)(*piVar1 + 0x24))();
      }
    }
    else {
      iVar2 = (**(code **)(*piVar1 + 0x14))();
      if (iVar2 == 0) {
        return (double)(float)piVar1[0x11];
      }
    }
  }
  return (double)_DAT_005d856c;
}

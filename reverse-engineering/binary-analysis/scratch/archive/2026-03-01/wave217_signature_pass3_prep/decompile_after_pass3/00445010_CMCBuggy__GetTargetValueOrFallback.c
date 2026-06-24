/* address: 0x00445010 */
/* name: CMCBuggy__GetTargetValueOrFallback */
/* signature: double __thiscall CMCBuggy__GetTargetValueOrFallback(void * this, int target_id, int fallback_id) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CMCBuggy__GetTargetValueOrFallback(void *this,int target_id,int fallback_id)

{
  int *piVar1;
  int iVar2;

  if (0 < *(int *)((int)this + 0x20)) {
    piVar1 = *(int **)(*(int *)((int)this + 4) + target_id * 4);
    if (piVar1 == (int *)0x0) {
      if ((target_id != 0) &&
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

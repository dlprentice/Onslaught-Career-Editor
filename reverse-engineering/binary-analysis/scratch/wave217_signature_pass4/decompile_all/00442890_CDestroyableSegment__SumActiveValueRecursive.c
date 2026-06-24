/* address: 0x00442890 */
/* name: CDestroyableSegment__SumActiveValueRecursive */
/* signature: double __thiscall CDestroyableSegment__SumActiveValueRecursive(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall CDestroyableSegment__SumActiveValueRecursive(void *this)

{
  undefined4 *puVar1;
  int iVar2;
  void *this_00;
  double dVar3;
  float local_4;

  local_4 = 0.0;
  if (((*(int *)((int)this + 0x1c) != 0) &&
      (iVar2 = (**(code **)(*(int *)this + 0x18))(), iVar2 == 0)) &&
     (*(float *)((int)this + 0xc) != _DAT_005d856c)) {
    local_4 = *(float *)((int)this + 0x10);
  }
  puVar1 = *(undefined4 **)((int)this + 0x24);
  if (puVar1 == (undefined4 *)0x0) {
    this_00 = (void *)0x0;
  }
  else {
    this_00 = (void *)*puVar1;
  }
  while (this_00 != (void *)0x0) {
    dVar3 = CDestroyableSegment__SumActiveValueRecursive(this_00);
    local_4 = (float)dVar3 + local_4;
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      this_00 = (void *)0x0;
    }
    else {
      this_00 = (void *)*puVar1;
    }
  }
  return (double)local_4;
}

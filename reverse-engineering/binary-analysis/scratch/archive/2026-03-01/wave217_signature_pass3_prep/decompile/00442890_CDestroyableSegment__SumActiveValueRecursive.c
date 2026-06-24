/* address: 0x00442890 */
/* name: CDestroyableSegment__SumActiveValueRecursive */
/* signature: double __fastcall CDestroyableSegment__SumActiveValueRecursive(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CDestroyableSegment__SumActiveValueRecursive(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  void *pvVar3;
  double dVar4;
  float local_4;

  local_4 = 0.0;
  if (((*(int *)((int)param_1 + 0x1c) != 0) &&
      (iVar2 = (**(code **)(*(int *)param_1 + 0x18))(), iVar2 == 0)) &&
     (*(float *)((int)param_1 + 0xc) != _DAT_005d856c)) {
    local_4 = *(float *)((int)param_1 + 0x10);
  }
  puVar1 = *(undefined4 **)((int)param_1 + 0x24);
  if (puVar1 == (undefined4 *)0x0) {
    pvVar3 = (void *)0x0;
  }
  else {
    pvVar3 = (void *)*puVar1;
  }
  while (pvVar3 != (void *)0x0) {
    dVar4 = CDestroyableSegment__SumActiveValueRecursive(pvVar3);
    local_4 = (float)dVar4 + local_4;
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = (void *)*puVar1;
    }
  }
  return (double)local_4;
}

/* address: 0x00412000 */
/* name: CMonitor__ClearTrackedEntryFlag60ByIndex */
/* signature: void __fastcall CMonitor__ClearTrackedEntryFlag60ByIndex(void * param_1) */


void __fastcall CMonitor__ClearTrackedEntryFlag60ByIndex(void *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  piVar1 = *(int **)param_1;
  iVar3 = 0;
  *(int **)((int)param_1 + 8) = piVar1;
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  if (iVar2 != 0) {
    while (iVar3 != *(int *)((int)param_1 + 0x10)) {
      iVar3 = iVar3 + 1;
      piVar1 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar1;
      }
      if (iVar2 == 0) {
        return;
      }
    }
    if (iVar2 != 0) {
      *(undefined4 *)(iVar2 + 0x60) = 0;
    }
  }
  return;
}

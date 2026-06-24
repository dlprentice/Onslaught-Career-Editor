/* address: 0x00414030 */
/* name: CGeneralVolume__ResolveCurrentOrFallbackEntry */
/* signature: int __fastcall CGeneralVolume__ResolveCurrentOrFallbackEntry(void * param_1) */


int __fastcall CGeneralVolume__ResolveCurrentOrFallbackEntry(void *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  if ((*(uint *)((int)param_1 + 0x10) != 0) ||
     (((*(int *)(*(int *)((int)param_1 + 0x20) + 0x2fc) == 0 ||
       (iVar3 = *(int *)((int)param_1 + 0x1c), iVar3 == 0)) &&
      (iVar3 = *(int *)((int)param_1 + 0x18), iVar3 == 0)))) {
    iVar3 = *(int *)((int)param_1 + 0x18);
    uVar5 = (uint)(iVar3 != 0);
    piVar1 = *(int **)param_1;
    *(int **)((int)param_1 + 8) = piVar1;
    if (piVar1 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar1;
    }
    while (iVar4 != 0) {
      if (uVar5 == *(uint *)((int)param_1 + 0x10)) {
        return iVar4;
      }
      uVar5 = uVar5 + 1;
      piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar2;
      if (piVar2 == (int *)0x0) {
        iVar4 = 0;
      }
      else {
        iVar4 = *piVar2;
      }
    }
    *(undefined4 *)((int)param_1 + 0x10) = 0;
    if (iVar3 != 0) {
      return iVar3;
    }
    *(int **)((int)param_1 + 8) = piVar1;
    if ((piVar1 != (int *)0x0) && (*piVar1 != 0)) {
      *(int **)((int)param_1 + 8) = piVar1;
      return *piVar1;
    }
    iVar3 = 0;
  }
  return iVar3;
}

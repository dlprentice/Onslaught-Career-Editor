/* address: 0x00413eb0 */
/* name: CGeneralVolume__SelectNextEnabledEntry */
/* signature: void __fastcall CGeneralVolume__SelectNextEnabledEntry(void * param_1) */


void __fastcall CGeneralVolume__SelectNextEnabledEntry(void *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  uint local_8;

  iVar3 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
  uVar7 = *(int *)((int)param_1 + 0x10) + 1;
  iVar3 = *(int *)(*(int *)(iVar3 + 0xa4) + 0x34);
  bVar8 = *(int *)((int)param_1 + 0x18) != 0;
  local_8 = (uint)bVar8;
  piVar1 = *(int **)param_1;
  *(int **)((int)param_1 + 8) = piVar1;
  if (piVar1 != (int *)0x0) {
    iVar5 = *piVar1;
    local_8 = (uint)bVar8;
    while (iVar5 != 0) {
      local_8 = local_8 + 1;
      piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar2;
      if (piVar2 == (int *)0x0) break;
      iVar5 = *piVar2;
    }
  }
  if (uVar7 == *(uint *)((int)param_1 + 0x10)) {
    return;
  }
  do {
    if ((uVar7 == 0) && (iVar5 = *(int *)((int)param_1 + 0x18), iVar5 != 0)) {
      if ((*(int *)(*(int *)((int)param_1 + 0x20) + 0x2fc) == 0) ||
         (iVar4 = *(int *)((int)param_1 + 0x1c), *(int *)((int)param_1 + 0x1c) == 0)) {
LAB_00413f35:
        iVar4 = iVar5;
        if (iVar5 == 0) goto LAB_00413f6d;
      }
      iVar5 = *(int *)(*(int *)(iVar4 + 0xa4) + 0x24);
      if ((*(int *)(iVar4 + 0x9c) != 0) &&
         ((*(int *)(*(int *)((int)param_1 + 0x20) + 0x55c + iVar5 * 4) != 0 ||
          (*(float *)(*(int *)(iVar4 + 0xa4) + 0x20) <=
           *(float *)(*(int *)((int)param_1 + 0x20) + 0x52c + iVar5 * 4))))) {
        *(uint *)((int)param_1 + 0x10) = uVar7;
        *(undefined4 *)(*(int *)((int)param_1 + 0x20) + 0x588) = 0;
        iVar5 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
        if (iVar5 != 0) {
          *(undefined4 *)(iVar5 + 0x60) = 0;
        }
        iVar5 = CGeneralVolume__ResolveCurrentOrFallbackEntry(param_1);
        if (iVar3 == *(int *)(*(int *)(iVar5 + 0xa4) + 0x34)) {
          return;
        }
        CGeneralVolume__SetParam2CC_ToOne(*(int *)((int)param_1 + 0x20));
        return;
      }
    }
    else {
      uVar6 = (uint)(*(int *)((int)param_1 + 0x18) != 0);
      *(int **)((int)param_1 + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piVar1;
      }
      while (iVar5 != 0) {
        if (uVar6 == uVar7) goto LAB_00413f35;
        uVar6 = uVar6 + 1;
        piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
        *(int **)((int)param_1 + 8) = piVar2;
        if (piVar2 == (int *)0x0) {
          iVar5 = 0;
        }
        else {
          iVar5 = *piVar2;
        }
      }
    }
LAB_00413f6d:
    uVar7 = uVar7 + 1;
    if ((int)local_8 <= (int)uVar7) {
      uVar7 = 0;
    }
    if (uVar7 == *(uint *)((int)param_1 + 0x10)) {
      return;
    }
  } while( true );
}

/* address: 0x00413cf0 */
/* name: CGeneralVolume__UpdateCurrentEntryProgressAndRefresh */
/* signature: void __fastcall CGeneralVolume__UpdateCurrentEntryProgressAndRefresh(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__UpdateCurrentEntryProgressAndRefresh(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  void *pvVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int local_8;

  iVar2 = CGeneralVolume__ResolveCurrentOrFallbackEntry((void *)param_1);
  if (((iVar2 != 0) && (*(int *)(iVar2 + 0x9c) != 0)) &&
     (iVar3 = CEngine__Unk_0050a080(iVar2), iVar3 != 0)) {
    iVar3 = *(int *)(iVar2 + 0xa4);
    iVar4 = 1;
    piVar8 = (int *)(iVar3 + 0x10);
    piVar7 = piVar8;
    do {
      if (*piVar7 != -1) {
        iVar4 = *(int *)(iVar3 + 0x24);
        iVar1 = *(int *)(param_1 + 0x20);
        if ((*(int *)(iVar1 + 0x55c + iVar4 * 4) == 0) &&
           (*(float *)(iVar1 + 0x52c + iVar4 * 4) <= _DAT_005d856c)) {
          return;
        }
        local_8 = 0;
        iVar6 = 0;
        piVar7 = (int *)(iVar3 + 0xc);
        do {
          if (*piVar7 != -1) {
            local_8 = iVar6;
          }
          iVar6 = iVar6 + 100;
          piVar7 = piVar7 + 1;
        } while (iVar6 < 500);
        iVar6 = 1;
        while (*piVar8 == -1) {
          iVar6 = iVar6 + 1;
          piVar8 = piVar8 + 1;
          if (4 < iVar6) {
            return;
          }
        }
        if ((float)local_8 <= *(float *)(iVar2 + 0x60)) {
          return;
        }
        if (*(int *)(iVar1 + 0x544 + iVar4 * 4) != 0) {
          return;
        }
        *(uint *)(iVar1 + 0x588) = (uint)(*(int *)(iVar3 + 0x2c) == 0);
        CEngine__Unk_005068f0(iVar2);
        iVar3 = *(int *)(param_1 + 0x20);
        *(undefined4 *)(param_1 + 0x14) = 0;
        if (*(int *)(iVar3 + 0x55c + iVar4 * 4) == 0) {
          return;
        }
        if ((*(float *)(iVar3 + 0x52c + iVar4 * 4) <
             *(float *)(*(int *)(iVar3 + 0x4b0) + 0x88 + iVar4 * 4)) &&
           (*(int *)(iVar3 + 0x544 + iVar4 * 4) == 0)) {
          *(float *)(iVar3 + 0x52c + iVar4 * 4) =
               *(float *)(*(int *)(iVar2 + 0xa4) + 0x20) + *(float *)(iVar3 + 0x52c + iVar4 * 4);
          return;
        }
        *(undefined4 *)(iVar3 + 0x544 + iVar4 * 4) = 1;
        CEngine__Helper_0040f110(*(int *)(param_1 + 0x20));
        *(undefined4 *)(*(int *)(param_1 + 0x20) + 0x588) = 0;
        pvVar5 = (void *)CGeneralVolume__ResolveCurrentOrFallbackEntry((void *)param_1);
        if (pvVar5 == (void *)0x0) {
          return;
        }
        if (*(int *)((int)pvVar5 + 0x9c) == 0) {
          return;
        }
        CGeneralVolume__Helper_00506010(pvVar5);
        return;
      }
      iVar4 = iVar4 + 1;
      piVar7 = piVar7 + 1;
    } while (iVar4 < 5);
    *(undefined4 *)(*(int *)(param_1 + 0x20) + 0x588) = 0;
    pvVar5 = (void *)CGeneralVolume__ResolveCurrentOrFallbackEntry((void *)param_1);
    if ((pvVar5 != (void *)0x0) && (*(int *)((int)pvVar5 + 0x9c) != 0)) {
      CGeneralVolume__Helper_00506010(pvVar5);
    }
  }
  return;
}

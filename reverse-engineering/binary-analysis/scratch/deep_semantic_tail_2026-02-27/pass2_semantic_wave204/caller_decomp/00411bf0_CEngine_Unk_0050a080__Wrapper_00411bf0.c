/* address: 0x00411bf0 */
/* name: CEngine_Unk_0050a080__Wrapper_00411bf0 */
/* signature: void __fastcall CEngine_Unk_0050a080__Wrapper_00411bf0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CEngine_Unk_0050a080__Wrapper_00411bf0(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  void *pvVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  int local_4;

  iVar7 = 0;
  piVar9 = *(int **)param_1;
  *(int **)((int)param_1 + 8) = piVar9;
  if (piVar9 == (int *)0x0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *piVar9;
  }
  if (iVar3 != 0) {
    while (iVar7 != *(int *)((int)param_1 + 0x10)) {
      iVar7 = iVar7 + 1;
      piVar9 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar9;
      if (piVar9 == (int *)0x0) {
        iVar3 = 0;
      }
      else {
        iVar3 = *piVar9;
      }
      if (iVar3 == 0) {
        return;
      }
    }
    if (((iVar3 != 0) && (*(int *)(iVar3 + 0x9c) != 0)) &&
       (iVar7 = CEngine__CanProceedByTargetRangeGate(iVar3), iVar7 != 0)) {
      iVar7 = *(int *)(iVar3 + 0xa4);
      iVar4 = 1;
      piVar9 = (int *)(iVar7 + 0x10);
      piVar8 = piVar9;
      do {
        if (*piVar8 != -1) {
          iVar4 = *(int *)(iVar7 + 0x24);
          iVar1 = *(int *)((int)param_1 + 0x18);
          if ((*(int *)(iVar1 + 0x55c + iVar4 * 4) == 0) &&
             (*(float *)(iVar1 + 0x52c + iVar4 * 4) <= _DAT_005d856c)) {
            return;
          }
          local_4 = 0;
          iVar5 = 0;
          piVar8 = (int *)(iVar7 + 0xc);
          do {
            if (*piVar8 != -1) {
              local_4 = iVar5;
            }
            iVar5 = iVar5 + 100;
            piVar8 = piVar8 + 1;
          } while (iVar5 < 500);
          iVar5 = 1;
          while (*piVar9 == -1) {
            iVar5 = iVar5 + 1;
            piVar9 = piVar9 + 1;
            if (4 < iVar5) {
              return;
            }
          }
          if ((float)local_4 <= *(float *)(iVar3 + 0x60)) {
            return;
          }
          if (*(int *)(iVar1 + 0x544 + iVar4 * 4) != 0) {
            return;
          }
          *(uint *)(iVar1 + 0x588) = (uint)(*(int *)(iVar7 + 0x2c) == 0);
          CEngine__AdvanceProgressIfAnySlotAssigned(iVar3);
          iVar7 = *(int *)((int)param_1 + 0x18);
          if (*(int *)(iVar7 + 0x55c + iVar4 * 4) == 0) {
            return;
          }
          if ((*(float *)(iVar7 + 0x52c + iVar4 * 4) <
               *(float *)(*(int *)(iVar7 + 0x4b0) + 0x88 + iVar4 * 4)) &&
             (*(int *)(iVar7 + 0x544 + iVar4 * 4) == 0)) {
            *(float *)(iVar7 + 0x52c + iVar4 * 4) =
                 *(float *)(*(int *)(iVar3 + 0xa4) + 0x20) + *(float *)(iVar7 + 0x52c + iVar4 * 4);
            return;
          }
          *(undefined4 *)(iVar7 + 0x544 + iVar4 * 4) = 1;
          CEngine__Helper_0040f110(*(int *)((int)param_1 + 0x18));
          iVar7 = 0;
          *(undefined4 *)(*(int *)((int)param_1 + 0x18) + 0x588) = 0;
          pvVar6 = CSPtrSet__First(param_1);
          if (pvVar6 == (void *)0x0) {
            return;
          }
          while (iVar7 != *(int *)((int)param_1 + 0x10)) {
            iVar7 = iVar7 + 1;
            puVar2 = *(undefined4 **)(*(int *)((int)param_1 + 8) + 4);
            *(undefined4 **)((int)param_1 + 8) = puVar2;
            if (puVar2 == (undefined4 *)0x0) {
              pvVar6 = (void *)0x0;
            }
            else {
              pvVar6 = (void *)*puVar2;
            }
            if (pvVar6 == (void *)0x0) {
              return;
            }
          }
          if (pvVar6 == (void *)0x0) {
            return;
          }
          if (*(int *)((int)pvVar6 + 0x9c) == 0) {
            return;
          }
          CGeneralVolume__Helper_00506010(pvVar6);
          return;
        }
        iVar4 = iVar4 + 1;
        piVar8 = piVar8 + 1;
      } while (iVar4 < 5);
      iVar7 = 0;
      *(undefined4 *)(*(int *)((int)param_1 + 0x18) + 0x588) = 0;
      piVar9 = *(int **)param_1;
      *(int **)((int)param_1 + 8) = piVar9;
      if (piVar9 == (int *)0x0) {
        pvVar6 = (void *)0x0;
      }
      else {
        pvVar6 = (void *)*piVar9;
      }
      if (pvVar6 != (void *)0x0) {
        while (iVar7 != *(int *)((int)param_1 + 0x10)) {
          iVar7 = iVar7 + 1;
          piVar9 = *(int **)(*(int *)((int)param_1 + 8) + 4);
          *(int **)((int)param_1 + 8) = piVar9;
          if (piVar9 == (int *)0x0) {
            pvVar6 = (void *)0x0;
          }
          else {
            pvVar6 = (void *)*piVar9;
          }
          if (pvVar6 == (void *)0x0) {
            return;
          }
        }
        if ((pvVar6 != (void *)0x0) && (*(int *)((int)pvVar6 + 0x9c) != 0)) {
          CGeneralVolume__Helper_00506010(pvVar6);
        }
      }
    }
  }
  return;
}

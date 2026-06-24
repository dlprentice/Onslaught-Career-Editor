/* address: 0x005068f0 */
/* name: CEngine__AdvanceProgressIfAnySlotAssigned */
/* signature: void __fastcall CEngine__AdvanceProgressIfAnySlotAssigned(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CEngine__AdvanceProgressIfAnySlotAssigned(int param_1)

{
  int iVar1;
  int *piVar2;

  iVar1 = 1;
  piVar2 = (int *)(*(int *)(param_1 + 0xa4) + 0x10);
  do {
    if (*piVar2 != -1) {
      if (*(float *)(param_1 + 0x60) < _DAT_005db358) {
        *(float *)(param_1 + 0x60) =
             *(float *)(*(int *)(param_1 + 0xa4) + 8) + *(float *)(param_1 + 0x60);
      }
      return;
    }
    iVar1 = iVar1 + 1;
    piVar2 = piVar2 + 1;
  } while (iVar1 < 5);
  return;
}

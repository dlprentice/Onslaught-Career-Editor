/* address: 0x00412570 */
/* name: CBattleEngine__IsIndexedEntryUsable */
/* signature: int __fastcall CBattleEngine__IsIndexedEntryUsable(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CBattleEngine__IsIndexedEntryUsable(void *param_1)

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
    do {
      if (iVar3 == *(int *)((int)param_1 + 0x10)) {
        if (iVar2 == 0) {
          return 0;
        }
        iVar3 = *(int *)((int)param_1 + 0x18);
        iVar2 = *(int *)(*(int *)(iVar2 + 0xa4) + 0x24);
        if (*(int *)(iVar3 + 0x55c + iVar2 * 4) == 0) {
          if (*(float *)(iVar3 + 0x52c + iVar2 * 4) <= _DAT_005d856c) {
            return 0;
          }
          return 1;
        }
        if (*(float *)(*(int *)(iVar3 + 0x4b0) + 0x88 + iVar2 * 4) <=
            *(float *)(iVar3 + 0x52c + iVar2 * 4)) {
          return 0;
        }
        if (*(int *)(iVar3 + 0x544 + iVar2 * 4) != 0) {
          return 0;
        }
        return 1;
      }
      iVar3 = iVar3 + 1;
      piVar1 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar1;
      }
    } while (iVar2 != 0);
  }
  return 0;
}

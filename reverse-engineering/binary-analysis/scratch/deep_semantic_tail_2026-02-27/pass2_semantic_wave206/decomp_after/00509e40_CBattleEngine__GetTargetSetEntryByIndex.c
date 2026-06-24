/* address: 0x00509e40 */
/* name: CBattleEngine__GetTargetSetEntryByIndex */
/* signature: int __cdecl CBattleEngine__GetTargetSetEntryByIndex(int param_1) */


int __cdecl CBattleEngine__GetTargetSetEntryByIndex(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  iVar3 = 0;
  piVar1 = (int *)*DAT_008553ec;
  DAT_008553ec[2] = (int)piVar1;
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  while( true ) {
    if (iVar2 == 0) {
      return 0;
    }
    if (iVar3 == param_1) break;
    iVar3 = iVar3 + 1;
    piVar1 = *(int **)(DAT_008553ec[2] + 4);
    DAT_008553ec[2] = (int)piVar1;
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
  }
  return iVar2;
}

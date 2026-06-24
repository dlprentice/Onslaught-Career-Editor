/* address: 0x00472ad0 */
/* name: UISelectionList__AdvanceToNextEnabledWithWrap */
/* signature: void __fastcall UISelectionList__AdvanceToNextEnabledWithWrap(int param_1) */


void __fastcall UISelectionList__AdvanceToNextEnabledWithWrap(int param_1)

{
  int iVar1;
  int iVar2;
  bool bVar3;
  int iVar4;

  if (*(char *)(param_1 + 0x1c) != '\0') {
    iVar4 = 5;
    if (*(int *)(param_1 + 0x44) == 2) {
      iVar4 = 3;
    }
    iVar1 = *(int *)(param_1 + 0x20);
    *(int *)(param_1 + 0x20) = iVar1 + 1;
    bVar3 = false;
    while ((iVar2 = *(int *)(param_1 + 0x20), iVar4 < iVar2 ||
           ((*(int *)(param_1 + 0x2c + iVar2 * 4) == 0 && (!bVar3))))) {
      *(int *)(param_1 + 0x20) = iVar2 + 1;
      if (iVar4 < iVar2 + 1) {
        bVar3 = true;
        *(int *)(param_1 + 0x20) = iVar1;
      }
    }
    if (iVar4 < *(int *)(param_1 + 0x20)) {
      *(int *)(param_1 + 0x20) = iVar4;
    }
    if (*(int *)(param_1 + 0x20) != iVar1) {
      CFrontEnd__PlaySound(0);
    }
  }
  return;
}

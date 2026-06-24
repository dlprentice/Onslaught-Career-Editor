/* address: 0x005214d0 */
/* name: CFEPVirtualKeyboard__IsSpecialKeyBlocked */
/* signature: int __fastcall CFEPVirtualKeyboard__IsSpecialKeyBlocked(int param_1) */


int __fastcall CFEPVirtualKeyboard__IsSpecialKeyBlocked(int param_1)

{
  short *psVar1;
  short sVar2;
  int iVar3;

  psVar1 = (short *)(param_1 + 0x54 +
                    (*(int *)(param_1 + 0x6ec) +
                    (*(int *)(param_1 + 0x6e4) * 5 + *(int *)(param_1 + 0x6e8)) * 0xe) * 8);
  if ((*(int *)(param_1 + 0x6e4) == 1) && ((sVar2 = *psVar1, sVar2 == 4 || (sVar2 == 5)))) {
    return 1;
  }
  if (*psVar1 == 9) {
    if (*(short *)(param_1 + 4) == 0) {
      return 1;
    }
    sVar2 = *(short *)(param_1 + 4);
    iVar3 = param_1 + 4;
    while( true ) {
      if (sVar2 == 0) {
        return 1;
      }
      if (sVar2 != 0x20) break;
      sVar2 = *(short *)(iVar3 + 2);
      iVar3 = iVar3 + 2;
    }
  }
  return 0;
}

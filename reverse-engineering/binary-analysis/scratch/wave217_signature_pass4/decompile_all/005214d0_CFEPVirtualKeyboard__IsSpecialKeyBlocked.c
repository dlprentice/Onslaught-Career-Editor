/* address: 0x005214d0 */
/* name: CFEPVirtualKeyboard__IsSpecialKeyBlocked */
/* signature: int __thiscall CFEPVirtualKeyboard__IsSpecialKeyBlocked(void * this) */


int __thiscall CFEPVirtualKeyboard__IsSpecialKeyBlocked(void *this)

{
  short *psVar1;
  short sVar2;
  int iVar3;

  psVar1 = (short *)((int)this +
                    (*(int *)((int)this + 0x6ec) +
                    (*(int *)((int)this + 0x6e4) * 5 + *(int *)((int)this + 0x6e8)) * 0xe) * 8 +
                    0x54);
  if ((*(int *)((int)this + 0x6e4) == 1) && ((sVar2 = *psVar1, sVar2 == 4 || (sVar2 == 5)))) {
    return 1;
  }
  if (*psVar1 == 9) {
    if (*(short *)((int)this + 4) == 0) {
      return 1;
    }
    sVar2 = *(short *)((int)this + 4);
    iVar3 = (int)this + 4;
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

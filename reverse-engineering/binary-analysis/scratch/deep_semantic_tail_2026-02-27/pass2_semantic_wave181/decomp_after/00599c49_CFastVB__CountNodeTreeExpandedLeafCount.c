/* address: 0x00599c49 */
/* name: CFastVB__CountNodeTreeExpandedLeafCount */
/* signature: int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, int param_1, int param_2) */


int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_EDI;
  int iVar2;

  iVar2 = 0;
  if (param_1 == 0) {
    return 0;
  }
  do {
    if (*(int *)(param_1 + 4) != 1) break;
    iVar1 = CFastVB__CountNodeTreeExpandedLeafCount(this,*(int *)(param_1 + 8),unaff_EDI);
    param_1 = *(int *)(param_1 + 0xc);
    iVar2 = iVar2 + iVar1;
  } while (param_1 != 0);
  if (param_1 == 0) {
    return iVar2;
  }
  iVar1 = *(int *)(param_1 + 4);
  if (iVar1 == 5) {
    iVar1 = *(int *)(param_1 + 0x18);
  }
  else {
    if (iVar1 == 7) {
      iVar1 = CFastVB__CountNodeTreeExpandedLeafCount(this,*(int *)(param_1 + 0x10),unaff_EDI);
      iVar1 = iVar1 * *(int *)(param_1 + 0x14);
      goto LAB_00599cca;
    }
    if (iVar1 == 8) {
      iVar1 = *(int *)(param_1 + 0x1c) * *(int *)(param_1 + 0x18);
      goto LAB_00599cca;
    }
    if (iVar1 != 10) {
      CFastVB__SetParseErrorAndMarkStateDirty((int)this,0,0,0x5ed3bc);
      return 0;
    }
    iVar1 = *(int *)(param_1 + 0x20);
  }
  iVar1 = CFastVB__CountNodeTreeExpandedLeafCount(this,iVar1,unaff_EDI);
LAB_00599cca:
  return iVar1 + iVar2;
}

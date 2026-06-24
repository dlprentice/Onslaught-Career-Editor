/* address: 0x00599bd7 */
/* name: CFastVB__Helper_00599bd7 */
/* signature: int __thiscall CFastVB__Helper_00599bd7(void * this, int param_1, int param_2) */


int __thiscall CFastVB__Helper_00599bd7(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_EDI;

  while( true ) {
    while( true ) {
      while( true ) {
        while( true ) {
          if (param_1 == 0) {
            return 1;
          }
          iVar1 = *(int *)(param_1 + 4);
          if (iVar1 != 1) break;
          iVar1 = CFastVB__Helper_00599bd7(this,*(int *)(param_1 + 8),unaff_EDI);
          if (iVar1 == 0) {
            return 0;
          }
          param_1 = *(int *)(param_1 + 0xc);
        }
        if (iVar1 != 5) break;
        param_1 = *(int *)(param_1 + 0x18);
      }
      if (iVar1 != 7) break;
      param_1 = *(int *)(param_1 + 0x10);
    }
    if (iVar1 == 8) break;
    if (iVar1 != 10) {
      CFastVB__SetParseErrorAndMarkStateDirty((int)this,0,0,0x5ed3bc);
      return 0;
    }
    param_1 = *(int *)(param_1 + 0x20);
  }
  if (*(int *)(param_1 + 0x10) < 0) {
    return 0;
  }
  if (2 < *(int *)(param_1 + 0x10)) {
    return 0;
  }
  return 1;
}

/* address: 0x00599b69 */
/* name: CFastVB__NodeTreeHasBitFlag0x200 */
/* signature: uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, int param_1, int param_2) */


uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void *this,int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int unaff_EDI;

  while( true ) {
    while( true ) {
      while( true ) {
        while( true ) {
          if (param_1 == 0) {
            return 0;
          }
          iVar1 = *(int *)(param_1 + 4);
          if (iVar1 != 1) break;
          uVar2 = CFastVB__NodeTreeHasBitFlag0x200(this,*(int *)(param_1 + 8),unaff_EDI);
          if (uVar2 != 0) {
            return 1;
          }
          param_1 = *(int *)(param_1 + 0xc);
        }
        if (iVar1 != 5) break;
        param_1 = *(int *)(param_1 + 0x18);
      }
      if (iVar1 != 7) break;
      param_1 = *(int *)(param_1 + 0x10);
    }
    if (iVar1 == 8) {
      return *(uint *)(param_1 + 0x20) & 0x200;
    }
    if (iVar1 != 10) break;
    param_1 = *(int *)(param_1 + 0x20);
  }
  CFastVB__SetParseErrorAndMarkStateDirty((int)this,0,0,0x5ed3bc);
  return 0;
}

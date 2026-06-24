/* address: 0x00599d80 */
/* name: CFastVB__Helper_00599d80 */
/* signature: int __thiscall CFastVB__Helper_00599d80(void * this, void * param_1, int param_2, uint param_3, int param_4) */


int __thiscall
CFastVB__Helper_00599d80(void *this,void *param_1,int param_2,uint param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int unaff_EDI;

  while( true ) {
    while( true ) {
      while( true ) {
        while( true ) {
          if (param_1 == (void *)0x0) {
            return -0x7fffbffb;
          }
          iVar1 = *(int *)((int)param_1 + 4);
          if (iVar1 != 1) break;
          uVar2 = CFastVB__Helper_00599c49(this,*(int *)((int)param_1 + 8),unaff_EDI);
          if ((uint)param_2 < uVar2) {
            param_1 = *(void **)((int)param_1 + 8);
          }
          else {
            param_1 = *(void **)((int)param_1 + 0xc);
            param_2 = param_2 - uVar2;
          }
        }
        if (iVar1 != 5) break;
        param_1 = *(void **)((int)param_1 + 0x18);
      }
      if (iVar1 != 7) break;
      param_1 = *(void **)((int)param_1 + 0x10);
      uVar2 = CFastVB__Helper_00599c49(this,(int)param_1,unaff_EDI);
      if (uVar2 == 0) {
        return -0x7fffbffb;
      }
      param_2 = (uint)param_2 % uVar2;
    }
    if (iVar1 == 8) {
      iVar1 = *(int *)((int)param_1 + 0x10);
      if (((iVar1 == 0) || (iVar1 == 1)) || (iVar1 == 2)) {
        *(undefined4 *)(param_3 + 0x10) = 0;
      }
      else if (iVar1 == 3) {
        *(undefined4 *)(param_3 + 0x10) = 3;
      }
      *(undefined4 *)(param_3 + 0x14) = *(undefined4 *)((int)param_1 + 0x14);
      *(undefined4 *)(param_3 + 0x18) = 1;
      *(undefined4 *)(param_3 + 0x1c) = 1;
      *(uint *)(param_3 + 0x20) = *(uint *)((int)param_1 + 0x20) & 0x200;
      return 0;
    }
    if (iVar1 != 10) break;
    param_1 = *(void **)((int)param_1 + 0x20);
  }
  CFastVB__SetParseErrorAndMarkStateDirty((int)this,0,0,0x5ed3bc);
  return 0;
}

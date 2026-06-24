/* address: 0x004cb0b0 */
/* name: CUnit__Helper_004cb0b0 */
/* signature: void __thiscall CUnit__Helper_004cb0b0(void * this, int param_1, int param_2) */


void __thiscall CUnit__Helper_004cb0b0(void *this,int param_1,int param_2)

{
  int iVar1;

  iVar1 = *(int *)((int)this + 4);
  if (iVar1 != 0) {
    if (param_1 != 1) {
      *(undefined2 *)(iVar1 + 0xb4) = 2;
      *(undefined4 *)((int)this + 4) = 0;
      return;
    }
    *(undefined2 *)(iVar1 + 0xb4) = 1;
  }
  *(undefined4 *)((int)this + 4) = 0;
  return;
}

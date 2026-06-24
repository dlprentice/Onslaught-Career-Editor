/* address: 0x00570870 */
/* name: CFastVB__Helper_00570870 */
/* signature: void __thiscall CFastVB__Helper_00570870(void * this, int param_1, int param_2) */


void __thiscall CFastVB__Helper_00570870(void *this,int param_1,int param_2)

{
  if (-1 < *(int *)((int)this + 0x20)) {
    *(int *)(param_1 + 0x14) = *(int *)((int)this + 0x20);
    *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)((int)this + 0x1c);
    return;
  }
  *(undefined4 *)(param_1 + 0x14) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)((int)this + 0x1c);
  return;
}

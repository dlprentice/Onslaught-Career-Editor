/* address: 0x004cdbe0 */
/* name: CEngine__Unk_004cdbe0 */
/* signature: void __thiscall CEngine__Unk_004cdbe0(void * this, int param_1, int param_2) */


void __thiscall CEngine__Unk_004cdbe0(void *this,int param_1,int param_2)

{
  if (*(int *)(param_1 + 0x3c) == 0) {
    *(undefined4 *)((int)this + 4) = *(undefined4 *)(param_1 + 0x40);
  }
  else {
    *(undefined4 *)(*(int *)(param_1 + 0x3c) + 0x40) = *(undefined4 *)(param_1 + 0x40);
  }
  if (*(int *)(param_1 + 0x40) == 0) {
    *(undefined4 *)((int)this + 8) = *(undefined4 *)(param_1 + 0x3c);
    *(undefined4 *)(param_1 + 0x3c) = 0;
    *(undefined4 *)(param_1 + 0x40) = 0;
    return;
  }
  *(undefined4 *)(*(int *)(param_1 + 0x40) + 0x3c) = *(undefined4 *)(param_1 + 0x3c);
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined4 *)(param_1 + 0x40) = 0;
  return;
}

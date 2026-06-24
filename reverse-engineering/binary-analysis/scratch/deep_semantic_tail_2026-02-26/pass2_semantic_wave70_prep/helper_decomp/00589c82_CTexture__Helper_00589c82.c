/* address: 0x00589c82 */
/* name: CTexture__Helper_00589c82 */
/* signature: int __thiscall CTexture__Helper_00589c82(void * this, int param_1, int param_2, int param_3) */


int __thiscall CTexture__Helper_00589c82(void *this,int param_1,int param_2,int param_3)

{
  int *piVar1;

  *(int *)(*(int *)((int)this + 0x54) + 0x1c) = param_1;
  if (*(int *)((int)this + 0x60) != 0xc) {
    piVar1 = (int *)(*(int *)((int)this + 0x54) + 0x1c);
    *piVar1 = *piVar1 + -1;
  }
  if (param_2 != 0) {
    *(int *)(*(int *)((int)this + 0x54) + 0x18) = param_2;
  }
  return 0;
}

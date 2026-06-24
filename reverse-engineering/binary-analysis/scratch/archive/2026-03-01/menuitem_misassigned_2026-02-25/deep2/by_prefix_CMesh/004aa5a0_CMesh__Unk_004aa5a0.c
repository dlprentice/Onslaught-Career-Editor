/* address: 0x004aa5a0 */
/* name: CMesh__Unk_004aa5a0 */
/* signature: int __thiscall CMesh__Unk_004aa5a0(void * this, int param_1, int param_2) */


int __thiscall CMesh__Unk_004aa5a0(void *this,int param_1,int param_2)

{
  int iVar1;

  iVar1 = *(int *)((int)this + 0x1c);
  if (iVar1 <= param_1) {
    do {
      this = *(void **)((int)this + 8);
      if (this == (void *)0x0) {
        return 0;
      }
      param_1 = param_1 - iVar1;
      iVar1 = *(int *)((int)this + 0x1c);
    } while (iVar1 <= param_1);
  }
  return *(int *)(param_1 * 0x150 + 0x40 + *(int *)((int)this + 0x20));
}

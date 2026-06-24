/* address: 0x004aa680 */
/* name: CMesh__Unk_004aa680 */
/* signature: int __thiscall CMesh__Unk_004aa680(void * this, int param_1, int param_2) */


int __thiscall CMesh__Unk_004aa680(void *this,int param_1,int param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)((int)this + 0x18);
  iVar2 = 0;
  if (0 < *(int *)((int)this + 0x14)) {
    do {
      if (*(int *)(iVar1 + 0x10) == param_1) {
        return iVar1;
      }
      iVar1 = iVar1 + 0x24;
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 0x14));
  }
  return 0;
}

/* address: 0x004aa8a0 */
/* name: CMesh__Unk_004aa8a0 */
/* signature: int __thiscall CMesh__Unk_004aa8a0(void * this, int param_1, void * param_2) */


int __thiscall CMesh__Unk_004aa8a0(void *this,int param_1,void *param_2)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)((int)this + 0x15c)) {
    do {
      iVar1 = stricmp((char *)(*(int *)(*(int *)((int)this + 0x160) + iVar2 * 4) + 0xdc),
                      (char *)param_1);
      if (iVar1 == 0) {
        return *(int *)(*(int *)((int)this + 0x160) + iVar2 * 4);
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 0x15c));
  }
  return 0;
}

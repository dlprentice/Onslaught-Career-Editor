/* address: 0x004aa820 */
/* name: CMesh__Unk_004aa820 */
/* signature: int __thiscall CMesh__Unk_004aa820(void * this, int param_1, void * param_2, int param_3) */


int __thiscall CMesh__Unk_004aa820(void *this,int param_1,void *param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;

  do {
    iVar2 = 0;
    if (0 < *(int *)((int)this + 0x1c)) {
      iVar3 = 0;
      do {
        iVar1 = stricmp((char *)(*(int *)((int)this + 0x20) + 0x4c + iVar3),(char *)param_1);
        if ((iVar1 == 0) && (*(void **)(*(int *)((int)this + 0x20) + 0x14c + iVar3) == param_2)) {
          return *(int *)(iVar2 * 0x150 + 0x40 + *(int *)((int)this + 0x20));
        }
        iVar2 = iVar2 + 1;
        iVar3 = iVar3 + 0x150;
      } while (iVar2 < *(int *)((int)this + 0x1c));
    }
    this = *(void **)((int)this + 8);
    if (this == (void *)0x0) {
      return 0;
    }
  } while( true );
}

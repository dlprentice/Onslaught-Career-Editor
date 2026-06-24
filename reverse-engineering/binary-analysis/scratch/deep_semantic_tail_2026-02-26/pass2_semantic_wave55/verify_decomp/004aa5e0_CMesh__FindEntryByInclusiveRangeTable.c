/* address: 0x004aa5e0 */
/* name: CMesh__FindEntryByInclusiveRangeTable */
/* signature: int __thiscall CMesh__FindEntryByInclusiveRangeTable(void * this, int param_1, int param_2) */


int __thiscall CMesh__FindEntryByInclusiveRangeTable(void *this,int param_1,int param_2)

{
  int *piVar1;
  int iVar2;

  do {
    iVar2 = 0;
    if (0 < *(int *)((int)this + 0xc)) {
      piVar1 = (int *)(*(int *)((int)this + 0x10) + 8);
      do {
        if ((piVar1[-1] <= param_1) && (param_1 <= *piVar1)) {
          return *(int *)(*(int *)((int)this + 0x10) + iVar2 * 0xc);
        }
        iVar2 = iVar2 + 1;
        piVar1 = piVar1 + 3;
      } while (iVar2 < *(int *)((int)this + 0xc));
    }
    this = *(void **)((int)this + 8);
    if (this == (void *)0x0) {
      return 0;
    }
  } while( true );
}

/* address: 0x00444580 */
/* name: CDestroyableSegment__Unk_00444580 */
/* signature: void __thiscall CDestroyableSegment__Unk_00444580(void * this, int param_1, int param_2) */


void __thiscall CDestroyableSegment__Unk_00444580(void *this,int param_1,int param_2)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)((int)this + 8)) {
    do {
      iVar1 = *(int *)(*(int *)((int)this + 4) + iVar2 * 4);
      if (iVar1 != 0) {
        *(int *)(iVar1 + 0xc) = param_1;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 8));
  }
  return;
}

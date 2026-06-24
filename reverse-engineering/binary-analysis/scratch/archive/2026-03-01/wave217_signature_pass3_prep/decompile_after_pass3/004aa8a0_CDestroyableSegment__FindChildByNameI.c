/* address: 0x004aa8a0 */
/* name: CDestroyableSegment__FindChildByNameI */
/* signature: void * __thiscall CDestroyableSegment__FindChildByNameI(void * this, void * child_name, void * unused_ctx) */


void * __thiscall
CDestroyableSegment__FindChildByNameI(void *this,void *child_name,void *unused_ctx)

{
  int iVar1;
  int iVar2;

  iVar2 = 0;
  if (0 < *(int *)((int)this + 0x15c)) {
    do {
      iVar1 = stricmp((char *)(*(int *)(*(int *)((int)this + 0x160) + iVar2 * 4) + 0xdc),child_name)
      ;
      if (iVar1 == 0) {
        return *(void **)(*(int *)((int)this + 0x160) + iVar2 * 4);
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 0x15c));
  }
  return (void *)0x0;
}

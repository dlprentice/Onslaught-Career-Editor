/* address: 0x00444620 */
/* name: CExplosionInitThing__Unk_00444620 */
/* signature: void __thiscall CExplosionInitThing__Unk_00444620(void * this, int param_1, int param_2) */


void __thiscall CExplosionInitThing__Unk_00444620(void *this,int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  double dVar3;

  iVar2 = 0;
  if (0 < *(int *)((int)this + 8)) {
    do {
      iVar1 = *(int *)(*(int *)((int)this + 4) + iVar2 * 4);
      if (iVar1 != 0) {
        *(int *)(iVar1 + 0x1c) = param_1;
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 8));
  }
  if (*(void **)((int)this + 0xc) != (void *)0x0) {
    dVar3 = CDestroyableSegment__Helper_00442890(*(void **)((int)this + 0xc));
    *(float *)((int)this + 0x18) = (float)dVar3;
  }
  return;
}

/* address: 0x004beea0 */
/* name: CExplosionInitThing__Unk_004beea0 */
/* signature: void __thiscall CExplosionInitThing__Unk_004beea0(void * this, int param_1, void * param_2) */


void __thiscall CExplosionInitThing__Unk_004beea0(void *this,int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  float unaff_EDI;
  int iVar3;

  iVar2 = *(int *)((int)this + 0xc);
  do {
    iVar3 = iVar2;
    iVar2 = iVar3 + -1;
    if (iVar2 < 0) break;
    iVar1 = CExplosionInitThing__Unk_004bc510
                      ((void *)param_1,
                       (uint)*(byte *)(*(int *)((int)this + 0x10) + -1 + *(int *)((int)this + 0xc)),
                       (uint)*(byte *)(*(int *)((int)this + 0x18) + -1 + *(int *)((int)this + 0xc)),
                       (uint)*(byte *)(*(int *)((int)this + 0x10) + iVar2),
                       (uint)*(byte *)(*(int *)((int)this + 0x18) + iVar2),unaff_EDI);
  } while (iVar1 == 0);
  iVar3 = iVar3 + 1;
  iVar2 = *(int *)((int)this + 0xc) + -1;
  if (iVar3 < iVar2) {
    iVar3 = (iVar2 - iVar3) + -1;
    if (iVar2 < *(int *)((int)this + 0xc)) {
      do {
        *(undefined1 *)(iVar2 + (*(int *)((int)this + 0x10) - iVar3)) =
             *(undefined1 *)(*(int *)((int)this + 0x10) + iVar2);
        *(undefined1 *)(iVar2 + (*(int *)((int)this + 0x18) - iVar3)) =
             *(undefined1 *)(*(int *)((int)this + 0x18) + iVar2);
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)((int)this + 0xc));
    }
    *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) - iVar3;
  }
  iVar2 = 0;
  if (0 < *(int *)((int)this + 0xc)) {
    do {
      iVar3 = CExplosionInitThing__Unk_004bc510
                        ((void *)param_1,(uint)**(byte **)((int)this + 0x10),
                         (uint)**(byte **)((int)this + 0x18),
                         (uint)(*(byte **)((int)this + 0x10))[iVar2],
                         (uint)(*(byte **)((int)this + 0x18))[iVar2],unaff_EDI);
      if (iVar3 != 0) break;
      iVar2 = iVar2 + 1;
    } while (iVar2 < *(int *)((int)this + 0xc));
  }
  iVar3 = iVar2 + -2;
  if (0 < iVar3) {
    iVar2 = iVar2 + -3;
    if (iVar3 < *(int *)((int)this + 0xc)) {
      do {
        *(undefined1 *)((*(int *)((int)this + 0x10) - iVar2) + iVar3) =
             *(undefined1 *)(*(int *)((int)this + 0x10) + iVar3);
        *(undefined1 *)((*(int *)((int)this + 0x18) - iVar2) + iVar3) =
             *(undefined1 *)(*(int *)((int)this + 0x18) + iVar3);
        iVar3 = iVar3 + 1;
      } while (iVar3 < *(int *)((int)this + 0xc));
    }
    *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) - iVar2;
  }
  return;
}

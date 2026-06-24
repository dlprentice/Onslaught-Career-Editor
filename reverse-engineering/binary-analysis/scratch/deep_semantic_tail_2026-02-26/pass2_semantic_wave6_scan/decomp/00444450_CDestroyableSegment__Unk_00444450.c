/* address: 0x00444450 */
/* name: CDestroyableSegment__Unk_00444450 */
/* signature: void __thiscall CDestroyableSegment__Unk_00444450(void * this, int param_1, int param_2, int param_3) */


void __thiscall CDestroyableSegment__Unk_00444450(void *this,int param_1,int param_2,int param_3)

{
  int *piVar1;
  void *this_00;
  int iVar2;
  void *unaff_EDI;

  piVar1 = *(int **)(*(int *)((int)this + 0x10) + 0x30);
  if (piVar1 != (int *)0x0) {
    this_00 = (void *)(**(code **)(*piVar1 + 0x24))();
    if (this_00 != (void *)0x0) {
      iVar2 = CDestroyableSegment__Helper_004aa8a0(this_00,param_1,unaff_EDI);
      if ((iVar2 != 0) &&
         (iVar2 = *(int *)(*(int *)((int)this + 4) + *(int *)(iVar2 + 0x88) * 4), iVar2 != 0)) {
        *(int *)(iVar2 + 0xc) = param_2;
        return;
      }
      CConsole__Printf(&DAT_0066f580,s_FATAL_ERROR__Could_not_find_segm_0062864c);
    }
  }
  return;
}

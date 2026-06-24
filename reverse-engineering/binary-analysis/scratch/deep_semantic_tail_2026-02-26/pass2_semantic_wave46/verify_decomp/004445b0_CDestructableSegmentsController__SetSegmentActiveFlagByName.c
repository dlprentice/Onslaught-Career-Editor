/* address: 0x004445b0 */
/* name: CDestructableSegmentsController__SetSegmentActiveFlagByName */
/* signature: void __thiscall CDestructableSegmentsController__SetSegmentActiveFlagByName(void * this, int param_1, int param_2, int param_3) */


void __thiscall
CDestructableSegmentsController__SetSegmentActiveFlagByName
          (void *this,int param_1,int param_2,int param_3)

{
  int *piVar1;
  void *this_00;
  int iVar2;
  void *unaff_EDI;
  double dVar3;

  piVar1 = *(int **)(*(int *)((int)this + 0x10) + 0x30);
  if (piVar1 != (int *)0x0) {
    this_00 = (void *)(**(code **)(*piVar1 + 0x24))();
    if (this_00 != (void *)0x0) {
      iVar2 = CDestroyableSegment__Helper_004aa8a0(this_00,param_1,unaff_EDI);
      if ((iVar2 == 0) ||
         (iVar2 = *(int *)(*(int *)((int)this + 4) + *(int *)(iVar2 + 0x88) * 4), iVar2 == 0)) {
        CConsole__Printf(&DAT_0066f580,s_FATAL_ERROR__Could_not_find_segm_0062864c);
      }
      else {
        *(int *)(iVar2 + 0x1c) = param_2;
        if (*(void **)((int)this + 0xc) != (void *)0x0) {
          dVar3 = CDestroyableSegment__Helper_00442890(*(void **)((int)this + 0xc));
          *(float *)((int)this + 0x18) = (float)dVar3;
          return;
        }
      }
    }
  }
  return;
}

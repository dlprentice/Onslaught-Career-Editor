/* address: 0x00444f20 */
/* name: CUnitAI__CanUseIndexedSegmentEntry */
/* signature: bool __thiscall CUnitAI__CanUseIndexedSegmentEntry(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool __thiscall CUnitAI__CanUseIndexedSegmentEntry(void *this,int param_1,int param_2)

{
  float fVar1;
  int *piVar2;
  float fVar3;
  int iVar4;
  double dVar5;

  piVar2 = *(int **)(*(int *)((int)this + 4) + param_1 * 4);
  if (piVar2 == (int *)0x0) {
    piVar2 = *(int **)(*(int *)((int)this + 0x10) + 0x30);
    if (piVar2 == (int *)0x0) {
      return true;
    }
    iVar4 = (**(code **)(*piVar2 + 0x24))();
    if ((((iVar4 != 0) && (iVar4 = *(int *)(*(int *)(iVar4 + 0x160) + param_1 * 4), iVar4 != 0)) &&
        (*(int *)(iVar4 + 0x8c) == 5)) &&
       ((*(int *)(iVar4 + 0x98) != 0 &&
        (iVar4 = *(int *)(*(int *)((int)this + 4) + *(int *)(*(int *)(iVar4 + 0x98) + 0x88) * 4),
        iVar4 != 0)))) {
      return *(int *)(iVar4 + 0x38) == 0;
    }
    return true;
  }
  if (*(int *)((int)this + 0x24) == 0) {
    iVar4 = (**(code **)(*piVar2 + 0x14))();
    if ((iVar4 == 0) && (piVar2[0x10] == 1)) {
      iVar4 = CDestructableSegmentsController__AreCoreChildrenDestroyed(*(int *)((int)this + 0xc));
      if (iVar4 != 1) {
        fVar1 = *(float *)((int)this + 0x18);
        fVar3 = (float)_DAT_005db0a0;
        dVar5 = CDestroyableSegment__Helper_00442890(*(void **)((int)this + 0xc));
        if ((double)(fVar1 * fVar3) <= dVar5) goto LAB_00444ffa;
      }
      return false;
    }
  }
LAB_00444ffa:
  return piVar2[0xe] == 0;
}

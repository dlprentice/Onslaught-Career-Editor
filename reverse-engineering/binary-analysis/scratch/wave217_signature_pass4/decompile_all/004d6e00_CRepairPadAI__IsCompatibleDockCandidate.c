/* address: 0x004d6e00 */
/* name: CRepairPadAI__IsCompatibleDockCandidate */
/* signature: int __thiscall CRepairPadAI__IsCompatibleDockCandidate(void * this, void * candidate_unit, int unused_ctx) */


int __thiscall
CRepairPadAI__IsCompatibleDockCandidate(void *this,void *candidate_unit,int unused_ctx)

{
  int iVar1;

  iVar1 = CRepairPadAI__IsWithinRepairBounds(candidate_unit);
  if ((iVar1 != 0) && (iVar1 = CRepairPadAI__HasAnySlotBelowThreshold(candidate_unit), iVar1 == 0))
  {
    return 0;
  }
  iVar1 = *(int *)((int)candidate_unit + 0x138);
  if (iVar1 == 0) {
    iVar1 = *(int *)(*(int *)((int)this + 8) + 0x138);
    if ((iVar1 != 0) && (iVar1 != 6)) {
      return 0;
    }
  }
  else {
    if (iVar1 == 1) {
      iVar1 = *(int *)(*(int *)((int)this + 8) + 0x138);
      if (iVar1 == 1) {
        return 1;
      }
      iVar1 = iVar1 + -6;
    }
    else {
      if (iVar1 != 6) {
        return 0;
      }
      iVar1 = *(int *)(*(int *)((int)this + 8) + 0x138);
      if (iVar1 == 1) {
        return 1;
      }
    }
    if (iVar1 != 0) {
      return 0;
    }
  }
  return 1;
}

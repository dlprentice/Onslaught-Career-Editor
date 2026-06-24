/* address: 0x0040c5e0 */
/* name: CRepairPadAI__HasAnySlotBelowThreshold */
/* signature: int __thiscall CRepairPadAI__HasAnySlotBelowThreshold(void * this) */


int __thiscall CRepairPadAI__HasAnySlotBelowThreshold(void *this)

{
  float *pfVar1;
  int iVar2;

  iVar2 = 0;
  pfVar1 = (float *)((int)this + 0x52c);
  while ((pfVar1[0xc] != 0.0 ||
         (*(float *)(*(int *)((int)this + 0x4b0) + (-0x4a4 - (int)this) + (int)pfVar1) <= *pfVar1)))
  {
    iVar2 = iVar2 + 1;
    pfVar1 = pfVar1 + 1;
    if (5 < iVar2) {
      return 0;
    }
  }
  return 1;
}

/* address: 0x004daab0 */
/* name: CEngine__SetProjectileTargetReader */
/* signature: void __thiscall CEngine__SetProjectileTargetReader(void * this, void * param_1, void * param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CEngine__SetProjectileTargetReader(void *this,void *param_1,void *param_2,int param_3)

{
  void *this_00;
  int unaff_ESI;

  if ((param_1 != (void *)0x0) &&
     ((*(int *)(*(int *)((int)this + 0xf0) + 0x48) != 0 ||
      (*(float *)(*(int *)((int)this + 0xf0) + 0x1c) < _DAT_005d856c)))) {
    if (param_2 != (void *)0x0) {
      this_00 = *(void **)((int)this + 0xec);
      if ((this_00 != (void *)0x0) && ((*(byte *)((int)this_00 + 0x34) & 8) != 0)) {
        CMonitor__RemoveActiveReaderById(this_00,*(int *)((int)this + 0xe8),unaff_ESI);
      }
      if ((*(int *)((int)this + 0xe8) != 0) &&
         ((*(byte *)(*(int *)((int)this + 0xe8) + 0x34) & 8) != 0)) {
        CSPtrSet__Remove(&DAT_008551a0,this);
      }
      CGenericActiveReader__SetReader((void *)((int)this + 0xe8),(void *)0x0);
    }
    CGenericActiveReader__SetReader((void *)((int)this + 0xe8),param_1);
    if ((*(byte *)((int)param_1 + 0x34) & 8) != 0) {
      CSPtrSet__AddToHead(&DAT_008551a0,this);
    }
  }
  return;
}

/* address: 0x004fd5e0 */
/* name: VFuncSlot_26_004fd5e0 */
/* signature: int __thiscall VFuncSlot_26_004fd5e0(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall VFuncSlot_26_004fd5e0(void *this,int param_1,int param_2)

{
  int iVar1;
  int unaff_EDI;
  double dVar2;
  float fVar3;

  if (*(void **)((int)this + 0x170) == (void *)0x0) {
    return *(int *)((int)this + 0x210);
  }
  dVar2 = CDestroyableSegment__Unk_004442d0(*(void **)((int)this + 0x170),param_1,unaff_EDI);
  if ((double)DAT_00672fd0 - dVar2 < (double)_DAT_005d8568) {
    dVar2 = CDestroyableSegment__Unk_00444300(*(void **)((int)this + 0x170),param_1,unaff_EDI);
    fVar3 = (float)dVar2;
    (**(code **)(*(int *)((int)this + -8) + 0x1ac))();
    *(undefined4 *)((int)this + 0x214) = 10;
    dVar2 = CDestroyableSegment__Unk_004442d0(*(void **)((int)this + 0x170),param_1,(int)fVar3);
    iVar1 = *(int *)((int)this + 0x210) -
            (int)(longlong)ROUND(((double)DAT_00672fd0 - dVar2) * (double)_DAT_005d857c) *
            *(int *)((int)this + 0x214);
    if (-1 < iVar1) {
      if (iVar1 < 0x65) {
        return iVar1;
      }
      return 100;
    }
  }
  return 0;
}

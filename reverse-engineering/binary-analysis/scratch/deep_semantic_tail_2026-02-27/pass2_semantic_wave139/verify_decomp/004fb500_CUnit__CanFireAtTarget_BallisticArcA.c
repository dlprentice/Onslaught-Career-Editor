/* address: 0x004fb500 */
/* name: CUnit__CanFireAtTarget_BallisticArcA */
/* signature: uint __thiscall CUnit__CanFireAtTarget_BallisticArcA(void * this, int param_1, int param_2, int param_3) */


uint __thiscall CUnit__CanFireAtTarget_BallisticArcA(void *this,int param_1,int param_2,int param_3)

{
  int iVar1;
  uint uVar2;
  int unaff_EDI;
  double dVar3;

  iVar1 = CUnit__Unk_004fb670(this,param_1,unaff_EDI);
  if (iVar1 != 0) {
    return 0;
  }
  if (*(int *)((int)this + 0x140) != 0) {
    dVar3 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(param_1 + 0x1c));
    if ((double)DAT_006fbdfc < dVar3) {
      dVar3 = (double)DAT_006fbdfc;
    }
    dVar3 = dVar3 - (double)*(float *)(param_1 + 0x24);
    iVar1 = *(int *)((int)*(void **)((int)this + 0x140) + 0xa0);
    if (((double)*(float *)(iVar1 + 0x6c) <= dVar3) && (dVar3 <= (double)*(float *)(iVar1 + 0x70)))
    {
      uVar2 = OID__CanFireAtTarget_BallisticArcA
                        (*(void **)((int)this + 0x140),(void *)param_1,param_2,unaff_EDI);
      return uVar2;
    }
  }
  return (uint)(*(int *)((int)this + 0x144) != 0);
}

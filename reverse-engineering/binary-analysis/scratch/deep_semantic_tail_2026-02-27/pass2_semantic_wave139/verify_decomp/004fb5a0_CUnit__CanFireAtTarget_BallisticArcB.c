/* address: 0x004fb5a0 */
/* name: CUnit__CanFireAtTarget_BallisticArcB */
/* signature: uint __thiscall CUnit__CanFireAtTarget_BallisticArcB(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __thiscall CUnit__CanFireAtTarget_BallisticArcB(void *this,int param_1,void *param_2)

{
  float fVar1;
  int iVar2;
  uint uVar3;
  int unaff_EDI;
  double dVar4;

  iVar2 = CUnit__Unk_004fb670(this,param_1,unaff_EDI);
  if (iVar2 != 0) {
    return 0;
  }
  if (*(int *)((int)this + 0x140) != 0) {
    iVar2 = (**(code **)(*(int *)param_1 + 0x10c))();
    fVar1 = _DAT_005d856c;
    if (iVar2 == 0) {
      dVar4 = CStaticShadows__Helper_0047eb80(0x6fadc8,(void *)(param_1 + 0x1c));
      fVar1 = (float)dVar4;
      if (DAT_006fbdfc < (float)dVar4) {
        fVar1 = DAT_006fbdfc;
      }
      fVar1 = fVar1 - *(float *)(param_1 + 0x24);
    }
    iVar2 = *(int *)((int)*(void **)((int)this + 0x140) + 0xa0);
    if ((*(float *)(iVar2 + 0x6c) <= fVar1) && (fVar1 <= *(float *)(iVar2 + 0x70))) {
      uVar3 = OID__CanFireAtTarget_BallisticArcB
                        (*(void **)((int)this + 0x140),(void *)param_1,unaff_EDI);
      return uVar3;
    }
  }
  return (uint)(*(int *)((int)this + 0x144) != 0);
}

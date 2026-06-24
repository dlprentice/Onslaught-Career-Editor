/* address: 0x004d1f10 */
/* name: CUnitAI__Unk_004d1f10 */
/* signature: void __thiscall CUnitAI__Unk_004d1f10(void * this, void * param_1, void * param_2, int param_3) */


void __thiscall CUnitAI__Unk_004d1f10(void *this,void *param_1,void *param_2,int param_3)

{
  uint uVar1;
  int unaff_EDI;

  if (((*(int *)(*(int *)((int)this + 0x164) + 0x11c) == 0) &&
      (((uVar1 = *(uint *)((int)param_1 + 0x34), (uVar1 & 0x400) == 0 || ((uVar1 & 8) != 0)) ||
       (*(int *)((int)param_1 + 0x138) != *(int *)((int)this + 0x138))))) &&
     (((uVar1 & 0x10) != 0 || ((uVar1 & 0x2100000) != 0)))) {
    if ((uVar1 & 0x10) != 0) {
      (**(code **)(*(int *)param_1 + 0x194))(this);
    }
    CExplosionInitThing__ctor_like_004fd230(this);
    (**(code **)(*(int *)this + 0x38))();
  }
  CThing__Hit_TriggerDieOnDamageMaskA(this,param_1,(int)param_2,unaff_EDI);
  return;
}

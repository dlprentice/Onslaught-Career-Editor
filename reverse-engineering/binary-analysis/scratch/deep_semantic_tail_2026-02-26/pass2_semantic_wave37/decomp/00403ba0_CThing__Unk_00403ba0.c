/* address: 0x00403ba0 */
/* name: CThing__Unk_00403ba0 */
/* signature: void __thiscall CThing__Unk_00403ba0(void * this, void * param_1, int param_2, int param_3) */


void __thiscall CThing__Unk_00403ba0(void *this,void *param_1,int param_2,int param_3)

{
  void *unaff_EDI;

  if (((*(int *)(*(int *)((int)this + 0x164) + 0x11c) == 0) &&
      ((*(byte *)((int)this + 0x2c) & 4) != 0)) &&
     (((*(uint *)((int)param_1 + 0x34) & 0x10) != 0 ||
      ((*(uint *)((int)param_1 + 0x34) & 0x2100000) != 0)))) {
    CExplosionInitThing__ctor_like_004fd230(this);
    (**(code **)(*(int *)this + 0x38))();
  }
  CThing__Helper_004fcc30(this,param_1,param_2,unaff_EDI);
  return;
}

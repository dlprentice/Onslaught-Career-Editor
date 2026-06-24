/* address: 0x00488330 */
/* name: CIBuffer__CreateConfigured */
/* signature: int __thiscall CIBuffer__CreateConfigured(void * this, void * param_1, int param_2, int param_3, int param_4, int param_5) */


int __thiscall
CIBuffer__CreateConfigured(void *this,void *param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;

  *(void **)((int)this + 0xc) = param_1;
  *(int *)((int)this + 0x14) = param_3;
  *(int *)((int)this + 0x10) = param_2;
  *(int *)((int)this + 0x18) = param_4;
  if (param_4 == 1) {
    iVar1 = (**(code **)(*(int *)this + 4))();
  }
  else {
    iVar1 = (**(code **)(*(int *)this + 8))();
  }
  FatalError_LocalizedStringId(-1 < iVar1,0xd2,7);
  return iVar1;
}

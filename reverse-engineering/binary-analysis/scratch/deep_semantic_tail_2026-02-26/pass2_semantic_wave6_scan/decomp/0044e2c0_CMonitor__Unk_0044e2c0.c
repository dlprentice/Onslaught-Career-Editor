/* address: 0x0044e2c0 */
/* name: CMonitor__Unk_0044e2c0 */
/* signature: int __fastcall CMonitor__Unk_0044e2c0(void * param_1) */


int __fastcall CMonitor__Unk_0044e2c0(void *param_1)

{
  void *this;
  int iVar1;
  int iVar2;
  void *unaff_EDI;
  undefined **ppuVar3;

  ppuVar3 = &PTR_DAT_00628e9c;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(this,(int)ppuVar3,unaff_EDI);
  iVar2 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar2 == iVar1) {
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return 0;
}

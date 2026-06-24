/* address: 0x004480c0 */
/* name: CUnitAI__CanContinueDoorWingTransition */
/* signature: int __fastcall CUnitAI__CanContinueDoorWingTransition(void * param_1) */


int __fastcall CUnitAI__CanContinueDoorWingTransition(void *param_1)

{
  int iVar1;
  uint uVar2;
  int unaff_ESI;
  int iVar3;

  if (*(int *)((int)param_1 + 0x294) != 0) {
    return 1;
  }
  iVar1 = CUnitAI__Helper_004fd7e0((int)param_1);
  if (iVar1 == 0) {
    iVar1 = (**(code **)(*(int *)param_1 + 0x144))();
    if (iVar1 != 0) {
      iVar3 = 1;
      iVar1 = (**(code **)(*(int *)param_1 + 0x144))();
      uVar2 = CUnit__Unk_004fb500(param_1,iVar1,iVar3,unaff_ESI);
      if (uVar2 != 0) {
        return 1;
      }
    }
  }
  return 0;
}

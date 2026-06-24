/* address: 0x00598873 */
/* name: CFastVB__CloneNodeChainWithAddRef */
/* signature: int __fastcall CFastVB__CloneNodeChainWithAddRef(void * param_1) */


int __fastcall CFastVB__CloneNodeChainWithAddRef(void *param_1)

{
  void *extraout_EAX;
  int extraout_EAX_00;
  int iVar1;
  undefined4 uVar2;
  int *piVar3;
  int local_8;

  local_8 = 0;
  piVar3 = &local_8;
  while( true ) {
    if (param_1 == (int *)0x0) {
      return local_8;
    }
    if (*(int *)((int)param_1 + 4) != 1) break;
    CFastVB__Helper_00426fd0(0x14);
    if (extraout_EAX == (void *)0x0) {
      iVar1 = 0;
    }
    else {
      CFastVB__Helper_005987d9(extraout_EAX);
      iVar1 = extraout_EAX_00;
    }
    *piVar3 = iVar1;
    if (iVar1 == 0) {
      return local_8;
    }
    *(int *)(iVar1 + 0x10) = *(int *)((int)param_1 + 0x10);
    if (*(int **)((int)param_1 + 8) != (int *)0x0) {
      uVar2 = (**(code **)(**(int **)((int)param_1 + 8) + 8))();
      *(undefined4 *)(*piVar3 + 8) = uVar2;
      if (*(int *)(*piVar3 + 8) == 0) {
        if ((undefined4 *)*piVar3 != (undefined4 *)0x0) {
          (*(code *)**(undefined4 **)*piVar3)(1);
        }
        *piVar3 = 0;
        return local_8;
      }
    }
    param_1 = *(void **)((int)param_1 + 0xc);
    piVar3 = (int *)(*piVar3 + 0xc);
  }
  iVar1 = (**(code **)(*(int *)param_1 + 8))();
  *piVar3 = iVar1;
  return local_8;
}

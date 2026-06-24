/* address: 0x004a4cd0 */
/* name: CMenuItemRange__ProcessInput */
/* signature: undefined CMenuItemRange__ProcessInput(void) */


undefined4 __thiscall
CMenuItemRange__ProcessInput(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int *piVar2;
  int unaff_EDI;

  piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),*(void **)(param_1 + 0x18),unaff_EDI);
  cVar1 = (**(code **)(*piVar2 + 0x20))();
  if (cVar1 != '\0') {
    piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),*(void **)(param_1 + 0x18),unaff_EDI);
    (**(code **)(*piVar2 + 4))(param_2,param_3,param_4);
    return 1;
  }
  return 0;
}

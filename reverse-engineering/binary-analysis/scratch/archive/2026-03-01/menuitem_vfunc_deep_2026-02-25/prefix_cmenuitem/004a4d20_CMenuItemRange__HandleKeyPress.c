/* address: 0x004a4d20 */
/* name: CMenuItemRange__HandleKeyPress */
/* signature: undefined CMenuItemRange__HandleKeyPress(void) */


void __thiscall
CMenuItemRange__HandleKeyPress(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  void *pvVar4;
  int unaff_EDI;

  if (param_3 != 0x2a) {
    if (param_3 != 0x2b) {
      piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),*(void **)(param_1 + 0x18),unaff_EDI
                                         );
      (**(code **)(*piVar2 + 4))(param_2,param_3,param_4);
      return;
    }
    CMenuItemRange__SelectNext();
    return;
  }
  iVar1 = *(int *)(param_1 + 0x18);
  if (iVar1 < 1) {
    if (*(int *)(param_1 + 0x14) < 3) {
      return;
    }
    *(int *)(param_1 + 0x18) = *(int *)(param_1 + 0x14) + -1;
  }
  else {
    *(int *)(param_1 + 0x18) = iVar1 + -1;
  }
  piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),*(void **)(param_1 + 0x18),unaff_EDI);
  iVar3 = (**(code **)(*piVar2 + 0xc))();
  while( true ) {
    if (iVar3 != 0) {
      CFrontEnd__PlaySound(0);
      return;
    }
    pvVar4 = (void *)(*(int *)(param_1 + 0x18) + -1);
    *(void **)(param_1 + 0x18) = pvVar4;
    if ((int)pvVar4 < 0) break;
    piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),pvVar4,unaff_EDI);
    iVar3 = (**(code **)(*piVar2 + 0xc))();
  }
  *(int *)(param_1 + 0x18) = iVar1;
  return;
}

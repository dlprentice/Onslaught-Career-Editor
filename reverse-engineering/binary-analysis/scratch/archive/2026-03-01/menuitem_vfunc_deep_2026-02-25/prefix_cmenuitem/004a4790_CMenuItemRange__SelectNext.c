/* address: 0x004a4790 */
/* name: CMenuItemRange__SelectNext */
/* signature: undefined CMenuItemRange__SelectNext(void) */


void __fastcall CMenuItemRange__SelectNext(int param_1)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  void *pvVar4;
  int unaff_EDI;

  iVar1 = *(int *)(param_1 + 0x18);
  if (iVar1 < *(int *)(param_1 + 0x14) + -1) {
    *(int *)(param_1 + 0x18) = iVar1 + 1;
  }
  else {
    if (*(int *)(param_1 + 0x14) < 3) {
      return;
    }
    *(undefined4 *)(param_1 + 0x18) = 0;
  }
  piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),*(void **)(param_1 + 0x18),unaff_EDI);
  iVar3 = (**(code **)(*piVar2 + 0xc))();
  while( true ) {
    if (iVar3 != 0) {
      CFrontEnd__PlaySound(0);
      return;
    }
    pvVar4 = (void *)(*(int *)(param_1 + 0x18) + 1);
    *(void **)(param_1 + 0x18) = pvVar4;
    if (*(int *)(param_1 + 0x14) <= (int)pvVar4) break;
    piVar2 = (int *)CUnit__Unk_004e5c90((void *)(param_1 + 8),pvVar4,unaff_EDI);
    iVar3 = (**(code **)(*piVar2 + 0xc))();
  }
  *(int *)(param_1 + 0x18) = iVar1;
  return;
}

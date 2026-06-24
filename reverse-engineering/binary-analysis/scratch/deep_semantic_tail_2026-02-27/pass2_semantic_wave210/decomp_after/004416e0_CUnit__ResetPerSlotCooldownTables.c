/* address: 0x004416e0 */
/* name: CUnit__ResetPerSlotCooldownTables */
/* signature: void __fastcall CUnit__ResetPerSlotCooldownTables(int param_1) */


void __fastcall CUnit__ResetPerSlotCooldownTables(int param_1)

{
  undefined4 *puVar1;
  undefined1 *puVar2;
  int iVar3;

  puVar1 = (undefined4 *)(param_1 + 0x96c);
  puVar2 = (undefined1 *)(param_1 + 9);
  iVar3 = 0x1e;
  do {
    *puVar2 = 0;
    *puVar1 = 0xc2c80000;
    puVar1 = puVar1 + 1;
    puVar2 = puVar2 + 0x50;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  *(undefined4 *)(param_1 + 0x9e4) = 0;
  *(undefined4 *)(param_1 + 0x9e8) = 0xc2c80000;
  if (DAT_00662dd0 == 1) {
    *(undefined4 *)(param_1 + 0x9ec) = 1;
  }
  return;
}

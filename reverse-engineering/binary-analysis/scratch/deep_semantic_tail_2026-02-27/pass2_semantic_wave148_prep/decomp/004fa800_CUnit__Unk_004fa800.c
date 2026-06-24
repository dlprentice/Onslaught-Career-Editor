/* address: 0x004fa800 */
/* name: CUnit__Unk_004fa800 */
/* signature: void __fastcall CUnit__Unk_004fa800(void * param_1) */


void __fastcall CUnit__Unk_004fa800(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  iVar1 = *(int *)((int)param_1 + 0x168);
  if (iVar1 == 1) {
    if (*(float *)((int)param_1 + 0x16c) <= DAT_00672fd0) {
      if (*(int *)((int)param_1 + 0x1ec) == 0) {
        (**(code **)(*(int *)param_1 + 0x15c))();
        *(undefined4 *)((int)param_1 + 0x168) = 0;
        return;
      }
      *(undefined4 *)((int)param_1 + 0x1e8) = 1;
      *(undefined4 *)((int)param_1 + 0x168) = 0;
      return;
    }
    *(undefined4 *)((int)param_1 + 0x1e8) = 0;
  }
  else {
    if (iVar1 != 2) {
      if (iVar1 != 3) {
        return;
      }
      if (*(float *)((int)param_1 + 0x16c) < DAT_00672fd0) {
        *(undefined4 *)((int)param_1 + 0x168) = 0;
      }
      puVar2 = (undefined4 *)((int)param_1 + 0x9c);
      puVar3 = (undefined4 *)((int)param_1 + 0x3c);
      for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
        *puVar3 = *puVar2;
        puVar2 = puVar2 + 1;
        puVar3 = puVar3 + 1;
      }
      return;
    }
    *(undefined4 *)((int)param_1 + 0x1e8) = 0;
    if (*(float *)((int)param_1 + 0x16c) < DAT_00672fd0) {
      *(undefined4 *)((int)param_1 + 0x168) = 0;
      return;
    }
  }
  (**(code **)(*(int *)param_1 + 0x100))();
  return;
}

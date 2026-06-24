/* address: 0x004a4e80 */
/* name: CMenuItemRangeVariant__Destructor */
/* signature: undefined CMenuItemRangeVariant__Destructor(void) */


void __fastcall CMenuItemRangeVariant__Destructor(undefined4 *param_1)

{
  undefined4 *puVar1;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  pvStack_c = ExceptionList;
  puStack_8 = &LAB_005d36db;
  ExceptionList = &pvStack_c;
  *param_1 = &PTR_CMenuItemRange__ScalarDestructor_005dc650;
  puVar1 = (undefined4 *)param_1[2];
  local_4 = 0;
  param_1[4] = puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    puVar1 = (undefined4 *)*puVar1;
  }
  while (puVar1 != (undefined4 *)0x0) {
    if (puVar1 != (undefined4 *)0x0) {
      (**(code **)*puVar1)(1);
    }
    puVar1 = *(undefined4 **)(param_1[4] + 4);
    param_1[4] = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      puVar1 = (undefined4 *)0x0;
    }
    else {
      puVar1 = (undefined4 *)*puVar1;
    }
  }
  CSPtrSet__Clear(param_1 + 2);
  if (param_1[9] != 0) {
    CUnit__Unk_004f27e0(param_1[9] + 8);
    param_1[9] = 0;
  }
  local_4 = 0xffffffff;
  CSPtrSet__Clear(param_1 + 2);
  ExceptionList = pvStack_c;
  return;
}

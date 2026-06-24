/* address: 0x00412cf0 */
/* name: CCockpit__DestroyWeaponSetAndOwnedNodes */
/* signature: void __fastcall CCockpit__DestroyWeaponSetAndOwnedNodes(void * param_1) */


void __fastcall CCockpit__DestroyWeaponSetAndOwnedNodes(void *param_1)

{
  undefined4 *puVar1;
  int *value;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d1348;
  pvStack_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &pvStack_c;
  while( true ) {
    puVar1 = *(undefined4 **)param_1;
    *(undefined4 **)((int)param_1 + 8) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (value = (int *)*puVar1, value == (int *)0x0)) break;
    CSPtrSet__Remove(param_1,value);
    (**(code **)(*value + 4))(1);
  }
  if (*(int **)((int)param_1 + 0x18) != (int *)0x0) {
    (**(code **)(**(int **)((int)param_1 + 0x18) + 4))(1);
  }
  if (*(int **)((int)param_1 + 0x1c) != (int *)0x0) {
    (**(code **)(**(int **)((int)param_1 + 0x1c) + 4))(1);
  }
  local_4 = 0xffffffff;
  CSPtrSet__Clear(param_1);
  ExceptionList = pvStack_c;
  return;
}

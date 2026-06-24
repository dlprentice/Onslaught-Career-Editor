/* address: 0x004102a0 */
/* name: CBattleEngine__Unk_004102a0 */
/* signature: void __fastcall CBattleEngine__Unk_004102a0(void * param_1) */


void __fastcall CBattleEngine__Unk_004102a0(void *param_1)

{
  undefined4 *puVar1;
  int *value;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d1308;
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
  local_4 = 0xffffffff;
  CSPtrSet__Clear(param_1);
  ExceptionList = pvStack_c;
  return;
}

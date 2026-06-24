/* address: 0x004d8a70 */
/* name: CUnit__Unk_004d8a70 */
/* signature: void __fastcall CUnit__Unk_004d8a70(int param_1) */


void __fastcall CUnit__Unk_004d8a70(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d49c8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CMonitor__Shutdown((void *)(param_1 + 0x24));
  local_4 = 0xffffffff;
  CCollisionSeekingRound__Destructor();
  ExceptionList = local_c;
  return;
}

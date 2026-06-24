/* address: 0x004f3a70 */
/* name: CThing__Unk_004f3a70 */
/* signature: void __fastcall CThing__Unk_004f3a70(int param_1) */


void __fastcall CThing__Unk_004f3a70(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d51b8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CMonitor__Shutdown((void *)(param_1 + 0x24));
  local_4 = 0xffffffff;
  CCollisionSeekingRound__Destructor();
  ExceptionList = local_c;
  return;
}

/* address: 0x00488ea0 */
/* name: CCollisionSeekingInfantryBloke__ShutdownAndDestroy */
/* signature: void __fastcall CCollisionSeekingInfantryBloke__ShutdownAndDestroy(int param_1) */


void __fastcall CCollisionSeekingInfantryBloke__ShutdownAndDestroy(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d2ea8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CMonitor__Shutdown((void *)(param_1 + 0x24));
  local_4 = 0xffffffff;
  CCollisionSeekingRound__Destructor();
  ExceptionList = local_c;
  return;
}

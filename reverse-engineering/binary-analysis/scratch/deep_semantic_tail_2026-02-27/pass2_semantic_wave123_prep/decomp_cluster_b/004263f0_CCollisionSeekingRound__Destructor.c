/* address: 0x004263f0 */
/* name: CCollisionSeekingRound__Destructor */
/* signature: undefined CCollisionSeekingRound__Destructor(void) */


void __fastcall CCollisionSeekingRound__Destructor(undefined4 *param_1)

{
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d19a8;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  *param_1 = &PTR_CFrontEndPage__ActiveNotification_NoOp_005d9608;
  local_4 = 0;
  if ((undefined4 *)param_1[5] != (undefined4 *)0x0) {
    (*(code *)**(undefined4 **)param_1[5])(1);
  }
  if ((undefined4 *)param_1[6] != (undefined4 *)0x0) {
    (*(code *)**(undefined4 **)param_1[6])(1);
  }
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = pvStack_c;
  return;
}

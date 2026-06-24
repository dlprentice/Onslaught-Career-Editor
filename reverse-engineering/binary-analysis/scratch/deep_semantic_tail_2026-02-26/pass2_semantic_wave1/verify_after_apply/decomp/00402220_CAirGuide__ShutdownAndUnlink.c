/* address: 0x00402220 */
/* name: CAirGuide__ShutdownAndUnlink */
/* signature: void __fastcall CAirGuide__ShutdownAndUnlink(void * param_1) */


void __fastcall CAirGuide__ShutdownAndUnlink(void *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d0f58;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  if ((*(int *)((int)param_1 + 0x2c) != 0) &&
     (this = *(void **)(*(int *)((int)param_1 + 0x2c) + 4), ExceptionList = &local_c,
     this != (void *)0x0)) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)((int)param_1 + 0x2c));
  }
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}

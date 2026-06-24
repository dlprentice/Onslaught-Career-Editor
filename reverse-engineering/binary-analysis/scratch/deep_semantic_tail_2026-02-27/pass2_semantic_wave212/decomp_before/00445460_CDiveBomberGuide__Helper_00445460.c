/* address: 0x00445460 */
/* name: CDiveBomberGuide__Helper_00445460 */
/* signature: void __fastcall CDiveBomberGuide__Helper_00445460(void * param_1) */


void __fastcall CDiveBomberGuide__Helper_00445460(void *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d22c8;
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

/* address: 0x0047d6d0 */
/* name: CGroundVehicleGuide__Helper_0047d6d0 */
/* signature: void __fastcall CGroundVehicleGuide__Helper_0047d6d0(void * param_1) */


void __fastcall CGroundVehicleGuide__Helper_0047d6d0(void *param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d2ca3;
  local_c = ExceptionList;
  local_4._0_1_ = 1;
  local_4._1_3_ = 0;
  ExceptionList = &local_c;
  OID__FreeObject(*(void **)((int)param_1 + 0x3c));
  local_4 = (uint)local_4._1_3_ << 8;
  OID__FreeObject(*(void **)((int)param_1 + 0x34));
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}

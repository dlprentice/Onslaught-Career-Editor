/* address: 0x0050f2d0 */
/* name: CDiveBomber__Destructor_VFunc01 */
/* signature: void __fastcall CDiveBomber__Destructor_VFunc01(int param_1) */


void __fastcall CDiveBomber__Destructor_VFunc01(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d6114;
  local_c = ExceptionList;
  local_4 = 2;
  ExceptionList = &local_c;
  CSPtrSet__Clear((void *)(param_1 + 0x26c));
  local_4._0_1_ = 1;
  CSPtrSet__Clear((void *)(param_1 + 0x25c));
  local_4 = (uint)local_4._1_3_ << 8;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CUnit__scalar_deleting_dtor_004f84e0();
  ExceptionList = local_c;
  return;
}

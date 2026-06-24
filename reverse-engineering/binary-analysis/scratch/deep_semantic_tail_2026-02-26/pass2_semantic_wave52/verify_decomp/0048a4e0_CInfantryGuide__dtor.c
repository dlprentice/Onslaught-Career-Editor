/* address: 0x0048a4e0 */
/* name: CInfantryGuide__dtor */
/* signature: void __fastcall CInfantryGuide__dtor(void * param_1) */


void __fastcall CInfantryGuide__dtor(void *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d2f1e;
  local_c = ExceptionList;
  local_4 = 1;
  ExceptionList = &local_c;
  if ((*(int *)((int)param_1 + 0x44) != 0) &&
     (this = *(void **)(*(int *)((int)param_1 + 0x44) + 4), ExceptionList = &local_c,
     this != (void *)0x0)) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)((int)param_1 + 0x44));
  }
  local_4._0_1_ = 2;
  OID__FreeObject(*(void **)((int)param_1 + 0x3c));
  local_4 = (uint)local_4._1_3_ << 8;
  OID__FreeObject(*(void **)((int)param_1 + 0x34));
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}

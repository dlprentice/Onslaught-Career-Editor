/* address: 0x0050f630 */
/* name: CRelaxedSquad__Destructor */
/* signature: void __fastcall CRelaxedSquad__Destructor(int param_1) */


void __fastcall CRelaxedSquad__Destructor(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d6208;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CSPtrSet__Clear((void *)(param_1 + 0xa4));
  local_4 = 0xffffffff;
  CComplexThing__ctor_like_004f3f00();
  ExceptionList = local_c;
  return;
}

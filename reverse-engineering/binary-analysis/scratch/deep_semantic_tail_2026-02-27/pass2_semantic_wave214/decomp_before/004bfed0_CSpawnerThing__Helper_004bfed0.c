/* address: 0x004bfed0 */
/* name: CSpawnerThing__Helper_004bfed0 */
/* signature: void __fastcall CSpawnerThing__Helper_004bfed0(int param_1) */


void __fastcall CSpawnerThing__Helper_004bfed0(int param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d3fc8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  if ((*(int *)(param_1 + 0x7c) != 0) &&
     (this = *(void **)(*(int *)(param_1 + 0x7c) + 4), ExceptionList = &local_c, this != (void *)0x0
     )) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)(param_1 + 0x7c));
  }
  local_4 = 0xffffffff;
  CComplexThing__ctor_like_004f3f00();
  ExceptionList = local_c;
  return;
}

/* address: 0x0050fff0 */
/* name: CExplosion__Destructor */
/* signature: void __fastcall CExplosion__Destructor(int param_1) */


void __fastcall CExplosion__Destructor(int param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d6438;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  if ((*(int *)(param_1 + 0x90) != 0) &&
     (this = *(void **)(*(int *)(param_1 + 0x90) + 4), ExceptionList = &local_c, this != (void *)0x0
     )) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)(param_1 + 0x90));
  }
  local_4 = 0xffffffff;
  CComplexThing__ctor_like_004f3f00();
  ExceptionList = local_c;
  return;
}

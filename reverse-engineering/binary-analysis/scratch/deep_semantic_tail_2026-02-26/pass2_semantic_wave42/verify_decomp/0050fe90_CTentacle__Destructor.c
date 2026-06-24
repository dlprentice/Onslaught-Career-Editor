/* address: 0x0050fe90 */
/* name: CTentacle__Destructor */
/* signature: void __fastcall CTentacle__Destructor(int param_1) */


void __fastcall CTentacle__Destructor(int param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  puStack_8 = &LAB_005d63f6;
  local_c = ExceptionList;
  local_4 = 1;
  ExceptionList = &local_c;
  if ((*(int *)(param_1 + 0x26c) != 0) &&
     (this = *(void **)(*(int *)(param_1 + 0x26c) + 4), ExceptionList = &local_c,
     this != (void *)0x0)) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)(param_1 + 0x26c));
  }
  local_4 = local_4 & 0xffffff00;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CUnit__scalar_deleting_dtor_004f84e0();
  ExceptionList = local_c;
  return;
}

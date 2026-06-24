/* address: 0x0050f8d0 */
/* name: CMissile__Destructor */
/* signature: void __fastcall CMissile__Destructor(void * param_1) */


void __fastcall CMissile__Destructor(void *param_1)

{
  void *pvVar1;
  void *pvStack_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d62b4;
  pvStack_c = ExceptionList;
  local_4 = 2;
  ExceptionList = &pvStack_c;
  if ((*(int *)((int)param_1 + 0xec) != 0) &&
     (pvVar1 = *(void **)(*(int *)((int)param_1 + 0xec) + 4), ExceptionList = &pvStack_c,
     pvVar1 != (void *)0x0)) {
    ExceptionList = &pvStack_c;
    CSPtrSet__Remove(pvVar1,(void *)((int)param_1 + 0xec));
  }
  local_4._0_1_ = 1;
  if ((*(int *)((int)param_1 + 0xe8) != 0) &&
     (pvVar1 = *(void **)(*(int *)((int)param_1 + 0xe8) + 4), pvVar1 != (void *)0x0)) {
    CSPtrSet__Remove(pvVar1,(void *)((int)param_1 + 0xe8));
  }
  local_4 = (uint)local_4._1_3_ << 8;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CActor__ctor_like_004013d0(param_1);
  ExceptionList = pvStack_c;
  return;
}

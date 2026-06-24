/* address: 0x00505f90 */
/* name: CWeapon__Helper_00505f90 */
/* signature: void __fastcall CWeapon__Helper_00505f90(void * param_1) */


void __fastcall CWeapon__Helper_00505f90(void *param_1)

{
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  puStack_8 = &LAB_005d58fe;
  local_c = ExceptionList;
  local_4 = 1;
  ExceptionList = &local_c;
  if ((*(int *)((int)param_1 + 0x2c) != 0) &&
     (this = *(void **)(*(int *)((int)param_1 + 0x2c) + 4), ExceptionList = &local_c,
     this != (void *)0x0)) {
    ExceptionList = &local_c;
    CSPtrSet__Remove(this,(void *)((int)param_1 + 0x2c));
  }
  local_4 = local_4 & 0xffffff00;
  CDXLandscape__DestroyArrayWithCallback
            ((int)param_1 + 0x14,8,2,CParticleManager__RemoveFromGlobalList);
  local_4 = 0xffffffff;
  CMonitor__Shutdown(param_1);
  ExceptionList = local_c;
  return;
}

/* address: 0x0050f1a0 */
/* name: CInfantryUnit__Destructor_VFunc01 */
/* signature: void CInfantryUnit__Destructor_VFunc01(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CInfantryUnit__Destructor_VFunc01(void)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d6078;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CUnit__scalar_deleting_dtor_004f84e0();
  ExceptionList = local_c;
  return;
}

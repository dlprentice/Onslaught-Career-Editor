/* address: 0x00510250 */
/* name: CWorldPhysicsManager__Unk_00510250 */
/* signature: void CWorldPhysicsManager__Unk_00510250(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorldPhysicsManager__Unk_00510250(void)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d64b8;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CComplexThing__ctor_like_004f3f00();
  ExceptionList = local_c;
  return;
}

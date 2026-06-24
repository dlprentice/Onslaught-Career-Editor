/* address: 0x004bff40 */
/* name: CExplosionInitThing__Unk_004bff40 */
/* signature: void __fastcall CExplosionInitThing__Unk_004bff40(int param_1) */


void __fastcall CExplosionInitThing__Unk_004bff40(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  uint local_4;

  puStack_8 = &LAB_005d3ff3;
  local_c = ExceptionList;
  local_4 = 1;
  ExceptionList = &local_c;
  CSPtrSet__Clear((void *)(param_1 + 0x8c));
  local_4 = local_4 & 0xffffff00;
  CParticleManager__RemoveFromGlobalList();
  local_4 = 0xffffffff;
  CComplexThing__ctor_like_004f3f00();
  ExceptionList = local_c;
  return;
}

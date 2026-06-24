/* address: 0x005113a0 */
/* name: CWorldPhysicsManager__Unk_005113a0 */
/* signature: void __fastcall CWorldPhysicsManager__Unk_005113a0(int param_1) */


void __fastcall CWorldPhysicsManager__Unk_005113a0(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d669b;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  CSPtrSet__Clear((void *)(param_1 + 0x50));
  local_4 = 0xffffffff;
  CSPtrSet__Clear((void *)(param_1 + 0x40));
  ExceptionList = local_c;
  return;
}

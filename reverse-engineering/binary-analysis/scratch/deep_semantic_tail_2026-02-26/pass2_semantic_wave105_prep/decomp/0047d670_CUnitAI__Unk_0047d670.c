/* address: 0x0047d670 */
/* name: CUnitAI__Unk_0047d670 */
/* signature: void __fastcall CUnitAI__Unk_0047d670(int param_1) */


void __fastcall CUnitAI__Unk_0047d670(int param_1)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d2c7b;
  local_c = ExceptionList;
  local_4 = 0;
  ExceptionList = &local_c;
  OID__FreeObject(*(void **)(param_1 + 0x18));
  local_4 = 0xffffffff;
  OID__FreeObject(*(void **)(param_1 + 0x10));
  ExceptionList = local_c;
  return;
}

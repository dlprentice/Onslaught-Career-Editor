/* address: 0x00510eb0 */
/* name: CWorldPhysicsManager__FreeRoundStatement */
/* signature: void __fastcall CWorldPhysicsManager__FreeRoundStatement(int param_1) */


void __fastcall CWorldPhysicsManager__FreeRoundStatement(int param_1)

{
  OID__FreeObject(*(void **)(param_1 + 0x18));
  *(undefined4 *)(param_1 + 0x18) = 0;
  OID__FreeObject(*(void **)(param_1 + 8));
  *(undefined4 *)(param_1 + 8) = 0;
  OID__FreeObject(*(void **)(param_1 + 0xc));
  *(undefined4 *)(param_1 + 0xc) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x10));
  *(undefined4 *)(param_1 + 0x10) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x14));
  *(undefined4 *)(param_1 + 0x14) = 0;
  return;
}

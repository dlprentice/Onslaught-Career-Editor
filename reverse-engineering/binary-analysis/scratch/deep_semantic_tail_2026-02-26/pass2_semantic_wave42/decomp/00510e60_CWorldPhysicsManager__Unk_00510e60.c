/* address: 0x00510e60 */
/* name: CWorldPhysicsManager__Unk_00510e60 */
/* signature: void __fastcall CWorldPhysicsManager__Unk_00510e60(void * param_1) */


void __fastcall CWorldPhysicsManager__Unk_00510e60(void *param_1)

{
  OID__FreeObject(*(void **)param_1);
  *(undefined4 *)param_1 = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0x20));
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  OID__FreeObject(*(void **)((int)param_1 + 0xc));
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  return;
}

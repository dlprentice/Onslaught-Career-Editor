/* address: 0x00511040 */
/* name: CWorldPhysicsManager__FreeWeaponStatement */
/* signature: void __fastcall CWorldPhysicsManager__FreeWeaponStatement(void * param_1) */


void __fastcall CWorldPhysicsManager__FreeWeaponStatement(void *param_1)

{
  OID__FreeObject(*(void **)param_1);
  *(undefined4 *)param_1 = 0;
  OID__FreeObject(*(void **)((int)param_1 + 4));
  *(undefined4 *)((int)param_1 + 4) = 0;
  return;
}

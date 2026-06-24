/* address: 0x00440c00 */
/* name: CDamage__FreeOwnedDamageObjects */
/* signature: void __fastcall CDamage__FreeOwnedDamageObjects(void * param_1) */


void __fastcall CDamage__FreeOwnedDamageObjects(void *param_1)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)param_1;
  if ((puVar1 != (undefined4 *)0x0) && ((void *)*puVar1 != (void *)0x0)) {
    OID__FreeObject((void *)*puVar1);
    *puVar1 = 0;
  }
  if (*(void **)param_1 != (void *)0x0) {
    OID__FreeObject(*(void **)param_1);
    *(undefined4 *)param_1 = 0;
  }
  return;
}

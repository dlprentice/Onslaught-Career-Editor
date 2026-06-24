/* address: 0x004fcfe0 */
/* name: CUnit__ReleaseChildUnits */
/* signature: void __fastcall CUnit__ReleaseChildUnits(int param_1) */


void __fastcall CUnit__ReleaseChildUnits(int param_1)

{
  undefined4 *puVar1;
  int *value;
  int *piVar2;

  while ((puVar1 = *(undefined4 **)(param_1 + 0x19c), puVar1 != (undefined4 *)0x0 &&
         (value = (int *)*puVar1, value != (int *)0x0))) {
    piVar2 = (int *)*value;
    if (piVar2 != (int *)0x0) {
      if ((*(byte *)(param_1 + 0x2c) & 4) == 0) {
        (**(code **)(*piVar2 + 8))();
      }
      else {
        (**(code **)(*piVar2 + 200))();
      }
    }
    CSPtrSet__Remove((int *)(param_1 + 0x19c),value);
    CGenericActiveReader__dtor(value);
    OID__FreeObject(value);
  }
  return;
}

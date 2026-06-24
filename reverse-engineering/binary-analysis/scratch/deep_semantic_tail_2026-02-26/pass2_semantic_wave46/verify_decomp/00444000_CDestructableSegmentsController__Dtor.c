/* address: 0x00444000 */
/* name: CDestructableSegmentsController__Dtor */
/* signature: void __fastcall CDestructableSegmentsController__Dtor(int param_1) */


void __fastcall CDestructableSegmentsController__Dtor(int param_1)

{
  OID__FreeObject(*(void **)(param_1 + 4));
  if (*(int **)(param_1 + 0xc) != (int *)0x0) {
    (**(code **)(**(int **)(param_1 + 0xc) + 4))(1);
  }
  return;
}

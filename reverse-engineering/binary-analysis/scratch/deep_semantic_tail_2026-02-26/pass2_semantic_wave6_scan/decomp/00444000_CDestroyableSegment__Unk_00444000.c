/* address: 0x00444000 */
/* name: CDestroyableSegment__Unk_00444000 */
/* signature: void __fastcall CDestroyableSegment__Unk_00444000(int param_1) */


void __fastcall CDestroyableSegment__Unk_00444000(int param_1)

{
  OID__FreeObject(*(void **)(param_1 + 4));
  if (*(int **)(param_1 + 0xc) != (int *)0x0) {
    (**(code **)(**(int **)(param_1 + 0xc) + 4))(1);
  }
  return;
}

/* address: 0x00589438 */
/* name: CTexture__CleanupIncludeContextRecursive */
/* signature: void __fastcall CTexture__CleanupIncludeContextRecursive(int param_1) */


void __fastcall CTexture__CleanupIncludeContextRecursive(int param_1)

{
  void *ptr;
  int *piVar1;
  void *extraout_EDX;
  int unaff_ESI;

  if (*(void **)(param_1 + 0x38) != (void *)0x0) {
    CTexture__IncludeNodeChain_scalar_deleting_dtor
              (*(void **)(param_1 + 0x38),(void *)0x1,unaff_ESI);
  }
  ptr = *(void **)(param_1 + 0x6c);
  if (ptr != (void *)0x0) {
    CTexture__CleanupIncludeContextRecursive((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  piVar1 = *(int **)(param_1 + 0x58);
  if ((piVar1 != (int *)0x0) && (*(int *)(param_1 + 100) != 0)) {
    (**(code **)(*piVar1 + 4))(piVar1,*(int *)(param_1 + 100));
  }
  CDXTexture__Helper_005888ae((void *)(param_1 + 0x4c));
  CDXTexture__Helper_00588896((void *)(param_1 + 0x3c),extraout_EDX);
  CTexture__Helper_0059877e();
  return;
}

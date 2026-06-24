/* address: 0x00589438 */
/* name: CDXTexture__Unk_00589438 */
/* signature: void __fastcall CDXTexture__Unk_00589438(int param_1) */


void __fastcall CDXTexture__Unk_00589438(int param_1)

{
  void *ptr;
  int *piVar1;
  void *extraout_EDX;
  int unaff_ESI;

  if (*(void **)(param_1 + 0x38) != (void *)0x0) {
    CDXTexture__Unk_005893e9(*(void **)(param_1 + 0x38),(void *)0x1,unaff_ESI);
  }
  ptr = *(void **)(param_1 + 0x6c);
  if (ptr != (void *)0x0) {
    CDXTexture__Unk_00589438((int)ptr);
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

/* address: 0x0058fb8b */
/* name: CTexture__Helper_0058fb8b */
/* signature: void __fastcall CTexture__Helper_0058fb8b(int param_1) */


void __fastcall CTexture__Helper_0058fb8b(int param_1)

{
  int *piVar1;
  int unaff_retaddr;

  piVar1 = *(int **)(param_1 + 8);
  if (piVar1 != (int *)0x0) {
    (**(code **)(*piVar1 + 8))(piVar1);
    *(undefined4 *)(param_1 + 8) = 0;
  }
  if (*(undefined4 **)(param_1 + 0x34) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x34))(1);
  }
  OID__FreeObject_Callback(*(void **)(param_1 + 0x58));
  if (*(void **)(param_1 + 0x78) != (void *)0x0) {
    CTexture__Dtor_ReleaseParserState_DeleteOnFlag
              (*(void **)(param_1 + 0x78),(void *)0x1,unaff_retaddr);
  }
  return;
}

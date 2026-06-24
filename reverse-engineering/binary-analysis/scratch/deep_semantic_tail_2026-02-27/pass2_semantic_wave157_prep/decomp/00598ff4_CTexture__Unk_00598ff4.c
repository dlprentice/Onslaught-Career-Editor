/* address: 0x00598ff4 */
/* name: CTexture__Unk_00598ff4 */
/* signature: void __fastcall CTexture__Unk_00598ff4(int param_1) */


void __fastcall CTexture__Unk_00598ff4(int param_1)

{
  int iVar1;
  undefined4 *ptr;

  iVar1 = *(int *)(param_1 + 8);
  while (iVar1 != 0) {
    ptr = *(undefined4 **)(param_1 + 8);
    *(undefined4 *)(param_1 + 8) = ptr[4];
    if (((ptr[2] & 8) != 0) || ((ptr[2] & 1) == 0)) {
      OID__FreeObject_Callback((void *)*ptr);
    }
    OID__FreeObject_Callback(ptr);
    iVar1 = *(int *)(param_1 + 8);
  }
  return;
}

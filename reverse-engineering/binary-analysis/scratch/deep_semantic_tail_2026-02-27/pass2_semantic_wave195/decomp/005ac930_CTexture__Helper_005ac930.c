/* address: 0x005ac930 */
/* name: CTexture__Helper_005ac930 */
/* signature: void __stdcall CTexture__Helper_005ac930(int param_1) */


void CTexture__Helper_005ac930(int param_1)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)(param_1 + 0x1b0);
  if (*(int *)(iVar1 + 0x10) != 0) {
    if (*(int *)(param_1 + 0x50) != 0) {
      iVar2 = CTexture__Helper_005ac180();
      if (iVar2 != 0) {
        *(undefined1 **)(iVar1 + 0xc) = &LAB_005ac2d0;
        *(undefined4 *)(param_1 + 0xa0) = 0;
        return;
      }
    }
    *(undefined1 **)(iVar1 + 0xc) = &LAB_005abff0;
  }
  *(undefined4 *)(param_1 + 0xa0) = 0;
  return;
}

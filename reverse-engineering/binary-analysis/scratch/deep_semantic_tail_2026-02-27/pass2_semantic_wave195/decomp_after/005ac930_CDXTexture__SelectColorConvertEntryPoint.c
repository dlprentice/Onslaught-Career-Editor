/* address: 0x005ac930 */
/* name: CDXTexture__SelectColorConvertEntryPoint */
/* signature: void __stdcall CDXTexture__SelectColorConvertEntryPoint(int param_1) */


void CDXTexture__SelectColorConvertEntryPoint(int param_1)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)(param_1 + 0x1b0);
  if (*(int *)(iVar1 + 0x10) != 0) {
    if (*(int *)(param_1 + 0x50) != 0) {
      iVar2 = CDXTexture__ValidateAndIndexQuantTables();
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

/* address: 0x00589405 */
/* name: CTexture__Helper_00589405 */
/* signature: int __fastcall CTexture__Helper_00589405(int param_1) */


int __fastcall CTexture__Helper_00589405(int param_1)

{
  CTexture__TokenList_InitState_Extended_0058c37c((void *)param_1);
  CDXTexture__InitMappedFileContext((void *)(param_1 + 0x3c));
  CDXTexture__ZeroGdiBitmapRecord((void *)(param_1 + 0x4c));
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x58) = 0;
  *(undefined4 *)(param_1 + 100) = 0;
  *(undefined4 *)(param_1 + 0x68) = 0;
  *(undefined4 *)(param_1 + 0x5c) = 0;
  *(undefined4 *)(param_1 + 0x60) = 0;
  *(undefined4 *)(param_1 + 0x6c) = 0;
  return param_1;
}

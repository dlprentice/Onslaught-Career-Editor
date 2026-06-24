/* address: 0x00588896 */
/* name: CDXTexture__CloseHandleIfValid */
/* signature: void __fastcall CDXTexture__CloseHandleIfValid(void * param_1, void * param_2) */


void __fastcall CDXTexture__CloseHandleIfValid(void *param_1,void *param_2)

{
  if (*(int *)param_1 != -1) {
    CTexture__Helper_00588855(param_1);
    return;
  }
  return;
}

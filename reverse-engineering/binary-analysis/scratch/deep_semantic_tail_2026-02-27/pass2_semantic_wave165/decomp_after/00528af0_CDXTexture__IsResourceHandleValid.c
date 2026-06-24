/* address: 0x00528af0 */
/* name: CDXTexture__IsResourceHandleValid */
/* signature: bool __fastcall CDXTexture__IsResourceHandleValid(int param_1) */


bool __fastcall CDXTexture__IsResourceHandleValid(int param_1)

{
  return *(int *)(param_1 + 0xc) != -1;
}

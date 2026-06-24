/* address: 0x00562a01 */
/* name: CDXTexture__ValidateSourceAndSetLoadErrorClass */
/* signature: int __cdecl CDXTexture__ValidateSourceAndSetLoadErrorClass(void * param_1, void * param_2) */


int __cdecl CDXTexture__ValidateSourceAndSetLoadErrorClass(void *param_1,void *param_2)

{
  int iVar1;
  int extraout_EAX;
  int extraout_EAX_00;

  iVar1 = CTexture__Helper_00562ab1((int)param_2);
  if (iVar1 != 0) {
    CTexture__Helper_00562c76();
    iVar1 = CDXTexture__Helper_0056c05c();
    if (iVar1 == 0) {
      CDXTexture__SetLoadErrorClassBySourceKind((int)param_1);
      iVar1 = extraout_EAX;
    }
    return iVar1;
  }
  CTexture__Helper_00562c76();
  CDXTexture__SetLoadErrorClassBySourceKind((int)param_1);
  return extraout_EAX_00;
}

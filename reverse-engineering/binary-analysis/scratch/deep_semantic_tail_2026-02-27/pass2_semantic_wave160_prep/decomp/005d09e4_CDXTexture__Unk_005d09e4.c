/* address: 0x005d09e4 */
/* name: CDXTexture__Unk_005d09e4 */
/* signature: int __cdecl CDXTexture__Unk_005d09e4(void * param_1) */


int __cdecl CDXTexture__Unk_005d09e4(void *param_1)

{
  int iVar1;
  int extraout_EAX;
  void *pvVar2;

  iVar1 = CRT__MbsRChr(param_1,0x2e);
  CDXTexture__Helper_0056cb9d(iVar1 + 1,0,0x20);
  if (extraout_EAX + 1U < 0x7fff) {
    pvVar2 = CRT__UIntToAsciiBase_ReturnBuffer(extraout_EAX + 1U,&param_1,0x20);
    CDXTexture__Helper_00567de0((void *)(iVar1 + 1),pvVar2);
    iVar1 = 0;
  }
  else {
    iVar1 = -1;
  }
  return iVar1;
}

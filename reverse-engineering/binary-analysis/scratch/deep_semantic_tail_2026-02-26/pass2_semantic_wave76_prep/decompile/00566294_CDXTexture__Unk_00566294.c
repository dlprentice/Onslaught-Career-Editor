/* address: 0x00566294 */
/* name: CDXTexture__Unk_00566294 */
/* signature: int __cdecl CDXTexture__Unk_00566294(int param_1) */


int __cdecl CDXTexture__Unk_00566294(int param_1)

{
  int iVar1;

  DAT_009d35e4 = HeapCreate((uint)(param_1 == 0),0x1000,0);
  if (DAT_009d35e4 != (HANDLE)0x0) {
    DAT_009d35e8 = CDXTexture__Unk_0056614c();
    if (DAT_009d35e8 == 3) {
      iVar1 = CDXTexture__Unk_005662f1(0x3f8);
    }
    else {
      if (DAT_009d35e8 != 2) {
        return 1;
      }
      iVar1 = CTexture__Unk_00566e38();
    }
    if (iVar1 != 0) {
      return 1;
    }
    HeapDestroy(DAT_009d35e4);
  }
  return 0;
}

/* address: 0x00569e57 */
/* name: CDXTexture__Unk_00569e57 */
/* signature: int __cdecl CDXTexture__Unk_00569e57(int param_1, int param_2) */


int __cdecl CDXTexture__Unk_00569e57(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;

  iVar1 = param_1;
  if (param_1 == 0) {
    return 0;
  }
  if (DAT_009d0998 == 0) {
    if ((ushort)param_2 < 0x100) {
      *(char *)param_1 = (char)param_2;
      return 1;
    }
  }
  else {
    param_1 = 0;
    iVar1 = WideCharToMultiByte(DAT_009d09a8,0x220,(LPCWSTR)&param_2,1,(LPSTR)iVar1,DAT_00653a9c,
                                (LPCSTR)0x0,&param_1);
    if ((iVar1 != 0) && (param_1 == 0)) {
      return iVar1;
    }
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 0x2a;
  return -1;
}

/* address: 0x00564f4c */
/* name: CTexture__Helper_00564f4c */
/* signature: int __cdecl CTexture__Helper_00564f4c(int param_1) */


int __cdecl CTexture__Helper_00564f4c(int param_1)

{
  int iVar1;

  iVar1 = CDXTexture__FlushWriteStreamSegment((void *)param_1);
  if (iVar1 != 0) {
    return -1;
  }
  if ((*(byte *)(param_1 + 0xd) & 0x40) != 0) {
    iVar1 = CRT__CommitFileHandle(*(uint *)(param_1 + 0x10));
    return -(uint)(iVar1 != 0);
  }
  return 0;
}

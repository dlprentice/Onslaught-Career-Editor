/* address: 0x00569732 */
/* name: CDXTexture__Unk_00569732 */
/* signature: void __cdecl CDXTexture__Unk_00569732(int param_1, int param_2) */


void __cdecl CDXTexture__Unk_00569732(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  uint *puVar3;

  puVar3 = (uint *)(param_1 + (param_2 / 0x20) * 4);
  iVar1 = CDXTexture__Helper_0056d4a6(*puVar3,1 << (0x1fU - (char)(param_2 % 0x20) & 0x1f),puVar3);
  iVar2 = param_2 / 0x20 + -1;
  if (-1 < iVar2) {
    puVar3 = (uint *)(param_1 + iVar2 * 4);
    do {
      if (iVar1 == 0) {
        return;
      }
      iVar1 = CDXTexture__Helper_0056d4a6(*puVar3,1,puVar3);
      iVar2 = iVar2 + -1;
      puVar3 = puVar3 + -1;
    } while (-1 < iVar2);
  }
  return;
}

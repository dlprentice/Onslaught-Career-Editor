/* address: 0x005696e9 */
/* name: CDXTexture__Unk_005696e9 */
/* signature: int __cdecl CDXTexture__Unk_005696e9(int param_1, int param_2) */


int __cdecl CDXTexture__Unk_005696e9(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;

  if ((*(uint *)(param_1 + (param_2 / 0x20) * 4) & ~(-1 << (0x1fU - (char)(param_2 % 0x20) & 0x1f)))
      != 0) {
    return 0;
  }
  iVar2 = param_2 / 0x20 + 1;
  if (iVar2 < 3) {
    piVar1 = (int *)(param_1 + iVar2 * 4);
    do {
      if (*piVar1 != 0) {
        return 0;
      }
      iVar2 = iVar2 + 1;
      piVar1 = piVar1 + 1;
    } while (iVar2 < 3);
  }
  return 1;
}

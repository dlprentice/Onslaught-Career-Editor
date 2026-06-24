/* address: 0x005951e9 */
/* name: CDXTexture__Helper_005951e9 */
/* signature: int __stdcall CDXTexture__Helper_005951e9(int param_1) */


int CDXTexture__Helper_005951e9(int param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;

  if (param_1 == 0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    puVar1 = (undefined4 *)CDXTexture__AllocZeroedDecodeState(2);
    if (puVar1 != (undefined4 *)0x0) {
      puVar3 = puVar1;
      for (iVar2 = 0x10; iVar2 != 0; iVar2 = iVar2 + -1) {
        *puVar3 = 0;
        puVar3 = puVar3 + 1;
      }
    }
  }
  return (int)puVar1;
}

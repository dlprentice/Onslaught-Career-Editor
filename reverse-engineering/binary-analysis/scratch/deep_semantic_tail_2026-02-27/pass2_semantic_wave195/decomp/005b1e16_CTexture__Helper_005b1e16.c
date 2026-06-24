/* address: 0x005b1e16 */
/* name: CTexture__Helper_005b1e16 */
/* signature: int __stdcall CTexture__Helper_005b1e16(int param_1) */


int CTexture__Helper_005b1e16(int param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;

  puVar1 = (undefined4 *)(**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1);
  if (puVar1 != (undefined4 *)0x0) {
    uVar3 = 8;
    iVar2 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),8,0x5a0);
    puVar1[9] = iVar2;
    if (iVar2 != 0) {
      iVar2 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1,0x40);
      puVar1[10] = iVar2;
      if (iVar2 == 0) {
        (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),puVar1[9]);
        (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),puVar1);
        return 0;
      }
      *puVar1 = 0;
      puVar1[0xb] = iVar2 + 0x40;
      puVar1[0xe] = uVar3;
      CDXTexture__ResetDecodeWindowState(puVar1,param_1,(void *)0x0);
      return (int)puVar1;
    }
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),puVar1);
  }
  return 0;
}

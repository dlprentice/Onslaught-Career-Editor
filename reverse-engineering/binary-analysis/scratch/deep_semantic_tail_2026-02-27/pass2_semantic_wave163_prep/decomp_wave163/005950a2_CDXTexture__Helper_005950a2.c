/* address: 0x005950a2 */
/* name: CDXTexture__Helper_005950a2 */
/* signature: void __stdcall CDXTexture__Helper_005950a2(int param_1, int param_2, int param_3) */


void CDXTexture__Helper_005950a2(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x54) = param_2;
  *(int *)(param_1 + 0x50) = param_3;
  if (*(int *)(param_1 + 0x4c) != 0) {
    *(undefined4 *)(param_1 + 0x4c) = 0;
    CDXTexture__Helper_00592d63(param_1,0x5eeb88);
    CDXTexture__Helper_00592d63(param_1,0x5eeb54);
  }
  *(undefined4 *)(param_1 + 0x120) = 0;
  return;
}

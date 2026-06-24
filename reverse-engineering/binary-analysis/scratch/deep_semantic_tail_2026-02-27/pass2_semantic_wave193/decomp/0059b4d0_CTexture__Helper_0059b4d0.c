/* address: 0x0059b4d0 */
/* name: CTexture__Helper_0059b4d0 */
/* signature: void __stdcall CTexture__Helper_0059b4d0(int param_1) */


void CTexture__Helper_0059b4d0(int param_1)

{
  undefined4 *puVar1;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x1c);
  *(undefined4 **)(param_1 + 0x1a8) = puVar1;
  *puVar1 = CTexture__Helper_0059b370;
  puVar1[1] = &LAB_0059b4a0;
  puVar1[2] = 0;
  CTexture__Helper_0059b1d0();
  return;
}

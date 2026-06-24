/* address: 0x005ad550 */
/* name: CDXTexture__Helper_005ad550 */
/* signature: void __stdcall CDXTexture__Helper_005ad550(int param_1) */


void CDXTexture__Helper_005ad550(int param_1)

{
  undefined4 *puVar1;
  int iVar2;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0xe8);
  *(undefined4 **)(param_1 + 0x1c0) = puVar1;
  *puVar1 = &LAB_005ad410;
  puVar1[1] = &LAB_005ad000;
  puVar1 = puVar1 + 10;
  iVar2 = 4;
  do {
    puVar1[4] = 0;
    *puVar1 = 0;
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}

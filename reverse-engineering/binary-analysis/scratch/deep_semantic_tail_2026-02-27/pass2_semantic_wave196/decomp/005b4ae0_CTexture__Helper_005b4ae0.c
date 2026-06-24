/* address: 0x005b4ae0 */
/* name: CTexture__Helper_005b4ae0 */
/* signature: void __stdcall CTexture__Helper_005b4ae0(int param_1) */


void CTexture__Helper_005b4ae0(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,1,0x6c);
  *(undefined4 **)(param_1 + 0x174) = puVar1;
  *puVar1 = &LAB_005b4950;
  puVar2 = puVar1 + 0x17;
  iVar3 = 4;
  do {
    puVar2[-4] = 0;
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  puVar1[0x10] = 0;
  return;
}

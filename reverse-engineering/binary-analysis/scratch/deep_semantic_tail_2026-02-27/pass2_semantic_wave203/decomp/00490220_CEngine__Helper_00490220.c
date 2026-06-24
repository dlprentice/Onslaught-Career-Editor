/* address: 0x00490220 */
/* name: CEngine__Helper_00490220 */
/* signature: void __fastcall CEngine__Helper_00490220(int param_1) */


void __fastcall CEngine__Helper_00490220(int param_1)

{
  undefined4 *puVar1;
  int iVar2;

  iVar2 = 6;
  puVar1 = (undefined4 *)(param_1 + 0x1f8);
  do {
    puVar1[-7] = 0;
    puVar1[-2] = 0;
    puVar1[-1] = 0;
    *puVar1 = 0;
    puVar1[2] = 0;
    puVar1[3] = 0;
    puVar1[4] = 0;
    puVar1[5] = 0;
    puVar1[-6] = 0;
    puVar1[-5] = 0;
    puVar1[-4] = 0;
    puVar1[6] = 0;
    puVar1[7] = 0;
    puVar1[8] = 0;
    puVar1[9] = 0;
    puVar1[10] = 0;
    puVar1[0xb] = 0;
    puVar1[0xc] = 0;
    puVar1[0xd] = 0;
    puVar1[0xe] = 0;
    puVar1 = puVar1 + 0x1d;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}

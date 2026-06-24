/* address: 0x004d0510 */
/* name: CPauseMenu__Unk_004d0510 */
/* signature: void __fastcall CPauseMenu__Unk_004d0510(int param_1) */


void __fastcall CPauseMenu__Unk_004d0510(int param_1)

{
  int iVar1;
  int *piVar2;

  piVar2 = *(int **)(param_1 + 0x14);
  *(int **)(param_1 + 0x1c) = piVar2;
  if (piVar2 == (int *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = *piVar2;
  }
  while (iVar1 != 0) {
    CMenuItemRange__LoadTexture();
    piVar2 = *(int **)(*(int *)(param_1 + 0x1c) + 4);
    *(int **)(param_1 + 0x1c) = piVar2;
    if (piVar2 == (int *)0x0) {
      iVar1 = 0;
    }
    else {
      iVar1 = *piVar2;
    }
  }
  piVar2 = CTexture__FindTexture(s_pausemenu_pause_circle01_tga_00631590,4,0,1,0,1);
  *(int **)(param_1 + 0x40) = piVar2;
  piVar2 = CTexture__FindTexture(s_pausemenu_pause_circle02_tga_00631570,4,0,1,0,1);
  *(int **)(param_1 + 0x44) = piVar2;
  if (DAT_0082b490 != (int *)0x0) {
    CHud__Helper_004f27e0((int)DAT_0082b490 + 8);
    DAT_0082b490 = (int *)0x0;
  }
  DAT_0082b490 = CTexture__FindTexture(s_FrontEnd_v2_FE_Blank_tga_00629f68,4,0,1,0,1);
  return;
}

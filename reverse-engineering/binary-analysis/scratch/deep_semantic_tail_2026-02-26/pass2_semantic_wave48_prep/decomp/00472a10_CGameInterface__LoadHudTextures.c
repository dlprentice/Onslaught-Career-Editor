/* address: 0x00472a10 */
/* name: CGameInterface__LoadHudTextures */
/* signature: void __fastcall CGameInterface__LoadHudTextures(int param_1) */


void __fastcall CGameInterface__LoadHudTextures(int param_1)

{
  int *piVar1;

  piVar1 = CTexture__FindTexture(s_Interface_Joypad_tga_0062c8a8,4,0,1,1,1);
  *(int **)(param_1 + 0xc) = piVar1;
  piVar1 = CTexture__FindTexture(s_hud_Menu_background_tga_0062c890,0,0,1,1,1);
  *(int **)(param_1 + 8) = piVar1;
  return;
}

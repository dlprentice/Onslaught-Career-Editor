/* address: 0x004b8e70 */
/* name: CMessageLog__LoadTextures */
/* signature: void __fastcall CMessageLog__LoadTextures(int param_1) */


void __fastcall CMessageLog__LoadTextures(int param_1)

{
  int *piVar1;

  piVar1 = CTexture__FindTexture(s_MessageLog_endcurve_tga_00630944,4,0,1,0,1);
  *(int **)(param_1 + 8) = piVar1;
  DAT_00807418 = CTexture__FindTexture(s_FrontEnd_v2_FE_Arrow_tga_006290f4,4,0,1,0,1);
  piVar1 = CTexture__FindTexture(s_FrontEnd_v2_FE_Blank_tga_00629f68,4,0,1,0,1);
  *(int **)(param_1 + 0xc) = piVar1;
  piVar1 = CTexture__FindTexture(s_MessageLog_messge_headframe_tga_00630924,4,0,1,0,1);
  *(int **)(param_1 + 0x10) = piVar1;
  piVar1 = CTexture__FindTexture(s_MessageLog_messge_headframe_mask_006308fc,4,0,1,0,1);
  *(int **)(param_1 + 0x14) = piVar1;
  return;
}

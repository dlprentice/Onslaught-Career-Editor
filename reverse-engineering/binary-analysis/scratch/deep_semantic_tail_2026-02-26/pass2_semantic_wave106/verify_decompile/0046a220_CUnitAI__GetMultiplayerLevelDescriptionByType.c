/* address: 0x0046a220 */
/* name: CUnitAI__GetMultiplayerLevelDescriptionByType */
/* signature: void __cdecl CUnitAI__GetMultiplayerLevelDescriptionByType(int param_1) */


void __cdecl CUnitAI__GetMultiplayerLevelDescriptionByType(int param_1)

{
  switch(param_1) {
  case 0:
    CText__GetStringById(&g_Text,0x358fd244);
    return;
  case 1:
    CText__GetStringById(&g_Text,0x4bc32e75);
    return;
  case 2:
  case 4:
    CText__GetStringById(&g_Text,0x61f68aa6);
    return;
  case 3:
    CText__GetStringById(&g_Text,0x358fd244);
    return;
  default:
    Text__AsciiToWideScratch(s_Unknown_Multiplayer_Level_Descri_0062aad4);
    return;
  }
}

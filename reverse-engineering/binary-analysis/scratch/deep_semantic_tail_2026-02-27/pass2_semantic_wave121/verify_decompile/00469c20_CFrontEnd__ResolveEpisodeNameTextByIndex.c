/* address: 0x00469c20 */
/* name: CFrontEnd__ResolveEpisodeNameTextByIndex */
/* signature: void __cdecl CFrontEnd__ResolveEpisodeNameTextByIndex(int param_1) */


void __cdecl CFrontEnd__ResolveEpisodeNameTextByIndex(int param_1)

{
  switch(param_1) {
  case 1:
    CText__GetStringById(&g_Text,0x19be7a7);
    return;
  case 2:
    CText__GetStringById(&g_Text,0x19ef81a);
    return;
  case 3:
    CText__GetStringById(&g_Text,0x1a2088d);
    return;
  case 4:
    CText__GetStringById(&g_Text,0x1a51900);
    return;
  case 5:
    CText__GetStringById(&g_Text,0x1a82973);
    return;
  case 6:
    CText__GetStringById(&g_Text,0x1ab39e6);
    return;
  case 7:
    CText__GetStringById(&g_Text,0x1ae4a59);
    return;
  case 8:
    CText__GetStringById(&g_Text,0x1b15acc);
    return;
  default:
    Text__AsciiToWideScratch(s_Unnamed_Episode_0062aac4);
    return;
  }
}

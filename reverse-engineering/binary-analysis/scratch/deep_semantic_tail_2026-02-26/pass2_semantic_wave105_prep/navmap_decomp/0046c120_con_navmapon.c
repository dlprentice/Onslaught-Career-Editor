/* address: 0x0046c120 */
/* name: con_navmapon */
/* signature: void __cdecl con_navmapon(char * cmd) */


/* Console command callback: con_navmapon(cmd)
   Source: references/Onslaught/game.cpp
   Registered by CGame__InitRestartLoop via CConsole__RegisterCommand("NavMapOn", ...,
   &con_navmapon, 0). */

void __cdecl con_navmapon(char *cmd)

{
  DAT_0089ce44 = 1;
  CUnitAI__Unk_0044a6b0();
  return;
}

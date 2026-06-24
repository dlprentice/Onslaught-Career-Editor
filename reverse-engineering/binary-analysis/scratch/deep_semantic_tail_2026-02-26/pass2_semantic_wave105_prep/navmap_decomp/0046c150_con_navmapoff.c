/* address: 0x0046c150 */
/* name: con_navmapoff */
/* signature: void __cdecl con_navmapoff(char * cmd) */


/* Console command callback: con_navmapoff(cmd)
   Source: references/Onslaught/game.cpp
   Registered by CGame__InitRestartLoop via CConsole__RegisterCommand("NavMapOff", ...,
   &con_navmapoff, 0). */

void __cdecl con_navmapoff(char *cmd)

{
  DAT_0089ce44 = 0;
  CUnitAI__Unk_0044a6b0();
  return;
}

/* address: 0x00464b30 */
/* name: CFEPLoadGame__ResolveTextByToken */
/* signature: void __cdecl CFEPLoadGame__ResolveTextByToken(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CFEPLoadGame__ResolveTextByToken(int param_1)

{
  short *psVar1;
  undefined1 local_190 [400];

  psVar1 = CFEPSaveGame__GetLocalizedOrFallbackTextByToken(param_1);
  CRT__WStrCpy(local_190,psVar1);
  DAT_00677614 = 0;
  CPlatform__Font(&DAT_0088a0a8,1);
  CFEPSaveGame__InitDialogAndLayoutState();
  _DAT_00677630 = 0;
  _DAT_00677634 = 0;
  return;
}

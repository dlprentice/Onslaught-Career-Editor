/* address: 0x00464bc0 */
/* name: CFEPSaveGame__DrawLocalizedStatusPrompt */
/* signature: void __stdcall CFEPSaveGame__DrawLocalizedStatusPrompt(int param_1, int param_2) */


void CFEPSaveGame__DrawLocalizedStatusPrompt(int param_1,int param_2)

{
  short *psVar1;
  undefined2 local_200 [256];

  local_200[0] = 0;
  if (param_2 == 0) {
    psVar1 = CFEPSaveGame__Helper_0046a2a0(0x9e);
  }
  else {
    psVar1 = CFEPSaveGame__Helper_0046a2a0(0xa0);
  }
  ControlsUI__Helper_0055e624(local_200,psVar1);
  CPlatform__Font(&DAT_0088a0a8,1);
  CFEPSaveGame__Helper_0044d390();
  return;
}

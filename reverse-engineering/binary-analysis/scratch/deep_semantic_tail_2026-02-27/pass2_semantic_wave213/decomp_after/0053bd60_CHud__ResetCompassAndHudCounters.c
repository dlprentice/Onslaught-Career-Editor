/* address: 0x0053bd60 */
/* name: CHud__ResetCompassAndHudCounters */
/* signature: int __fastcall CHud__ResetCompassAndHudCounters(int param_1) */


int __fastcall CHud__ResetCompassAndHudCounters(int param_1)

{
  undefined4 *puVar1;
  int iVar2;

  CDXCompass__Reset();
  puVar1 = (undefined4 *)(param_1 + 0x3f04);
  iVar2 = 2;
  do {
    puVar1[-0xc1] = 0;
    *puVar1 = 0;
    puVar1 = puVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  *(undefined4 *)(param_1 + 0x3f0c) = 0;
  *(undefined4 *)(param_1 + 0x3c08) = 0;
  *(undefined4 *)(param_1 + 0x3f10) = 0;
  return param_1;
}

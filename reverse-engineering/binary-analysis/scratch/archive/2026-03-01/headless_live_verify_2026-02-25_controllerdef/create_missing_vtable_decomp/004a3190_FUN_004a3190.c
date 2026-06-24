/* address: 0x004a3190 */
/* name: FUN_004a3190 */
/* signature: undefined FUN_004a3190(void) */


wchar_t * __fastcall FUN_004a3190(int param_1)

{
  wchar_t *pwVar1;
  short *psVar2;
  int iVar3;

  iVar3 = *(int *)(param_1 + 8);
  if ((iVar3 == 0x9aba4) || (iVar3 == 0x9c55c)) {
    psVar2 = CText__GetStringById(&g_Text,0x119bdd4);
    CTexture__Unk_0055e64e(&DAT_00704878,psVar2);
    psVar2 = Text__AsciiToWideScratch(&DAT_0062f7f8);
    CDXTexture__Unk_0055e624(&DAT_00704878,psVar2);
    iVar3 = 0x378d6;
  }
  else {
    if ((iVar3 != 0x10c6d0) && (iVar3 != 0x9d238)) {
      if (iVar3 == 0) {
        pwVar1 = Localization__GetStringById(*(int *)(param_1 + 0x18));
        return pwVar1;
      }
      pwVar1 = CText__GetStringById(&g_Text,iVar3);
      return pwVar1;
    }
    psVar2 = CText__GetStringById(&g_Text,0x119bdd4);
    CTexture__Unk_0055e64e(&DAT_00704878,psVar2);
    psVar2 = Text__AsciiToWideScratch(&DAT_0062f7f8);
    CDXTexture__Unk_0055e624(&DAT_00704878,psVar2);
    iVar3 = 0x50cf2;
  }
  psVar2 = CText__GetStringById(&g_Text,iVar3);
  CDXTexture__Unk_0055e624(&DAT_00704878,psVar2);
  return (wchar_t *)&DAT_00704878;
}

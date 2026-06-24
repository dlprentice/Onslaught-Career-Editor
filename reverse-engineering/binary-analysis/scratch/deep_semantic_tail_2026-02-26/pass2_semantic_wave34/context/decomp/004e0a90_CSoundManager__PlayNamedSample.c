/* address: 0x004e0a90 */
/* name: CSoundManager__PlayNamedSample */
/* signature: undefined CSoundManager__PlayNamedSample(void) */


void __thiscall CSoundManager__PlayNamedSample(void *param_1,char *param_2)

{
  int iVar1;

  if (*(char *)((int)param_1 + 4) == '\0') {
    CConsole__Printf(&DAT_0066f580,s_ERROR__Could_not_play_sample___s_006322f0);
    return;
  }
  iVar1 = CSoundManager__GetOrCreateSample(param_1,param_2,0,'\0');
  if (iVar1 != 0) {
    CSoundManager__Unk_004e0b30();
    return;
  }
  CConsole__Printf(&DAT_0066f580,s_ERROR__PlayNamedSample_failed_to_006322b8);
  return;
}

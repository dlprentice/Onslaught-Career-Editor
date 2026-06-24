/* address: 0x004655d0 */
/* name: con_fmv_play */
/* signature: void __cdecl con_fmv_play(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl con_fmv_play(void *param_1)

{
  char cVar1;
  uint uVar2;
  char *pcVar3;

  uVar2 = 0xffffffff;
  pcVar3 = param_1;
  do {
    if (uVar2 == 0) break;
    uVar2 = uVar2 - 1;
    cVar1 = *pcVar3;
    pcVar3 = pcVar3 + 1;
  } while (cVar1 != '\0');
  if (9 < ~uVar2 - 1) {
    _DAT_0089d69c = (uint)(DAT_006630cc != 0);
    CFrontEnd__Helper_0042d7d0(1);
    (**(code **)(DAT_0089d690 + 0x2c))((int)param_1 + 9,0,0,0,0,1);
    CFrontEnd__Helper_0042d7d0(0);
    return;
  }
  CConsole__AddString(&DAT_00663498,s_Syntax___fmv_play_<filename>_00629abc);
  return;
}

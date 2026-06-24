/* address: 0x0040dce0 */
/* name: CBattleEngine__HostileEnvironment */
/* signature: void __fastcall CBattleEngine__HostileEnvironment(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CBattleEngine__HostileEnvironment(int param_1)

{
  void *pvVar1;
  int unaff_ESI;
  char local_100 [256];

  if (_DAT_005d85d8 < DAT_00672fd0 - *(float *)(param_1 + 0x510)) {
    sprintf(local_100,s_hud__s_00623314);
    pvVar1 = (void *)CBattleEngine__Helper_004e1910(&DAT_00896988,(int)local_100,0,unaff_ESI);
    CMonitor__Helper_004e1940(&DAT_00896988,pvVar1,(void *)param_1);
    CConsole__Printf(&DAT_0066f580,s_playing_sample___hostile_environ_00623500);
    *(float *)(param_1 + 0x510) = DAT_00672fd0;
    return;
  }
  *(float *)(param_1 + 0x510) = DAT_00672fd0;
  return;
}

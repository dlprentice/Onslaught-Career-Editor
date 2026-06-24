/* address: 0x0040d5f0 */
/* name: CBattleEngine__AttachHudSoundEventListener */
/* signature: void __fastcall CBattleEngine__AttachHudSoundEventListener(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CBattleEngine__AttachHudSoundEventListener(int param_1)

{
  void *pvVar1;
  int unaff_ESI;
  char local_100 [256];

  sprintf(local_100,s_hud__s_00623314);
  pvVar1 = (void *)CBattleEngine__FindSoundEventByNameIfEnabled
                             (&DAT_00896988,(int)local_100,0,unaff_ESI);
  CMonitor__Helper_004e1940(&DAT_00896988,pvVar1,(void *)param_1);
  return;
}
